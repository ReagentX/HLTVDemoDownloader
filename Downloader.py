import urllib2
import urllib
import re
import os
import datetime
import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool


def getMatchIDs(eventid):
    # Create an offset variable for lists that are paginated on HLTV
    offset = 0
    # Build the URL

    # Create an array of all of the Demo URLs on the page
    matchIDs = findMatchIDsAtURL("https://www.hltv.org/results?offset=%s&event=%s" % (offset, eventid))

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
            moreMatchIDs = findMatchIDsAtURL("https://www.hltv.org/results?offset=%s&event=%s" % (offset, eventid))
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


def convertToDemoIDs(matchIDs, threads):
    # Tell the user what is happening
    print "Converting Match IDs to Demo IDs"

    # Define the number of threads
    pool = ThreadPool(threads)

    # Calls getDemoIDs() and adds the value returned each call to an array called demoIDs
    demoIDs = pool.map(getDemoIDs, matchIDs)

    # Create an array to add any captured errors to
    errors = []

    # Find any errors, add them to the errors array, and remove them from demoIDs
    for text in demoIDs:
        if " " in text:
            errors.append(text[1:])
            demoIDs.remove(text)

    # Print the errors (if there are any)
    printErrors(errors)
    return demoIDs


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
            print "Converted %s" % (matchID)
            # Return the Demo ID
            return demoID[0]

    # If there is no element, print which match has no demo
    elif len(demoID) < 1:
        print "No demo found for %s" % (matchID)
        # Return the Match ID with a space char so we can find it later
        return " %s" % matchID


def download(demoIDs, threads):
    # Convert the DemoIDs to URLs
    urls = convertToURLs(demoIDs)

    # Define the number of threads
    pool = ThreadPool(threads)

    # Make a folder for the event to save the files in
    directory = makeDir()

    # Calls get() and adds the filesize returned each call to an array called filesizes
    filesizes = pool.map(get, urls)
    pool.close()
    pool.join()

    # Create a float to store the filesizes in and add them together
    totalFileSize = 0.0
    for f in filesizes:
        totalFileSize = sum(filesizes)

    # Print the properly formatted filesize.
    print "Successfully transferred %s. Enjoy!" % (formatFilesize(totalFileSize))
    return True


def convertToURLs(demoIDs):
    return ["https://www.hltv.org/download/demo/%s" % demoID for demoID in demoIDs]


def get(url):
    # Build and open the URL
    opener = urllib2.build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
    response = opener.open(url)

    # HLTV redicrects to a .rar or .zip file
    finalurl = response.geturl()

    # Gets the filename (everything after the last trailing /)
    filename = finalurl.rsplit('/', 1)[-1]

    # Gets the Content-Length from the metadata from finalurl
    filesize = (int(urllib.urlopen(finalurl).info().getheaders("Content-Length")[0])/1024)/1024

    # Tell user we are downloading filesize
    print "Starting %s: %s MB." % (filename, filesize)

    # Downloads the file to the directory the user enters
    urllib.urlretrieve(finalurl, directory+"/"+filename)

    # Tell user the current status and file information
    print "Completed %s: %s MB." % (filename, filesize)
    return filesize


def makeDir():
    # Ask the user what the event name is
    # TODO eventName = raw_input("What is the event name? ")
    eventName = datetime.datetime.now().time()

    # Create a global variable so the different threads can access it
    global directory
    directory = "./%s" % (eventName)
    os.mkdir(directory)

    # Return the string so we can use it
    return directory


def formatFilesize(filesize):
    if filesize > 1024:
        return "%.2f GB" % (float(filesize) / 1024)
    else:
        return "%s MB" % (int(filesize))


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
    # Print URL(s) for the match(es) with no demo file(s)
    if len(errors) == 1:
        print "%s match has no demo:" % (len(errors))
        for i in range(0, len(errors)):
            print "%s: https://www.hltv.org/matches/%s" % (i+1, errors[i])
    elif len(errors) > 0:
        print "%s matches have no demo:" % (len(errors))
        for i in range(0, len(errors)):
            print "%s: https://www.hltv.org/matches/%s" % (i+1, errors[i])
    else:
        print "No errors found!"
    return True


# Calls the method for a given Event ID.
# TODO eventID = raw_input("What is the event ID? ")
eventID = 2334
threads = multiprocessing.cpu_count()
matchIDs = getMatchIDs(eventID)
# eventName = getData(eventID)
demoIDs = convertToDemoIDs(matchIDs, threads)
download(demoIDs, threads)
