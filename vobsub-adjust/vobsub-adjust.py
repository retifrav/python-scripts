"""
Scale and move VobSub (DVD) subtitle bitmaps, no OCR.

Reads a .idx/.sub pair, redraws every subtitle bitmap at a new size and/or
position on the same canvas, and writes a new .idx/.sub pair. Timing,
colours, forced flags and the .idx header (size:, palette:, ...) are kept.
"""

import argparse
import bisect
import re
import struct
import sys
from pathlib import Path

import numpy as np

PACK_SIZE = 2048


class SpuError(Exception):
    """A subtitle this script can't safely rewrite; it is copied unchanged."""


# --- .idx file

TS_RE = re.compile(r"^(\s*timestamp\s*:\s*[-\d:]+\s*,\s*filepos\s*:\s*)([0-9A-Fa-f]+)")


def read_idx(path):
    text = Path(path).read_bytes().decode("latin-1")
    lines = text.splitlines(keepends=True)
    size = palette = None
    for line in lines:
        s = line.strip()
        if size is None:
            m = re.match(r"size\s*:\s*(\d+)\s*x\s*(\d+)", s, re.I)
            if m:
                size = (int(m.group(1)), int(m.group(2)))
        if palette is None:
            m = re.match(r"palette\s*:\s*(.+)", s, re.I)
            if m:
                vals = [v.strip() for v in m.group(1).split(",") if v.strip()]
                palette = [int(v, 16) for v in vals[:16]]
    return lines, size, palette


# --- .sub file (MPEG-2 program stream carrying DVD subpicture units)

def read_timestamp(b):
    return (((b[0] >> 1) & 7) << 30) | (b[1] << 22) | ((b[2] >> 1) << 15) \
        | (b[3] << 7) | (b[4] >> 1)


def write_timestamp(prefix, t):
    return bytes([prefix | ((t >> 29) & 0x0E) | 1, (t >> 22) & 0xFF,
                  ((t >> 14) & 0xFE) | 1, (t >> 7) & 0xFF, ((t << 1) & 0xFE) | 1])


def read_sub(data):
    """Split a .sub file into subpicture units, each with the file offset of
    the pack it starts in (that is what .idx filepos values point to)."""
    spus, open_spus = [], {}
    pos, n, pack_start, broken = 0, len(data), 0, 0

    while pos + 4 <= n:
        if data[pos] or data[pos + 1] or data[pos + 2] != 1:
            pos += 1
            continue
        code = data[pos + 3]
        if code == 0xBA:                                   # pack header
            pack_start = pos
            if pos + 14 <= n and data[pos + 4] & 0xC0 == 0x40:
                pos += 14 + (data[pos + 13] & 7)           # MPEG-2
            else:
                pos += 12                                  # MPEG-1
            continue
        if code < 0xBB or pos + 6 > n:                     # end code etc.
            pos += 4
            continue
        end = pos + 6 + struct.unpack_from(">H", data, pos + 4)[0]
        if code == 0xBD and end <= n:                      # private stream 1
            p, pts = pos + 6, None
            if data[p] & 0xC0 == 0x80:                     # MPEG-2 PES header
                if data[p + 1] & 0x80:
                    pts = read_timestamp(data[p + 3:p + 8])
                p += 3 + data[p + 2]
            else:                                          # MPEG-1 PES header
                while p < end and data[p] == 0xFF:
                    p += 1
                if p < end and data[p] & 0xC0 == 0x40:
                    p += 2
                if p < end and data[p] & 0xE0 == 0x20:
                    pts = read_timestamp(data[p:p + 5])
                    p += 10 if data[p] & 0x10 else 5
                else:
                    p += 1
            if p < end and 0x20 <= data[p] <= 0x3F:
                sid = data[p]
                cur = open_spus.get(sid)
                if cur is not None and pts is not None:    # new one began early
                    broken += 1
                    spus.append(open_spus.pop(sid))
                    cur = None
                if cur is None:
                    cur = open_spus[sid] = {"filepos": pack_start, "pts": pts,
                                            "sid": sid, "data": bytearray()}
                cur["data"] += data[p + 1:end]
                d = cur["data"]
                if len(d) >= 2 and len(d) >= ((d[0] << 8) | d[1]):
                    del d[(d[0] << 8) | d[1]:]
                    spus.append(open_spus.pop(sid))
        pos = end

    broken += len(open_spus)
    spus.extend(open_spus.values())
    spus.sort(key=lambda s: s["filepos"])
    return spus, broken


