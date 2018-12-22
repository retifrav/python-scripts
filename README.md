## My Python scripts

- [ssh-known-hosts](#ssh-known-hosts)
- [mp3-idv3-tags](#mp3-idv3-tags)
- [generate-iconset](#generate-iconset)
- [oxps-to-pdf](#oxps-to-pdf)

### ssh-known-hosts

SSH config known hosts analysis.

### mp3-idv3-tags

Mass ID3v2 tags editing.

``` bash
python mp3-idv3-tags.py /path/to/folder/with/mp3files/
```

### generate-iconset

Generate `.icns` file for Mac OS application from `.png` picture.

``` bash
python generate-iconset.py /path/to/original/icon.png
```

Result (`icon.icns`) will be saved to `/path/to/original/`.

More information in the following [article](https://retifrav.github.io/blog/2018/10/09/macos-convert-png-to-icns/).

### oxps-to-pdf

Convert OXPS files into PDF. Requires `ghostscript`/`gxps` to be installed.

``` bash
python oxps-to-pdf.py /path/to/folder/with/oxps/files
```
