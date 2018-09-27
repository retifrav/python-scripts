import os
import sys
from glob import glob
from mutagen.easyid3 import EasyID3

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

path = os.path.join(sys.argv[1], "*.mp3")

for filename in glob(path):
    mp3file = EasyID3(filename)
    mp3file["tracknumber"] = ""
    mp3file.save()
    print(mp3file.items())
