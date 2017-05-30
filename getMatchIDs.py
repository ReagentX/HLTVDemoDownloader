from urllib.request import Request, urlopen
import re
import csv
import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool


def getMatchIDs(eventid):
    # Create an offset variable for lists that are paginated on HLTV
    offset = 0
    # Build the URL

    # Create an array of all of the Demo URLs on the page
    matchIDs = findMatchIDsAtURL("https://www.hltv.org/results?offset=%s" % (offset))

    # If the length is = 50, offset by 50 and loop again
    if len(matchIDs) == 100:
        print("Parsed first page. Found %s IDs" % (len(matchIDs)))

        # Set a boolean to close the while loop and a page variable we can increment when paginating
        morePages = True
        page = 1

        # While check is true, offset by 50
        while morePages:
            offset += 100

            # Same URL building and parsing as above
            moreMatchIDs = findMatchIDsAtURL("https://www.hltv.org/results?offset=%s" % (offset))
            for m in moreMatchIDs:
                matchIDs.append(m)

            # Determine if there are additional pages to be found, if not the while loop ends
            if len(moreMatchIDs) < 100:
                morePages = False
                page += 1
                print("Parsed page %s. Found %s IDs." % (page, len(matchIDs)))
            else:
                # Prints the current page and the number of parsed IDs
                page += 1
                print("Parsed page %s. %s IDs found so far." % (page, len(matchIDs)))

    elif len(matchIDs) < 100:
        print("Total demos: %s" % len(matchIDs))
    elif len(matchIDs) > 100:
        print("HLTV altered demo page layout on offset %s" % (offset))
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


def getDemoIDs(matchID):
    # URL building and opening
    url = "https://www.hltv.org/matches/%s" % (matchID)
    html = getHTML(url)
    demoID = re.findall('"(/download/demo/.*?)"', html)

    # Check if re.findall()'s array is empty
    # If it has an element, add that Demo ID to the demoIDs array
    if len(demoID) > 0:
        # Loop through the demoIDs array and remove everything up to the last / to get the real Demo ID
        for i in range(0, len(demoID)):
            demoID[i] = demoID[i].rsplit('/', 1)[-1]
            print("Converted %s" % (matchID))
            # Return the Demo ID
            return demoID[0]

    # If there is no element, print which match has no demo
    elif len(demoID) < 1:
        print("No demo found for %s" % (matchID))
        # Return the Match ID with a space char so we can find it later
        return " %s" % matchID


def getHTML(url):
    # Open the URL
    # Spoof the user agent
    request = Request(url)
    request.add_header('User-Agent', 'Mozilla/5.0')
    # Read the response as HTML
    html = urlopen(request).read().decode('ascii', 'ignore')
    return html


# Calls the method for a given Event ID.
# TODO eventID = raw_input("What is the event ID? ")
eventID = 2334
threads = multiprocessing.cpu_count()
matchIDs = getMatchIDs(eventID)
for i in range(0, len(matchIDs)):
    print(matchIDs[i])
# eventName = getData(eventID)
# demoIDs = convertToDemoIDs(matchIDs, threads)
# download(demoIDs, threads)
