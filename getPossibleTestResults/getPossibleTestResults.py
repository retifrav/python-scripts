import requests
from random import randrange
from bs4 import BeautifulSoup
from time import sleep

numberOfRequests = 1000
testID = 23147
results = []

for x in range(numberOfRequests):
    print("[{0}/{1}] ...".format(x + 1, numberOfRequests))

    testResult = ""
    try:
        testResultsURL = "http://mindmix.ru/result?t={0}&1={1}&2={2}&3={3}&4={4}&5={5}&6={6}&7={7}&8={8}&9={9}&10={10}".format(
            testID,
            randrange(1, 4),
            randrange(1, 4),
            randrange(1, 3),
            randrange(1, 4),
            randrange(1, 5),
            randrange(1, 3),
            randrange(1, 3),
            randrange(1, 3),
            randrange(1, 4),
            randrange(1, 5)
            )
        #print(testResultsURL)
        testResultRequest = requests.get(testResultsURL)
        if testResultRequest.status_code != 200:
            print("[ERROR] Could not get test results. Error code: {0}".format(
                testResultRequest.status_code
                )
            )
            continue
        testResult = BeautifulSoup(testResultRequest.text, 'html.parser')
    except Exception as ex:
        print(ex)
        break

    #print(testResult.title.text)
    if testResult and testResult.title.text not in results:
        results.append(testResult.title.text)
    # don't overwhelm the server
    sleep(0.1)

#print(list(set(results)))
print(results)
