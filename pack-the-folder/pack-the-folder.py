import pathlib
import shutil

currentWorkingDirectory = pathlib.Path().resolve()
cwdUP = currentWorkingDirectory.parents[0]
# print(currentWorkingDirectory, cwdUP)

# list the folder contents, just in case
# for p in pathlib.Path(currentWorkingDirectory).iterdir():
#     print(p)

archiveName = "folder"
shutil.make_archive(cwdUP / archiveName, "zip", currentWorkingDirectory)
shutil.move(
    cwdUP / f"{archiveName}.zip",
    currentWorkingDirectory / f"{archiveName}.zip"
)
