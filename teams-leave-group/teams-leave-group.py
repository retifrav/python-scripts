import sys
import argparse
import requests
import webbrowser

notADrill: bool = False
# the tokens are short-lived (90 minutes?), so you'll have to open MICROSOFT_GRAPH_EXPLORER_URL
# every time and copy it from `Access token` tab
accessToken: str = ""

MICROSOFT_GRAPH_EXPLORER_URL = "https://developer.microsoft.com/en-us/graph/graph-explorer"
MICROSOFT_GRAPH_API_BASE_URL = "https://graph.microsoft.com/v1.0"
TEAM_ID = "HERE-GOES-THE-TEAM-ID"  # which team to leave


def memberOfTheTeam(session: requests.Session, team_id: str) -> bool:
    joinedTeamsURL = f"{MICROSOFT_GRAPH_API_BASE_URL}/me/joinedTeams"
    while joinedTeamsURL:
        joinedTeamsRez = session.get(joinedTeamsURL)
        joinedTeamsRez.raise_for_status()
        joinedTeams = joinedTeamsRez.json()
        for team in joinedTeams.get("value", []):
            if team.get("id") == team_id:
                return True
        joinedTeamsURL = joinedTeams.get("@odata.nextLink")  # if there is pagination
    return False


argParser = argparse.ArgumentParser(
    description="Leave a specific team/group via Microsoft Graph.",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    allow_abbrev=False
)
argParser.add_argument(
    "--token",
    required=True,
    help="Microsoft Graph API access token",
)
argParser.add_argument(
    "--not-a-drill",
    action='store_true',
    help=" ".join((
        "if this is set, then actually leave the team. Otherwise,",
        "just check if you are a member of it",
        "(default: %(default)s)"
    ))
)
cliArgs = argParser.parse_args()

notADrill = cliArgs.not_a_drill
accessToken =  cliArgs.token

session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {accessToken}",
    "Content-Type": "application/json",
})

try:
    userIDrez = session.get(f"{MICROSOFT_GRAPH_API_BASE_URL}/me?$select=id")
    userIDrez.raise_for_status()
    USER_ID: str = userIDrez.json()["id"]

    if not memberOfTheTeam(session, TEAM_ID):
        print(f"You are not a member of {TEAM_ID} team")
    else:
        print("Removing you from the team...")
        if notADrill:
            # but it is probably not allowed for regular users to leave a team via API,
            # so that will fail with `403 Client Error`
            url = f"{MICROSOFT_GRAPH_API_BASE_URL}/groups/{TEAM_ID}/members/{USER_ID}/$ref"
            removeFromTeamRez = session.delete(url)
            if removeFromTeamRez.status_code == 204:
                print(f"Successfully left the team {TEAM_ID}")
            else:
                removeFromTeamRez.raise_for_status()
        else:
            print("This is just a drill, not doing anything unless you provide `--not-a-drill`")
except requests.exceptions.HTTPError as ex:
    if ex.response is not None and ex.response.status_code == 401:
        print(
            " ".join((
                "Got 401 Unauthorized - the token is either invalid or expired,",
                f"go to {MICROSOFT_GRAPH_EXPLORER_URL} and get a new one"
            )),
            file=sys.stderr
        )
        webbrowser.open(MICROSOFT_GRAPH_EXPLORER_URL)
        raise SystemExit(1)
    raise
