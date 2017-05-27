from urllib.request import Request, urlopen
import re
import csv
import string
import random
import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool


def processIDs(eventIDs, threads):

        # Define the number of threads
        pool = ThreadPool(threads)

        # Calls get() and adds the filesize returned each call to an array called filesizes
        pool.map(getMatchIDs, eventIDs)
        pool.close()
        pool.join()



def getData(eventID):
    html = getHTML("https://www.hltv.org/results?offset=0&event=%s" % (eventID))
    # Find the type of event (online, LAN, etc)
    eventType = re.findall(' <div class=\".*text-ellipsis\">', html)
    if len(eventType) < 1:
        return True
    eventNames = re.findall('text-ellipsis\">.*<', html)
    eventEndDate = re.findall('class="standard-headline">.*<', html)

    # print eventType
    if len(eventType) > 0:
        eventType[0] = (eventType[0].replace(" <div class=\"", "")).replace(" text-ellipsis\">", "")
    else:
        eventType.append(0)

    # print eventNames
    if len(eventNames) > 0:
        eventNames[0] = (eventNames[0].replace("text-ellipsis\">", "")).replace("<", "")
    else:
        eventNames.append(0)

    # print eventEndDate
    if len(eventEndDate) > 0:
        eventEndDate[0] = (eventEndDate[0].replace("class=\"standard-headline\">", "")).replace("<", "")
    else:
        eventEndDate.append(0)
    print("%s,%s,%s,%s" % (eventType[0], eventNames[0], eventEndDate[0], eventID))
    return "%s,%s,%s,%s" % (eventType[0], eventNames[0], eventEndDate[0], eventID)


def getHTML(url):
    # Open the URL
    # Spoof the user agent
    request = Request(url)
    request.add_header('User-Agent', 'Mozilla/5.0')
    # Read the response as HTML
    html = urlopen(request).read().decode('utf-8')
    return html


eventIDs = []
with open('eventData.csv', encoding='utf-8') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        eventIDs.append(row[3])
    print(eventIDs)


eventIDs = list(range(1,7948))
# print(eventIDs)
threads = multiprocessing.cpu_count()
processIDs(eventIDs, threads)
