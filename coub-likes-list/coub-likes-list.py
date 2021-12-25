import requests
import json

CoubSettings = {
    "likesEndpoint": "".join((
        "https://coub.com/api/v2/timeline/likes",
        "?all=true",
        "&order_by=date"
    )),
    "likesTotalPages": 1,
    "baseViewURL": "https://coub.com/view/",
    "aythenticationCookie": "remember_token=HERE-GOES-SOME-TOKEN; _coub_session_2=HERE-GOES-SESSION-TOKEN"
}

myCoubLikes = []

whereToSaveLikesList = "/tmp/my-coub-likes.txt"
whereToSaveLikesDetails = "/tmp/my-coub-likes-details.json"


def getLikesFromCoub(pageNumber):
    try:
        coubRequest = requests.get(
            f"{CoubSettings['likesEndpoint']}&page={pageNumber}",
            headers={"Cookie": CoubSettings["aythenticationCookie"]}
        )
        if coubRequest.status_code != 200:
            raise SystemExit(
                " ".join((
                    "Some error on sending request to Coub,",
                    f"returned status code: {coubRequest.status_code}"
                ))
            )
        return coubRequest.json()
    except Exception as ex:
        raise SystemExit(
            " ".join((
                "Sending request to Coub failed,",
                f"exception: {ex}"
            ))
        )


def extractInfoFromCoub(coubJSON):
    sourceURL = coubJSON.get("external_download")
    myCoubLikes.append(
        {
            "id": coubJSON["permalink"],
            "title": coubJSON["title"],
            "source": sourceURL.get("url") if sourceURL else ""
        }
    )


# get the first page
likesCurrentPage = getLikesFromCoub(1)

CoubSettings["likesTotalPages"] = likesCurrentPage["total_pages"]
print(f"Total pages: {CoubSettings['likesTotalPages']}")

# process the first page, since we already have it
print(f"- processing page #1...")
for likedCoub in likesCurrentPage['coubs']:
    extractInfoFromCoub(likedCoub)

# iterate through the rest of pages
for pageNumber in range(2, CoubSettings["likesTotalPages"] + 1):
    print(f"- processing page #{pageNumber}...")
    likesCurrentPage = getLikesFromCoub(pageNumber)
    for likedCoub in likesCurrentPage['coubs']:
        extractInfoFromCoub(likedCoub)

# save the final JSON just in case
#with open(whereToSaveLikesDetails, "w") as f:
#    json.dump(myCoubLikes, f, indent=4)

# do stuff with the extracted data
# for instance, make a list of links for CoubDownloader
with open(whereToSaveLikesList, "w") as f:
    for likedCoub in myCoubLikes:
        f.write(f"{CoubSettings['baseViewURL']}{likedCoub['id']}\n")

raise SystemExit(0)
