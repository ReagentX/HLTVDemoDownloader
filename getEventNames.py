import urllib2
import re
import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool


def processIDs(eventIDs, threads):

        # Define the number of threads
        pool = ThreadPool(threads)

        # Calls get() and adds the filesize returned each call to an array called filesizes
        pool.map(getData, eventIDs)
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
    print "%s,%s,%s,%s" % (eventType[0], eventNames[0], eventEndDate[0], eventID)
    return "%s,%s,%s,%s" % (eventType[0], eventNames[0], eventEndDate[0], eventID)


def getHTML(url):
    # Open the URL
    opener = urllib2.build_opener()

    # Spoof the user agent
    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
    response = opener.open(url)

    # Read the response as HTML
    html = response.read()
    return html


eventIDs = list(xrange(2900))
threads = multiprocessing.cpu_count()
processIDs(eventIDs, threads)
