from urllib.request import Request, urlopen
import re
import csv
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
    html = getHTML("https://www.hltv.org/matches/%s" % (matchID))
    # Find the type of event (online, LAN, etc)
    eventName = re.findall('\"/events/.*/', html)
    if len(eventName) < 1:
        # print("Failed %s" % (matchID))
        return True

    # print eventType
    if len(eventName) > 1:
        eventName[0] = (eventName[0].replace("\"/events/", "")).split("/", 1)[0]
    else:
        eventName.append(0)

    print("%s,%s" % (matchID, eventName[0]))
    return "%s,%s" % (matchID, eventName[0])


def getHTML(url):
    # Open the URL
    # Spoof the user agent
    request = Request(url)
    request.add_header('User-Agent', 'Mozilla/5.0')
    # Read the response as HTML
    html = urlopen(request).read().decode('ascii', 'ignore')
    return html


matchIDs = []
with open('matchIDs.csv', encoding='utf-8') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        matchIDs.append(row[0])

removeIDs = []
with open('joinMatchEvent.csv', encoding='utf-8') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        removeIDs.append(row[0])


print(len(matchIDs))
for i in range(1, len(removeIDs)):
    if removeIDs[i] in matchIDs:
        matchIDs.remove(removeIDs[i])
print(len(matchIDs))


# threads = multiprocessing.cpu_count()
threads = 32
processIDs(matchIDs, threads)
