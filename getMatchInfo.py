from urllib.request import Request, urlopen
import re
import csv
from datetime import datetime
import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Process, Queue



def processIDs(matchIDs, threads):

        # Define the number of threads
        pool = ThreadPool(threads)

        # Calls get() and adds the filesize returned each call to an array called filesizes
        pool.map_async(getData, matchIDs)
        pool.close()
        pool.join()
        print("Done!")

def getData(matchID):
    # Set some vars for later
    team1 = 0
    team2 = 0
    team1half1 = 0
    team1half2 = 0
    team2half1 = 0
    team2half2 = 0
    team1ot = 0
    team2ot = 0
    html = getHTML("https://www.hltv.org/matches/%s" % (matchID))
    # Search variables data-unix="
    date = re.findall('data-unix=\".*\"', html)
    teamIDs = re.findall('src=\"https://static.hltv.org/images/team/logo/.*\" class', html)
    teamNames = re.findall('class=\"logo\" title=\".*\">', html)
    map = re.findall('<div class=\"mapname\">.*</div>', html)
    scores = re.findall('<div class=\"results\"><span class=\".*</span><span>', html)

    # Give up if no team names found
    if len(teamNames) < 1:
        return True

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
    if len(map) == 1:
        map[0] = (map[0].replace("<div class=\"mapname\">", "")).replace("</div>", "")
    elif len(map) > 1:
        for i in range(0, len(map)):
            map[i] = (map[i].replace("<div class=\"mapname\">", "")).replace("</div>", "")
    else:
        map.append(0)

    # print scores
    sides = []
    if len(scores) == 1:
        if re.findall('\"t\"|\"ct\"', scores[0])[0] == '\"t\"':
            sides.append("T")
            sides.append("CT")
        else:
            sides.append("CT")
            sides.append("T")
    elif len(scores) > 1:
        for i in range(0, len(scores)):
            if re.findall('\"t\"|\"ct\"', scores[i])[0] == "\"t\"":
                sides.append("T")
                sides.append("CT")
            else:
                sides.append("CT")
                sides.append("T")
    else:
        return True

    if len(map) == 1:
        scores[0] = re.findall('\d+', scores[0])
    elif len(map) > 1:
        for i in range(0, len(scores)):
            scores[i] = re.findall('\d+', scores[i])
    else:
        scores.append(0)

    for i in range(0, len(scores)):
        if len(scores[i]) == 6:
            scores[i].append(0)
            scores[i].append(0)
            for set in range(0, len(scores[i])):
                team1 = scores[i][0]
                team2 = scores[i][1]
                team1half1 = scores[i][2]
                team1half2 = scores[i][3]
                team2half1 = scores[i][4]
                team2half2 = scores[i][5]
                team1ot = scores[i][6]
                team2ot = scores[i][7]
        elif len(scores[i]) > 6:
            for set in range(0, len(scores[i])):
                team1 = scores[i][0]
                team2 = scores[i][1]
                team1half1 = scores[i][2]
                team1half2 = scores[i][3]
                team2half1 = scores[i][4]
                team2half2 = scores[i][5]
                team1ot = scores[i][6]
                team2ot = scores[i][7]
        else:
            return True


    # Handle printing
    if len(map) > 1:
        for i in range(0, len(scores)):
            print("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (date[0], map[i], teamIDs[0], sides[0], scores[i][0], scores[i][2], scores[i][4], scores[i][6], teamIDs[1], sides[1], scores[i][1], scores[i][3], scores[i][5], scores[i][7], matchID))
    else:
        print("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (date[0], map[0], teamIDs[0], sides[0], scores[0][0], scores[0][2], scores[0][4], scores[0][6], teamIDs[1], sides[1], scores[0][1], scores[0][3], scores[0][5], scores[0][7], matchID))
    return True


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
    html = urlopen(request).read().decode('ascii', 'ignore')
    return html


def chunks(list, chunks):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(list), chunks):
        yield list[i:i + chunks]


eventIDs = []
with open('matchIDs.csv', encoding='utf-8') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        eventIDs.append(row[0])

removeIDs = []
with open('matches.csv', encoding='utf-8') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        removeIDs.append(row[14])


print(len(eventIDs))
for i in range(1, len(removeIDs)):
    if removeIDs[i] in eventIDs:
        eventIDs.remove(removeIDs[i])
print(len(eventIDs))

# eventIDs = ["2311209/teamone-vs-keyd-stars-liga-pro-alienware-gamersclub-4"]
# print(eventIDs)
# threads = multiprocessing.cpu_count()
threads = 32
processIDs(eventIDs, threads)
