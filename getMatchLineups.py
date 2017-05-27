from urllib.request import Request, urlopen
import re
import csv
from datetime import datetime
import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool



def processIDs(eventIDs, threads):

        # Define the number of threads
        pool = ThreadPool(threads)

        # Calls get() and adds the filesize returned each call to an array called filesizes
        pool.map(getData, eventIDs)
        pool.close()
        pool.join()

def getData(matchID):
    # Set some vars for later
    html = getHTML("https://www.hltv.org/matches/%s" % (matchID))
    playerIDs = re.findall('<a href=\"/player/.*/', html)

    # Give up if no team names found
    if len(playerIDs) < 1:
        return True
    for i in range(0, len(playerIDs)):
        playerIDs[i] = (playerIDs[i].split("/"))[2].split("/")[0]
    # print(playerIDs)c
    # print(playerIDs[0:5] + playerIDs[10:15])

    # Handle printing
    if len(playerIDs) > 15:
        # print(matchID)
        print("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (playerIDs[0], playerIDs[1], playerIDs[2], playerIDs[3], playerIDs[4], playerIDs[5], playerIDs[6], playerIDs[7], playerIDs[8], playerIDs[9], matchID))
    return True


def findMatchIDsAtURL(url):
    # Get the HTML using getHTML()
    html = getHTML(url)

    # Create an array of all of the Demo URLs on the page
    matchIDs = re.findall('"(.*?000"><a href="/matches/.*?)"', html)

    # Loop through the messy array and removes the pesky parts
    for i in range(0, len(matchIDs)):
        matchIDs[i] = matchIDs[i].split('/', 2)[-1]
    return matchIDs


def getHTML(url):
    # Open the URL
    # Spoof the user agent
    request = Request(url)
    request.add_header('User-Agent', 'Mozilla/5.0')
    # Read the response as HTML
    html = urlopen(request).read().decode('ascii', 'ignore')
    return html


def chunks(list, chunks):
    # Yield successive chunks from list.
    for i in range(0, len(list), chunks):
        yield list[i:i + chunks]


eventIDs = []
with open('joinMatchEvent.csv', encoding='utf-8') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        eventIDs.append(row[0])

print(len(eventIDs))
removeIDs = []
with open('matchLineups.csv', encoding='utf-8') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        removeIDs.append(row[10])

for i in range(1, len(removeIDs)):
    if removeIDs[i] in eventIDs:
        eventIDs.remove((removeIDs[i]))

print(len(eventIDs))
# eventIDs = chunks(eventIDs, multiprocessing.cpu_count())
# eventIDs = ["2188359/cph-wolves-vs-northern-dreamhack-winter-2012-danish-qual"]
# print(eventIDs)
# threads = multiprocessing.cpu_count()
threads = 32
processIDs(eventIDs, threads)
