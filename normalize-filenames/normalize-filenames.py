from unidecode import unidecode
from datetime import datetime
from typing import Tuple
import argparse
import pathlib
import json
import sys
import re
import os

__version_info__: Tuple[int, int, int] = (0, 1, 0)
__version__: str = ".".join(map(str, __version_info__))
__copyright__: str = " ".join((
    f"Copyright (C) 2022-{datetime.now().year}",
    "Declaration of VAR"
))

timeNow: str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")

pathToFolder: pathlib.Path = pathlib.Path()
withDotFiles: bool = False
notADrill: bool = False
noLog: bool = False


def normalizeFilename(originalFilename: str) -> str:
    # make all letters small
    newFilename: str = originalFilename.lower()
    # replace whitespaces with dashes
    newFilename = re.sub(r"\s+", "-", newFilename)
    # replace underscores with dashes
    newFilename = re.sub("_", "-", newFilename)
    # transliterate to Latin
    newFilename = unidecode(newFilename)
    # remove non-alphanumeric and non-dash symbols
    newFilename = re.sub(r"[^a-zA-Z0-9\-]+", "", newFilename)
    # replace multiple dashes with a single dash
    newFilename = re.sub(r"\-+", "-", newFilename)
    # return resulting filename
    return newFilename


def main() -> None:
    argParser = argparse.ArgumentParser(
        prog="normalize-filenames",
        description=" ".join((
            f"%(prog)s\n{__copyright__}\n\nNormalizes",
            "the names of files (and files only) in a given",
            "folder:\n- replaces spaces with dashes\n- removes",
            "non-alphanumeric symbols\n- makes all letters small"
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
        "pathToFolder",
        nargs="?",
        type=pathlib.Path,
        metavar="/path/to/folder/",
        help="path to the folder with files"
    )
    argParser.add_argument(
        "--with-dot-files",
        action='store_true',
        help=" ".join((
            "also processes files starting with a dot, such as ",
            ".DS_Store, .gitignore and so on (default: %(default)s)"
        ))
    )
    argParser.add_argument(
        "--not-a-drill",
        action='store_true',
        help=" ".join((
            "if this is set, then do the actual renaming. Otherwise,",
            "just emulate normalizing and print new filenames",
            "(default: %(default)s)"
        ))
    )
    argParser.add_argument(
        "--no-log",
        action='store_true',
        help=" ".join((
            "do not create renamings log",
            "(default: %(default)s)"
        ))
    )

    cliArgs = argParser.parse_args()
    # print(cliArgs)

    if not cliArgs.pathToFolder:
        raise SystemExit(
            " ".join((
                "[ERROR] You need to provide path",
                "to the folder with files"
            ))
        )
    else:
        pathToFolder = pathlib.Path(cliArgs.pathToFolder)

    withDotFiles = cliArgs.with_dot_files
    notADrill = cliArgs.not_a_drill
    noLog = cliArgs.no_log

    if not pathToFolder.is_dir():
        raise SystemExit(
            f"[ERROR] There is no such folder: {pathToFolder}"
        )
    # else:
    #     print(f"Got this folder: {pathToFolder}")

    if notADrill:
        print(
            " ".join((
                f"THIS IS NOT A DRILL!\nAll the files in {pathToFolder} folder",
                "will be renamed.\nHopefully, you've made a backup."
            ))
        )
    else:
        print(
            " ".join((
                "[DRY RUN] Will emulate normalizing, print new filenames,",
                "but won't perform the actual renaming.\nTo do the renaming,",
                "pass the --not-a-drill flag.\nAnd perhaps make a backup copy",
                "of your folder first, as there is no rollback!"
            ))
        )


    filesCnt: int = 0
    renamings = []
    for p in pathToFolder.iterdir():
        currentItem = pathlib.Path(p)
        if p.is_file():
            if p.name.startswith(".") and not withDotFiles:
                continue
            print(f"\n- renaming: {p.name}")
            newFilename: str = f"{normalizeFilename(p.stem)}{p.suffix}"
            newFile: pathlib.Path = pathlib.Path(pathToFolder / newFilename)
            if not notADrill:
                print(f"[DRY RUN] New filename will be: {newFilename}")
            if (newFile.exists()):
                print(f"[WARNING] The file {newFilename} already exists")
                continue
            if notADrill:
                try:
                    p.rename(newFile)
                    renamings.append(
                        {
                            "id": filesCnt+1,
                            "original": p.name,
                            "renamed": newFile.name
                        }
                    )
                    print("OK")
                except Exception as ex:
                    print(
                        f"[ERROR] Couldn't rename {p.name}: {ex}",
                        file=sys.stderr
                )
            filesCnt += 1
    print()
    if notADrill:
        if not noLog:
            try:
                renamingsLog = {}
                renamingsLog["dateTime"] = timeNow
                renamingsLog["originalPath"] = pathToFolder.as_posix()
                renamingsLog["totalRenamings"] = filesCnt
                renamingsLog["renamings"] = renamings
                with open(f"./{timeNow}-renamings-log.json", "w") as logFile:
                    json.dump(renamingsLog, logFile, indent=4)
            except Exception as ex:
                print(f"[ERROR] Couldn't write to log: {ex}")
        finalMessage: str = f"---\nTotal files processed: {filesCnt}"
        print(finalMessage)
    else:
        print(
            " ".join((
                "---\n[DRY RUN] Total number of files",
                f"that would be processed: {filesCnt}"
            ))
        )


if __name__ == "__main__":
    main()
