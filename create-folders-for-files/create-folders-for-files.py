import os
import sys
import pathlib
from glob import glob

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

# I am looking specifically for .md files
path = os.path.join(dir, "*.md")

for filename in glob(path):
    fname = pathlib.Path(filename).stem
    #print(fname)
    newdir = os.path.join(dir, fname)
    # create a new directory named after the file
    os.mkdir(newdir)
    # move the file into that directory while changing its name
    pathlib.Path(filename).rename(os.path.join(newdir, "index.md"))
