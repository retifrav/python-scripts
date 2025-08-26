import logging
from datetime import datetime
import argparse
from urllib.parse import urlparse
import sys
import requests
# from requests_toolbelt.utils import dump

loggingLevel: int = logging.INFO
loggingFormat: str = "[%(levelname)s] %(message)s"


def checkURL(urlCandidate: str) -> str:
    result = urlparse(urlCandidate)
    if all([result.scheme, result.netloc]):
        return urlCandidate
    else:
        raise argparse.ArgumentTypeError(
            f"[{urlCandidate}] is not a valid URL"
        )


argParser = argparse.ArgumentParser(
    prog="website-availability",
    description="".join((
        "-= %(prog)s =-\n\n",
        "Checks availability of a website. Mostly based on 200 HTTP ",
        "response status code.\n\n",
        f"Copyright (C) 2025-{datetime.now().year} ",
        "Declaration of VAR\n",
        "License: GPLv3"
    )),
    formatter_class=argparse.RawDescriptionHelpFormatter,
    allow_abbrev=False
)
argParser.add_argument(
    "websiteURL",
    type=checkURL,
    metavar="https://example.org/",
    help="website URL"
)
argParser.add_argument(
    "--allow-redirects",
    action='store_true',
    help="automatically redirect in case of 301 (default: %(default)s)"
)
argParser.add_argument(
    "--use-get",
    action='store_true',
    help="use GET instead of HEAD (default: %(default)s)"
)
argParser.add_argument(
    "--debug",
    action='store_true',
    help="enable debug/dev mode (default: %(default)s)"
)
cliArgs = argParser.parse_args()

websiteURL: str = cliArgs.websiteURL
allowRedirects: bool = cliArgs.allow_redirects
useGet: bool = cliArgs.use_get
debugMode: bool = cliArgs.debug

if debugMode:
    loggingLevel = logging.DEBUG
    # 8 is the length of "CRITICAL" - the longest log level name
    loggingFormat = "%(asctime)s | %(levelname)-8s | %(message)s"

logging.basicConfig(
    format=loggingFormat,
    level=loggingLevel,
    stream=sys.stdout
)

logging.debug(f"CLI arguments: {cliArgs}")
logging.debug("-")

# ---

try:
    r = (
        requests.get(websiteURL, allow_redirects=allowRedirects)
        if useGet else
        requests.head(websiteURL, allow_redirects=allowRedirects)
    )
    # logging.debug(f"Raw headers:\n{dump.dump_all(r).decode()}")
    if r.status_code == 200:
        raise SystemExit(0)
    else:
        logging.error(f"HTTP response status code: {r.status_code}")
        raise SystemExit(1)
except requests.exceptions.ConnectionError:
    logging.error("Host unreachable or a DNS issue")
    raise SystemExit(14)
except requests.exceptions.Timeout:
    logging.error("Request timeout")
    raise SystemExit(13)
except requests.exceptions.RequestException as ex:
    logging.error(f"Unexpected error: {ex}")
    raise SystemExit(12)
except Exception as ex:
    logging.error(f"An even more unexpected error: {ex}")
    raise SystemExit(11)
