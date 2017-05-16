import urllib2
import urllib
import re
import os


def getIDs(eventID):
    # Get the variable passed as an argument so it can be used
    eventid = eventID
    # Create an offset varibale for lists that are paginated on HLTV
    offset = 0
    #  Build the URL
    url = 'http://www.hltv.org/?pageid=28&&eventid=%s&offset=%s' % (eventid, offset)
    # Open the URL
    opener = urllib2.build_opener()
    # Spoof the user agent
    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
    response = opener.open(url)
    # Read the response as HTML
    html = response.read()
    # Create an array of all of the Demo URLs on the page
    demoIDs = re.findall('"(.*?eventid=%s&offset=%d&amp;demoid=.*?)"' % (eventid, offset), html)
    # Loops trhrough the messy array and removes the pesky parts
    for i in range(0, len(demoIDs)):
        demoIDs[i] = demoIDs[i].replace('" href="?pageid=28&amp;&eventid=%s&offset=%s&amp;demoid=' % (eventid, offset), "")
    # If the length is = 25, offset by 25 and loop again
    if len(demoIDs) == 25:
        # Set a boolean to cloe the while loop and a page variable we can increment when paginating
        morePages = True
        page = 1
        # While check is true, offset by 25
        while morePages:
            offset += 25
            # Same URL building and parsing as above
            url = 'http://www.hltv.org/?pageid=28&&eventid=%s&offset=%s' % (eventid, offset)
            opener = urllib2.build_opener()
            opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
            response = opener.open(url)
            html = response.read()
            moreDemoIDs = re.findall('"(.*?eventid=%s&offset=%d&amp;demoid=.*?)"' % (eventid, offset), html)
            for i in range(0, len(moreDemoIDs)):
                moreDemoIDs[i] = moreDemoIDs[i].replace('" href="?pageid=28&amp;&eventid=%s&offset=%s&amp;demoid=' % (eventid, offset), "")
                # Appends the new IDs to the master list
                demoIDs.append(moreDemoIDs[i])
            # Determine if there are additional page to be found, if not the while loop ends
            if len(moreDemoIDs) < 25:
                morePages = False
                print "Parsing final page. Found %s IDs" % (len(demoIDs))
            else:
                # Prints the current page and the number of parsed IDs
                page += 1
                print "Parsing next page: %s. %s IDs so far." % (page, len(demoIDs))
    elif len(demoIDs) < 25:
        print "Total demos: %s" % len(demoIDs)
    elif len(demoIDs) > 25:
        print "HLTV altered demo page layout"
    return demoIDs


def download(demoIDs):
    # Get the variable passed as an argument so it can be used
    demoIDs = demoIDs
    # Create a counter varibale
    counter = 0
    # Make a folder for the files to be stored in.
    eventName = raw_input("What is the event name? ")
    directory = "./%s" % (eventName)
    os.mkdir(directory)
    # Parse through the array of Demo IDs
    for i in range(0, len(demoIDs)):
        # Buidld the URL, same as above
        url = "http://www.hltv.org/interfaces/download.php?demoid=%s" % (demoIDs[i])
        opener = urllib2.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        response = opener.open(url)
        # HLTV redicrects to a .rar or .zip file
        finalurl = response.geturl()
        # Gets the filename (everything after the last trailing /)
        filename = finalurl.rsplit('/', 1)[-1]
        # Downloads the file to the directory with the script
        urllib.urlretrieve(finalurl, directory+"/"+filename)
        counter += 1
        print "Downloaded %s demos" % (counter)
    return True


# Calls the method for a given Event ID.
eventID = raw_input("What is the even ID? ")
demoIDs = getIDs(eventID)
download(demoIDs)
