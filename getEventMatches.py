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



def getMatchIDs(eventid):
    # Create an offset variable for lists that are paginated on HLTV
    offset = 0
    # Build the URL

    # Create an array of all of the Demo URLs on the page
    matchIDs = findMatchIDsAtURL("https://www.hltv.org/results?offset=%s&event=%s" % (offset, eventid))

    # If the length is = 50, offset by 50 and loop again
    if len(matchIDs) == 50:
        # print("Parsed first page. Found %s IDs" % (len(matchIDs)))

        # Set a boolean to close the while loop and a page variable we can increment when paginating
        morePages = True
        page = 1

        # While check is true, offset by 50
        while morePages:
            offset += 50

            # Same URL building and parsing as above
            moreMatchIDs = findMatchIDsAtURL("https://www.hltv.org/results?offset=%s&event=%s" % (offset, eventid))
            for m in moreMatchIDs:
                matchIDs.append(m)

            # Determine if there are additional pages to be found, if not the while loop ends
            if len(moreMatchIDs) < 50:
                morePages = False
                page += 1
                # print "Parsed page %s. Found %s IDs." % (page, len(matchIDs))
            else:
                # Prints the current page and the number of parsed IDs
                page += 1
                # print "Parsed page %s. %s IDs found so far." % (page, len(matchIDs))

    elif len(matchIDs) < 50:
        # print "Total demos: %s" % len(matchIDs)
        for i in matchIDs:
            print("%s,%s" % (i, eventid))
    elif len(matchIDs) > 50:
        print("")
    return matchIDs


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
    html = urlopen(request).read().decode('utf-8')
    return html


eventIDs = []
with open('eventData.csv', encoding='utf-8') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        eventIDs.append(row[3])
    print(eventIDs)

# eventIDs = list(range(2000,2500))
# print(eventIDs)
threads = multiprocessing.cpu_count()
processIDs(eventIDs, threads)
