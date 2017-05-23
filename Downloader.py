import urllib2
import urllib
import re
import os


def getMatchIDs(eventid):
    # Create an offset variable for lists that are paginated on HLTV
    offset = 0
    # Build the URL
    url = 'https://www.hltv.org/results?offset=%s&event=%s' % (offset, eventid)

    # Create an array of all of the Demo URLs on the page
    matchIDs = findMatchIDsAtURL(url)

    # If the length is = 50, offset by 50 and loop again
    if len(matchIDs) == 50:
        print "Parsed first page. Found %s IDs" % (len(matchIDs))

        # Set a boolean to close the while loop and a page variable we can increment when paginating
        morePages = True
        page = 1

        # While check is true, offset by 50
        while morePages:
            offset += 50

            # Same URL building and parsing as above
            url = 'https://www.hltv.org/results?offset=%s&event=%s' % (offset, eventid)
            moreMatchIDs = findMatchIDsAtURL(url)
            for m in moreMatchIDs:
                matchIDs.append(m)

            # Determine if there are additional pages to be found, if not the while loop ends
            if len(moreMatchIDs) < 50:
                morePages = False
                page += 1
                print "Parsed page %s. Found %s IDs." % (page, len(matchIDs))
            else:
                # Prints the current page and the number of parsed IDs
                page += 1
                print "Parsed page %s. %s IDs found so far." % (page, len(matchIDs))

    elif len(matchIDs) < 50:
        print "Total demos: %s" % len(matchIDs)
    elif len(matchIDs) > 50:
        print "HLTV altered demo page layout :("
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


def getDemoIDs(matchIDs):
    # Tell the user what is happening
    print "Converting Match IDs to Demo IDs"

    # Define the array of Demo IDs
    demoIDs = []

    # Create an array for Match IDs with no Demo ID
    noDemos = []

    # Loops through the array of Match IDs and gets the respective Demo IDs
    for i in range(0, len(matchIDs)):
        # Same URL building and opening as above
        url = "https://www.hltv.org/matches/%s" % (matchIDs[i])
        html = getHTML(url)
        demoID = re.findall('"(/download/demo/.*?)"', html)

        # Check if re.findall()'s array is empty
        # If it has an element, add that Demo ID to the demoIDs array
        if len(demoID) > 0:
            demoIDs.append(demoID[0])

        # If there is no element, print which match has no demo
        elif len(demoID) < 1:
            print "No demo found for %s (%s)" % (len(matchIDs)-i, matchIDs[i].rsplit('/', 1)[-1])
            noDemos.append(matchIDs[i])

        print "%s remaining to convert." % (len(matchIDs)-i-1)

    # Loop through the demoIDs array and remove everything up to the last / to get the real Demo ID
    for i in range(0, len(demoIDs)):
        demoIDs[i] = demoIDs[i].rsplit('/', 1)[-1]

    # If there are errors, print them
    printErrors(noDemos)

    return demoIDs


def download(demoIDs):
    # Tell the user how many demo files will be downloaded
    print "%s demo files to retrieve." % (len(demoIDs))

    # Make a folder for the files to be stored in.
    eventName = raw_input("What is the event name? ")
    directory = "./%s" % (eventName)
    os.mkdir(directory)

    # Create a float to calculate the total data transferred
    totalFilesize = 0.0

    # Parse through the array of Demo IDs
    for i in range(0, len(demoIDs)):
        # Build and open the URL
        url = "https://www.hltv.org/download/demo/%s" % (demoIDs[i])
        opener = urllib2.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        response = opener.open(url)

        # HLTV redicrects to a .rar or .zip file
        finalurl = response.geturl()

        # Gets the filename (everything after the last trailing /)
        filename = finalurl.rsplit('/', 1)[-1]

        # Gets the Content-Length from the metadata from finalurl
        filesize = (int(urllib.urlopen(finalurl).info().getheaders("Content-Length")[0])/1024)/1024

        # Add the filesize to the total filesize
        totalFilesize += filesize

        # Downloads the file to the directory the user enters
        urllib.urlretrieve(finalurl, directory+"/"+filename)

        # Tell user the current status and file information
        print "%s demos remaining. Completed %s: %s MB." % (len(demoIDs)-i-1, filename, filesize)

    print "Total data transferred: %s. Enjoy!" % (formatFilesize(totalFileSize))
    return True


def formatFilesize(filesize):
    if filesize > 1024:
        return "%.2f GB" % (float(data) / 1024)
    else:
        return "%s MB" % (data)


def getHTML(url):
    # Open the URL
    opener = urllib2.build_opener()

    # Spoof the user agent
    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
    response = opener.open(url)

    # Read the response as HTML
    html = response.read()

    return html


def printErrors(errors):
    if len(errors) == 1:
        print "%s match has no demo:" % (len(errors))

        # Print URLs for the matches with no demo file
        for i in range(0, len(errors)):
            print "%s: https://www.hltv.org/matches/%s" % (i+1, errors[i])

    elif len(errors) > 0:
        print "%s matches have no demo:" % (len(errors))

        # Print URLs for the matches with no demo file
        for i in range(0, len(errors)):
            print "%s: https://www.hltv.org/matches/%s" % (i+1, errors[i])
    else:
        print "No errors found!"
    return True


# Calls the method for a given Event ID.
eventID = raw_input("What is the event ID? ")
matchIDs = getMatchIDs(eventID)
demoIDs = getDemoIDs(matchIDs)
download(demoIDs)
