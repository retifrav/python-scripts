import sys
import requests

if len(sys.argv) < 2:
    print("No URL specified")
    raise SystemExit

if len(sys.argv) > 2:
    print("Too many arguments")
    raise SystemExit

urlToShorten = sys.argv[1]

tinyURLendpoint = "https://tinyurl.com/api-create.php?url="

req = requests.get(tinyURLendpoint + urlToShorten)
rez = req.content.decode("utf-8")

if (req.status_code == 200):
    print(rez, end='')
    sys.exit(0)
else:
    sys.stderr.write("Error: " + str(req.status_code) + ", " + rez)
    sys.exit(1)
