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


def getData(matchID):
    html = getHTML("https://www.hltv.org/matches/%s" % (matchID))
    # Search variables data-unix="
    date = re.findall('data-unix=\".*\"', html)
    teamIDs = re.findall('src=\"https://static.hltv.org/images/team/logo/.*\" class', html)
    teamNames = re.findall('class=\"logo\" title=\".*\">', html)
    map = re.findall('<div class=\"mapname\">.*</div>', html)
    scores = re.findall('<div class=\"results\"><span class=\".*</span><span>', html)
    print(scores)
    if len(teamNames) < 1:
        return True
    eventNames = re.findall('text-ellipsis\">.*<', html)
    eventEndDate = re.findall('class="standard-headline">.*<', html)

    if len(date) > 0:
        date[0] = (date[0].replace("data-unix=\"", "")).replace("\"", "")[:-3]
        date[0] = datetime.utcfromtimestamp(int(date[0])).strftime('%Y-%m-%d')
    else:
        date.append(0)

    # print teamID
    if len(teamIDs) > 0:
        teamIDs[0] = (teamIDs[0].replace("src=\"https://static.hltv.org/images/team/logo/", "")).replace("\" class", "")
        teamIDs[1] = (teamIDs[1].replace("src=\"https://static.hltv.org/images/team/logo/", "")).replace("\" class", "")
        # print(teamIDs[0] + teamIDs[1])
    else:
        teamIDs.append(0)

    # print map
    if len(map) > 0:
        map[0] = (map[0].replace("<div class=\"mapname\">", "")).replace("</div>", "")
    else:
        map.append(0)

    # print eventEndDate
    if len(eventEndDate) > 0:
        eventEndDate[0] = (eventEndDate[0].replace("class=\"standard-headline\">", "")).replace("<", "")
    else:
        eventEndDate.append(0)
    print("%s,%s,%s,%s,%s" % (date[0], map[0], teamIDs[0], teamIDs[1], matchID))
    return "%s,%s,%s" % (teamNames[0], teamNames[1], matchID)


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
with open('joinMatchEvent.csv', encoding='utf-8') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        eventIDs.append(row[0])

getData("2311068/faze-vs-fnatic-ecs-season-3-europe")
# eventIDs = list(range(2000,2500))
# print(eventIDs)
threads = multiprocessing.cpu_count()
# processIDs(eventIDs, threads)
