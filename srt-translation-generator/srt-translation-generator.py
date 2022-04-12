from datetime import datetime
from typing import Tuple
import argparse
import pathlib
import re

__version_info__: Tuple[int, int, int] = (0, 1, 0)
__version__: str = ".".join(map(str, __version_info__))
__copyright__: str = " ".join((
    f"Copyright (C) 2022-{datetime.now().year}",
    "Declaration of VAR"
))

originalSrt: str = None
wrongFormatError: str = " ".join((
    "Original SRT file seems to have",
    "a wrong format, because"
))
regexSrtNumber = re.compile(r"^[1-9]{1}\d*$")
regexSrtTimeCode = re.compile(r"^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$")


def main() -> None:
    argParser = argparse.ArgumentParser(
        prog="srt-translation-generator",
        description=" ".join((
            f"%(prog)s\n{__copyright__}\nGenerates",
            "an empty SRT file for translation"
        )),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        allow_abbrev=False
    )
    argParser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    argParser.add_argument(
        "originalSrt",
        nargs="?",
        type=pathlib.Path,
        metavar="/path/to/some.srt",
        help="path to the original SRT file"
    )
    argParser.add_argument(
        "--lang",
        metavar="ru",
        default="ru",
        help=" ".join((
            "language suffix to append to the original file name",
            "(default: %(default)s)"
        ))
    )
    argParser.add_argument(
        "--srt-encoding",
        metavar="utf_8",
        default="utf_8",
        help="encoding of the original SRT file (default: %(default)s)"
    )
    cliArgs = argParser.parse_args()
    # print(cliArgs)

    if not cliArgs.originalSrt:
        raise SystemExit(
            " ".join((
                "[ERROR] You need to provide path to the",
                "original SRT file"
            ))
        )
    else:
        originalSrt = pathlib.Path(cliArgs.originalSrt)

    if not originalSrt.is_file():
        raise SystemExit(
            f"[ERROR] There is no such file: {originalSrt}"
        )
    # else:
    #     print(f"Got this file: {cliArgs.originalSrt}")

    if originalSrt.suffix != ".srt":
        raise SystemExit(
            f"[ERROR] The file extension is not .srt"
        )

    # print(f"Parent directory: {originalSrt.parents[0]}")

    generatedSrt = pathlib.Path(
        originalSrt.parents[0],
        f"{originalSrt.stem}-{cliArgs.lang}{originalSrt.suffix}"
    )

    with open(originalSrt,
              "r",
              encoding=cliArgs.srt_encoding
              ) as originalFile, \
         open(generatedSrt,
              "w",
              encoding="utf-8"
              ) as generatedFile:
        previousLineWasEmpty: bool = False
        previousLineWasTitleNumber: bool = False
        currentTitleNumber: int = 0
        try:
            for index, line in enumerate(originalFile):
                line: str = line.strip()
                # print(f"Line {index}: {line}")
                if not line:
                    if previousLineWasEmpty:
                        raise SystemExit(
                            " ".join((
                                f"[ERROR] {wrongFormatError} the line {index+1}",
                                "should not be empty"
                            ))
                        )
                    if previousLineWasTitleNumber:
                        raise SystemExit(
                            " ".join((
                                f"[ERROR] {wrongFormatError} after",
                                f"the title number on the line {index}",
                                "there should have been a time code",
                                f"on the line {index+1}"
                            ))
                        )
                    else:
                        generatedFile.write("\n")
                    previousLineWasEmpty = True
                else:
                    if (
                        (index == 0 or previousLineWasEmpty)
                        and regexSrtNumber.fullmatch(line) is not None
                    ):
                        currentTitleNumberCandidate = int(line)
                        if currentTitleNumberCandidate - currentTitleNumber != 1:
                            raise SystemExit(
                                " ".join((
                                    f"[ERROR] {wrongFormatError} the title number",
                                    f"on the line {index+1}",
                                    f"({currentTitleNumberCandidate}) is not",
                                    "a +1 increment of the previous",
                                    f"title number ({currentTitleNumber})"
                                ))
                            )
                        else:
                            generatedFile.write(f"{line}\n")
                            currentTitleNumber = currentTitleNumberCandidate
                        previousLineWasTitleNumber = True
                    else:
                        if previousLineWasTitleNumber:
                            if regexSrtTimeCode.fullmatch(line) is None:
                                raise SystemExit(
                                    " ".join((
                                        f"[ERROR] {wrongFormatError}",
                                        "after the title number",
                                        f"on the line {index} there should",
                                        "have been a time code",
                                        f"on the line {index+1}"
                                    ))
                                )
                            else:
                                generatedFile.write(f"{line}\n")
                        else:
                            generatedFile.write("\n")
                        previousLineWasTitleNumber = False
                    previousLineWasEmpty = False
        except UnicodeDecodeError as ex:
            raise SystemExit(
                " ".join((
                    "[ERROR] It looks like the original SRT file is not",
                    "in UTF-8 encoding. Try to provide a different one",
                    "with --srt-encoding, for example latin_1 or cp1251"
                ))
            )


if __name__ == "__main__":
    main()
