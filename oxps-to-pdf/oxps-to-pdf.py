import os
import sys
import pathlib
import subprocess
from glob import glob

# path to gxps if it's not in your PATH
gxpsPath = "/usr/local/Cellar/ghostscript/9.26/bin/gxps"

if len(sys.argv) < 2:
    print("No directory specified")
    raise SystemExit

if len(sys.argv) > 2:
    print("Too many arguments")
    raise SystemExit

dir = sys.argv[1]
if not (os.path.isdir(dir)):
    print("There is no such directory")
    raise SystemExit

oxpsFiles = os.path.join(dir, "*.oxps")

filesCount = 0
for oxpsFile in glob(oxpsFiles):
    fname = pathlib.Path(oxpsFile).stem
    ext = pathlib.Path(oxpsFile).suffix
    subprocess.call([gxpsPath, "-sDEVICE=pdfwrite", f"-sOutputFile={os.path.join(dir, fname)}.pdf", "-dNOPAUSE", oxpsFile])
    filesCount += 1

print(f"Files processed: {filesCount}")