def pack_header(scr):
    scr &= (1 << 33) - 1
    return bytes([
        0x00, 0x00, 0x01, 0xBA,
        0x44 | ((scr >> 27) & 0x38) | ((scr >> 28) & 0x03),
        (scr >> 20) & 0xFF,
        0x04 | ((scr >> 12) & 0xF8) | ((scr >> 13) & 0x03),
        (scr >> 5) & 0xFF,
        0x04 | ((scr << 3) & 0xF8),
        0x01,
        0x01, 0x89, 0xC3,      # mux rate, the usual DVD value
        0xF8,                  # no pack stuffing
    ])


def write_spu(out, data, pts, sid):
    """Append one subpicture unit as 2048-byte packs; return its offset."""
    start, pos, first = len(out), 0, True
    while first or pos < len(data):
        opt = write_timestamp(0x20, pts) if first and pts is not None else b""
        room = PACK_SIZE - 14 - 6 - 3 - len(opt) - 1
        chunk = data[pos:pos + room]
        spare = room - len(chunk)
        stuffing = b"\xff" * spare if 0 < spare < 6 else b""
        pes = bytes([0x81, 0x80 if opt else 0x00, len(opt) + len(stuffing)]) \
            + opt + stuffing + bytes([sid]) + chunk
        out += pack_header(pts or 0) + b"\x00\x00\x01\xbd" \
            + struct.pack(">H", len(pes)) + pes
        if spare >= 6:
            out += b"\x00\x00\x01\xbe" + struct.pack(">H", spare - 6) \
                + b"\xff" * (spare - 6)
        pos += len(chunk)
        first = False
    return start


# --- subpicture units: control sequences and 2-bit RLE bitmaps

ARG_LEN = {0x00: 0, 0x01: 0, 0x02: 0, 0x03: 2, 0x04: 2, 0x05: 6, 0x06: 4}


def parse_spu(spu):
    if len(spu) < 4:
        raise SpuError("too short")
    ctrl = struct.unpack_from(">H", spu, 2)[0]
    seqs, off, seen = [], ctrl, set()
    while True:
        if off in seen or off + 4 > len(spu):
            raise SpuError("broken control sequence")
        seen.add(off)
        delay, nxt = struct.unpack_from(">HH", spu, off)
        p, cmds = off + 4, []
        while True:
            if p >= len(spu):
                raise SpuError("truncated control sequence")
            c = spu[p]
            p += 1
            if c == 0xFF:
                break
            if c == 0x07:                                  # CHG_COLCON
                if p + 2 > len(spu):
                    raise SpuError("truncated control sequence")
                n = struct.unpack_from(">H", spu, p)[0]
            elif c in ARG_LEN:
                n = ARG_LEN[c]
            else:
                raise SpuError(f"unknown command 0x{c:02x}")
            if p + n > len(spu):
                raise SpuError("truncated control sequence")
            cmds.append((c, bytes(spu[p:p + n])))
            p += n
        seqs.append((delay, cmds))
        if nxt <= off or nxt + 4 > len(spu):
            break
        off = nxt
    return seqs


def one_value(seqs, cmd):
    vals = {arg for _, cmds in seqs for c, arg in cmds if c == cmd}
    if len(vals) > 1:
        raise SpuError("bitmap changes during display")
    return vals.pop() if vals else None


def nibbles_to_list(arg):
    """SET_COLOR / SET_CONTR argument -> values for pixel codes 0..3."""
    return [arg[1] & 15, arg[1] >> 4, arg[0] & 15, arg[0] >> 4]


