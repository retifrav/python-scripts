import os
import sys
import pathlib
from datetime import datetime as dt

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

path = pathlib.Path(dir)
scriptContent = []

with open("script.sql", "a") as script:
    for entry in path.iterdir():
        if (entry.is_dir()):
            try:
                toolsDT = dt.utcfromtimestamp(
                    os.path.getmtime(pathlib.Path.joinpath(entry, "Tools"))
                    ).strftime("%Y-%m-%d %H:%M:%S")
                script.write(
                    "insert into revisions("
                    "dt_published,release_id,revision,content_id) "
                    "values('{}',1,'{}',3);\n".format(toolsDT, entry.name)
                    )
            except Exception as ex:
                print(ex)
