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


def getData(playerID):
    html = getHTML("https://www.hltv.org/player/%s/a" % (playerID))
    # Find the type of event (online, LAN, etc)
    playerName = re.findall('Complete statistics for.*</a>', html)
    if len(playerName) < 1:
        return True
    playerCountry = re.findall('class=\"flag\" title=\".*\"> ', html)
    if len(playerCountry) < 1:
        return True

    # print teamName
    if len(playerName) > 0:
        playerName[0] = (playerName[0].replace("Complete statistics for", "")).replace("</a>", "")
    else:
        playerName.append(0)

    # print teamCountry
    if len(playerCountry) > 0:
        playerCountry[0] = (playerCountry[0].replace("class=\"flag\" title=\"", "")).replace("\"> ", "")
    else:
        playerCountry.append(0)

    print("%s,%s,%s" % (playerName[0], playerCountry[0], playerID))
    return "%s,%s,%s" % (playerName[0], playerCountry[0], playerID)


def getHTML(url):
    # Open the URL
    # Spoof the user agent
    request = Request(url)
    request.add_header('User-Agent', 'Mozilla/5.0')
    # Read the response as HTML
    html = urlopen(request).read().decode('ascii', 'ignore')
    return html


eventIDs = list(range(1, 14244))
threads = multiprocessing.cpu_count()
processIDs(eventIDs, threads)