def decode_bitmap(spu, w, h, top, bottom):
    img = np.zeros((h, w), np.uint8)
    end = len(spu) * 2

    for field, start in ((0, top), (1, bottom)):
        pos = start * 2
        for y in range(field, h, 2):
            row, x = img[y], 0
            while x < w and pos < end:
                v = (spu[pos >> 1] >> (0 if pos & 1 else 4)) & 15
                pos += 1
                for limit in (0x4, 0x10, 0x40):
                    if v >= limit or pos >= end:
                        break
                    v = (v << 4) | ((spu[pos >> 1] >> (0 if pos & 1 else 4)) & 15)
                    pos += 1
                run, colour = v >> 2, v & 3
                if run == 0 or x + run > w:
                    run = w - x
                if colour:
                    row[x:x + run] = colour
                x += run
            pos += pos & 1                                 # lines are byte aligned
    return img


def encode_field(img, field):
    nibs = []
    h, w = img.shape
    for y in range(field, h, 2):
        row = img[y]
        cuts = (np.flatnonzero(row[1:] != row[:-1]) + 1).tolist()
        starts = [0] + cuts
        ends = cuts + [w]
        for k, (s, e) in enumerate(zip(starts, ends)):
            c = int(row[s])
            if k == len(starts) - 1:
                nibs += (0, 0, 0, c)                       # fill to end of line
                break
            left = e - s
            while left:
                r = min(left, 255)
                v = (r << 2) | c
                if r < 4:
                    nibs.append(v)
                elif r < 16:
                    nibs += (v >> 4, v & 15)
                elif r < 64:
                    nibs += (0, v >> 4, v & 15)
                else:
                    nibs += (0, v >> 8, (v >> 4) & 15, v & 15)
                left -= r
        if len(nibs) & 1:
            nibs.append(0)
    a = np.array(nibs, np.uint8).reshape(-1, 2)
    return ((a[:, 0] << 4) | a[:, 1]).astype(np.uint8).tobytes()


def darea_bytes(x1, x2, y1, y2):
    return bytes([x1 >> 4, ((x1 & 15) << 4) | (x2 >> 8), x2 & 255,
                  y1 >> 4, ((y1 & 15) << 4) | (y2 >> 8), y2 & 255])


def build_spu(img, x1, y1, seqs):
    """Encode img at (x1, y1) and rebuild the control sequences around it."""
    h, w = img.shape
    top, bottom = encode_field(img, 0), encode_field(img, 1)
    ctrl = 4 + len(top) + len(bottom)
    area = darea_bytes(x1, x1 + w - 1, y1, y1 + h - 1)
    offsets = struct.pack(">HH", 4, 4 + len(top))

    bodies = []
    for delay, cmds in seqs:
        body = b"".join(bytes([c]) + (area if c == 0x05 else offsets if c == 0x06 else arg)
                        for c, arg in cmds)
        bodies.append((delay, body + b"\xff"))
    starts, o = [], ctrl
    for _, body in bodies:
        starts.append(o)
        o += 4 + len(body)
    if o > 0xFFFF:
        raise SpuError("redrawn subtitle too large")

    out = bytearray(struct.pack(">HH", o, ctrl)) + top + bottom
    for i, (delay, body) in enumerate(bodies):
        nxt = starts[i + 1] if i + 1 < len(starts) else starts[i]
        out += struct.pack(">HH", delay, nxt) + body
    return bytes(out)


# --- resampling a 4-colour bitmap

def _box(x):
    return ((x > -0.5) & (x <= 0.5)).astype(float)


def _triangle(x):
    return np.maximum(0.0, 1.0 - np.abs(x))


def _lanczos(x):
    return np.where(np.abs(x) < 3, np.sinc(x) * np.sinc(x / 3), 0.0)


KERNELS = {"box": (_box, 0.5), "bilinear": (_triangle, 1.0), "lanczos": (_lanczos, 3.0)}


def weights(n_in, n_out, kernel):
    k, support = KERNELS[kernel]
    scale = n_in / n_out
    fs = max(scale, 1.0)
    sup = support * fs
    W = np.zeros((n_out, n_in))
    for i in range(n_out):
        c = (i + 0.5) * scale
        lo = max(int(np.floor(c - sup)), 0)
        hi = min(int(np.ceil(c + sup)), n_in)
        wv = k((np.arange(lo, hi) + 0.5 - c) / fs)
        s = wv.sum()
        if s > 0:
            W[i, lo:hi] = wv / s
        else:
            W[i, min(int(c), n_in - 1)] = 1.0
    return W


