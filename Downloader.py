from multiprocessing.dummy import Pool as ThreadPool
import urllib2
import urllib
import re
import os


def get_match_ids(eventid):
    # Create an offset variable for lists that are paginated on HLTV
    offset = 0
    # Build the URL

    # Create an array of all of the Demo URLs on the page
    match_ids = find_match_ids_at_url("https://www.hltv.org/results?offset=%s&event=%s" % (offset, eventid))

    # If the length is = 50, offset by 50 and loop again
    if len(match_ids) == 50:
        print "Parsed first page. Found %s IDs" % (len(match_ids))

        # Set a boolean to close the while loop and a page variable we can increment when paginating
        more_pages = True
        page = 1

        # While check is true, offset by 50
        while more_pages:
            offset += 50

            # Same URL building and parsing as above
            more_match_ids = find_match_ids_at_url("https://www.hltv.org/results?offset=%s&event=%s" % (offset, eventid))
            for match in more_match_ids:
                match_ids.append(match)

            # Determine if there are additional pages to be found, if not the while loop ends
            if len(more_match_ids) < 50:
                more_pages = False
                page += 1
                print "Parsed page %s. Found %s IDs." % (page, len(match_ids))
            else:
                # Prints the current page and the number of parsed IDs
                page += 1
                print "Parsed page %s. %s IDs found so far." % (page, len(match_ids))

    elif len(match_ids) < 50:
        print "Total demos: %s" % len(match_ids)
    elif len(match_ids) > 50:
        print "HLTV altered demo page layout :("
    return match_ids


def find_match_ids_at_url(url):
    # Get the HTML using get_html()
    html = get_html(url)

    # Create an array of all of the Demo URLs on the page
    match_ids = re.findall('<div class="result-con"><a href=\"/matches/(.*?)\"', html)

    return match_ids


def convert_to_demo_ids(match_ids, threads):
    # Tell the user what is happening
    print "Converting Match IDs to Demo IDs"

    # Define the number of threads
    pool = ThreadPool(threads)

    # Calls get_demo_ids() and adds the value returned each call to an array called demo_ids
    demo_ids = pool.map(get_demo_ids, match_ids)
    pool.close()
    pool.join()

    # Create an array to add any captured errors to
    errors = []

    # Find any errors, add them to the errors array, and remove them from demo_ids
    for text in demo_ids:
        if " " in text:
            errors.append(text[1:])
            demo_ids.remove(text)

    # Print the errors (if there are any)
    print_errors(errors)
    return demo_ids


def get_demo_ids(match_id):
    # URL building and opening
    url = "https://www.hltv.org/matches/%s" % (match_id)
    html = get_html(url)
    demo_id = re.findall('"(/download/demo/.*?)"', html)

    # Check if re.findall()'s array is empty
    # If it has an element, add that Demo ID to the demo_ids array
    if len(demo_id) > 0:
        # Loop through the demo_ids array and remove everything up to the last / to get the real Demo ID
        for i in range(0, len(demo_id)):
            demo_id[i] = demo_id[i].rsplit('/', 1)[-1]
            print "Converted %s" % (match_id)
            # Return the Demo ID
            return demo_id[0]

    # If there is no element, print which match has no demo
    elif len(demo_id) < 1:
        print "No demo found for %s" % (match_id)
        # Return the Match ID with a space char so we can find it later
        return " %s" % match_id


def download(demo_ids, threads):
    # Convert the DemoIDs to URLs
    urls = convert_to_urls(demo_ids)

    # Define the number of threads
    pool = ThreadPool(threads)

    # Make a folder for the event to save the files in
    directory = make_dir()

    # Calls get() and adds the filesize returned each call to an array called filesizes
    filesizes = pool.map(get, urls)
    pool.close()
    pool.join()

    # Create a float to store the filesizes in and add them together
    total_file_size = sum(filesizes)

    # Print the properly formatted filesize.
    print "Successfully transferred %s. Enjoy!" % (format_file_size(total_file_size))
    return True


def convert_to_urls(demo_ids):
    return ["https://www.hltv.org/download/demo/%s" % demo_id for demo_id in demo_ids]


def get(url):
    # Build and open the URL
    opener = urllib2.build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
    response = opener.open(url)

    # HLTV redicrects to a .rar or .zip file
    final_url = response.geturl()

    # Gets the filename (everything after the last trailing /)
    filename = final_url.rsplit('/', 1)[-1]

    # Gets the Content-Length from the metadata from final_url
    filesize = (int(urllib.urlopen(final_url).info().getheaders("Content-Length")[0])/1024)/1024

    # Tell user we are downloading filesize
    print "Starting %s: %s MB." % (filename, filesize)

    # Downloads the file to the directory the user enters
    urllib.urlretrieve(final_url, directory+"/"+filename)

    # Tell user the current status and file information
    print "Completed %s: %s MB." % (filename, filesize)
    return filesize


def make_dir():
    # Ask the user what the event name is
    event_name = raw_input("What is the event name? ")

    # Create a global variable so the different threads can access it
    global directory
    directory = "./%s" % (event_name)
    os.mkdir(directory)

    # Return the string so we can use it
    return directory


def format_file_size(filesize):
    if filesize > 1024:
        return "%.2f GB" % (float(filesize) / 1024)
    else:
        return "%s MB" % (int(filesize))


def get_html(url):
    # Open the URL
    opener = urllib2.build_opener()

    # Spoof the user agent
    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
    response = opener.open(url)

    # Read the response as HTML
    html = response.read()
    return html


def print_errors(errors):
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
event_id = raw_input("What is the event ID? ")
processes = 32
match_ids = get_match_ids(event_id)
demo_ids = convert_to_demo_ids(match_ids, processes)
download(demo_ids, processes)