def resample(img, rgba, nw, nh, kernel):
    h, w = img.shape
    if kernel == "nearest":
        ys = np.minimum(((np.arange(nh) + 0.5) * h / nh).astype(int), h - 1)
        xs = np.minimum(((np.arange(nw) + 0.5) * w / nw).astype(int), w - 1)
        return img[np.ix_(ys, xs)]

    # Resample in premultiplied RGBA, then map every pixel back to the
    # nearest of the colours the subtitle actually uses.
    pm = np.concatenate([rgba[:, :3] * rgba[:, 3:4], rgba[:, 3:4]], axis=1)
    src = pm[img]
    if nh != h:
        src = np.tensordot(weights(h, nh, kernel), src, axes=(1, 0))
    if nw != w:
        src = np.tensordot(src, weights(w, nw, kernel), axes=(1, 1)).transpose(0, 2, 1)
    np.clip(src, 0.0, 1.0, out=src)

    vals, counts = np.unique(img, return_counts=True)
    used = vals[np.argsort(-counts, kind="stable")]
    d = ((src[:, :, None, :] - pm[used][None, None]) ** 2).sum(-1)
    return used[d.argmin(-1)].astype(np.uint8)


# --- adjusting one subtitle

def adjust_spu(spu, palette, canvas, opt):
    """Return (new_spu_bytes, before_box, after_box, clamped).
    Boxes are (x1, y1, x2, y2) of the visible pixels, end-exclusive."""
    seqs = parse_spu(spu)
    if any(c == 0x07 for _, cmds in seqs for c, _ in cmds):
        raise SpuError("uses per-line colour changes")
    area, dspxa = one_value(seqs, 0x05), one_value(seqs, 0x06)
    if area is None or dspxa is None:
        raise SpuError("no bitmap")
    colour, contrast = one_value(seqs, 0x03), one_value(seqs, 0x04)

    x1 = (area[0] << 4) | (area[1] >> 4)
    x2 = ((area[1] & 15) << 8) | area[2]
    y1 = (area[3] << 4) | (area[4] >> 4)
    y2 = ((area[4] & 15) << 8) | area[5]
    w, h = x2 - x1 + 1, y2 - y1 + 1
    if w <= 0 or h <= 0:
        raise SpuError("empty display area")
    top, bottom = struct.unpack(">HH", dspxa)
    img = decode_bitmap(spu, w, h, top, bottom)

    cmap = nibbles_to_list(colour) if colour else [0, 1, 2, 3]
    amap = nibbles_to_list(contrast) if contrast else [0, 15, 15, 15]
    rgba = np.array([[*palette[cmap[i]], amap[i] / 15.0] for i in range(4)])

    visible = (rgba[:, 3] > 0)[img]
    if not visible.any():
        raise SpuError("fully transparent")
    rows, cols = np.flatnonzero(visible.any(1)), np.flatnonzero(visible.any(0))
    r0, r1, c0, c1 = rows[0], rows[-1] + 1, cols[0], cols[-1] + 1
    crop = img[r0:r1, c0:c1]
    ch, cw = crop.shape
    before = (x1 + c0, y1 + r0, x1 + c1, y1 + r1)

    nw = max(1, round(cw * opt.scale_x))
    nh = max(1, round(ch * opt.scale_y))
    new = crop if (nw, nh) == (cw, ch) else resample(crop, rgba, nw, nh, opt.filter)

    # Horizontal scaling is centred on the screen's centre line, vertical
    # scaling keeps the bottom edge in place, then the shift is applied.
    cx = canvas[0] / 2
    nx = round(cx + (before[0] + cw / 2 - cx) * opt.scale_x - nw / 2)
    ny = round(before[3] + opt.shift_canvas) - nh

    clamped = False
    if not opt.no_clamp:
        cx_, cy_ = min(max(nx, 0), max(canvas[0] - nw, 0)), min(max(ny, 0), max(canvas[1] - nh, 0))
        clamped = (cx_, cy_) != (nx, ny)
        nx, ny = cx_, cy_
    if nx < 0 or ny < 0:
        raise SpuError("would move off the top/left edge")
    after = (nx, ny, nx + nw, ny + nh)

    # Draw the result into the subtitle's original display area (grown if the
    # text now reaches outside it), not into a tight box around the text.
    # Some players ignore where the display area sits and just put the whole
    # bitmap at the bottom; for them the transparent rows under the text are
    # what sets its height on screen.
    clear = [c for c in np.argsort(-np.bincount(img.ravel(), minlength=4))
             if rgba[c, 3] == 0]
    if clear:
        ux1, uy1 = min(x1, nx), min(y1, ny)
        ux2, uy2 = max(x1 + w, nx + nw), max(y1 + h, ny + nh)
        if not opt.no_clamp:
            ux2, uy2 = min(ux2, max(canvas[0], nx + nw)), min(uy2, max(canvas[1], ny + nh))
        # Some players mishandle bitmaps with an odd number of rows.
        if (uy2 - uy1) % 2:
            if uy1 > 0:
                uy1 -= 1
            elif opt.no_clamp or uy2 < canvas[1]:
                uy2 += 1
        out = np.full((uy2 - uy1, ux2 - ux1), clear[0], np.uint8)
        out[ny - uy1:ny - uy1 + nh, nx - ux1:nx - ux1 + nw] = new
        new, nx, ny = out, ux1, uy1

    return build_spu(new, nx, ny, seqs), before, after, clamped, (y1, y1 + h)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Scale and move VobSub (.idx/.sub) subtitle bitmaps without OCR.",
        epilog="Horizontal scaling is centred on the middle of the screen, so centred "
               "subtitles stay centred. Vertical scaling keeps each subtitle's bottom "
               "edge in place. Subtitles that would leave the canvas are stopped at "
               "its edge.")
    ap.add_argument("input", help="input .idx (the .sub next to it is read too)")
    ap.add_argument("output", nargs="?", help="output .idx (a .sub is written next to it)")
    ap.add_argument("--scale-x", type=float, default=1.0, metavar="F",
                    help="width factor, e.g. 0.8 for 80%% of the current width")
    ap.add_argument("--scale-y", type=float, default=1.0, metavar="F",
                    help="height factor (default 1.0)")
    ap.add_argument("--shift-y", type=float, default=0.0, metavar="PX",
                    help="move down by PX (negative moves up); subtitle-canvas "
                         "pixels, or video pixels if --video-height is given")
    ap.add_argument("--video-height", type=int, metavar="H",
                    help="height of the video the subs are muxed into, e.g. 816")
    ap.add_argument("--filter", choices=["lanczos", "bilinear", "box", "nearest"],
                    default="bilinear", help="resampling filter (default: bilinear)")
    ap.add_argument("--no-clamp", action="store_true",
                    help="don't stop subtitles at the bottom/right edge of the canvas")
    ap.add_argument("--info", action="store_true",
                    help="only report where the subtitles sit; write nothing")
    opt = ap.parse_args(argv)

    if opt.scale_x <= 0 or opt.scale_y <= 0:
        ap.error("scale factors must be positive")
    if not opt.info and not opt.output:
        ap.error("an output .idx is required (or use --info)")

    in_idx = Path(opt.input)
    in_sub = in_idx.with_suffix(".sub")
    if not in_sub.exists():
        sys.exit(f"Can't find {in_sub} next to {in_idx}")

    lines, canvas, pal = read_idx(in_idx)
    if canvas is None:
        canvas = (720, 576)
        print("Note: the .idx has no 'size:' line, assuming 720x576. Add one, "
              "otherwise players will draw the subs at the wrong scale.")
    if not pal:
        print("Note: the .idx has no palette; colours are only used for resampling.")
        pal = [0x000000, 0xFFFFFF, 0x000000, 0x808080] * 4
    pal = (pal + [0x808080] * 16)[:16]
    palette = [((p >> 16) / 255, ((p >> 8) & 255) / 255, (p & 255) / 255) for p in pal]

    factor = canvas[1] / opt.video_height if opt.video_height else 1.0
    opt.shift_canvas = opt.shift_y * factor

    spus, broken = read_sub(in_sub.read_bytes())
    if not spus:
        sys.exit("No subtitles found in the .sub file.")

    out_sub, new_pos = bytearray(), {}
    befores, afters, areas, clamped, kept, reasons = [], [], [], 0, 0, {}
    for s in spus:
        data = bytes(s["data"])
        try:
            new, before, after, was_clamped, area = adjust_spu(data, palette, canvas, opt)
            befores.append(before)
            afters.append(after)
            areas.append(area)
            clamped += was_clamped
            if not opt.info:
                data = new
        except SpuError as e:
            kept += 1
            reasons[str(e)] = reasons.get(str(e), 0) + 1
        if not opt.info:
            new_pos[s["filepos"]] = write_spu(out_sub, data, s["pts"], s["sid"])

    def span(boxes):
        return min(b[1] for b in boxes), max(b[3] for b in boxes) - 1

    def px(v):
        """Canvas pixels, plus the video-pixel equivalent if known."""
        return f"{v} px" + (f" (about {v / factor:.0f} video px)" if opt.video_height else "")

    def median(vals):
        return sorted(vals)[len(vals) // 2]

    unit = "video" if opt.video_height else "canvas"
    print(f"Canvas {canvas[0]}x{canvas[1]}, {len(spus)} subtitles")
    if befores:
        top, bot = span(befores)
        rooms = [canvas[1] - b[3] for b in befores]
        print(f"  Text now sits in rows {top}-{bot}")
        print(f"  Room below the text: median {px(median(rooms))}, smallest {px(min(rooms))}")
        gaps = [a[1] - b[3] for a, b in zip(areas, befores)]
        if median(gaps) > 0:
            print(f"  Transparent space under the text inside its display area: "
                  f"median {px(median(gaps))}")
        widths = [b[2] - b[0] for b in befores]
        print(f"  Text width: median {median(widths)} px, widest {max(widths)} px")
    if kept:
        print(f"  Copied unchanged: {kept} ("
              + ", ".join(f"{n} {r}" for r, n in reasons.items()) + ")")
    if broken:
        print(f"  Warning: {broken} subtitle(s) in the .sub looked incomplete")
    if opt.info:
        return

    if afters:
        top, bot = span(afters)
        print(f"  After: text in rows {top}-{bot}")
    if clamped:
        limit = min(canvas[1] - b[3] for b in befores) / factor
        print(f"  WARNING: {clamped} of {len(befores)} subtitles would have gone below "
              f"the bottom of the canvas and were stopped at the edge, so a bigger "
              f"--shift-y won't move those any lower. To keep all of them clear of "
              f"the edge, use --shift-y {limit:.0f} or less ({unit} px).")

    # Rewrite filepos values in the .idx.
    old_starts = sorted(new_pos)
    out_lines, unmatched = [], 0
    for line in lines:
        m = TS_RE.match(line)
        if m:
            old = int(m.group(2), 16)
            i = bisect.bisect_left(old_starts, old)
            if i == len(old_starts):
                i = len(old_starts) - 1
            unmatched += old_starts[i] != old
            line = line[:m.start(2)] + f"{new_pos[old_starts[i]]:09x}" + line[m.end(2):]
        out_lines.append(line)
    if unmatched:
        print(f"  Warning: {unmatched} .idx entries didn't point exactly at a subtitle "
              "and were matched to the next one")

    out_idx = Path(opt.output).with_suffix(".idx")
    out_sub_path = out_idx.with_suffix(".sub")
    if out_idx.resolve() == in_idx.resolve() or out_sub_path.resolve() == in_sub.resolve():
        sys.exit("Output would overwrite the input; choose a different name.")
    out_sub_path.write_bytes(out_sub)
    out_idx.write_bytes("".join(out_lines).encode("latin-1"))
    print(f"Wrote {out_idx} and {out_sub_path}")


if __name__ == "__main__":
    main()
