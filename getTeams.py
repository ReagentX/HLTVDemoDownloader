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


def getData(teamID):
    html = getHTML("https://www.hltv.org/team/%s/a" % (teamID))
    # Find the type of event (online, LAN, etc)
    teamName = re.findall('<div><span class=\"subjectname\">.*</span><br><i', html)
    if len(teamName) < 1:
        return True
    teamCountry = re.findall('fa fa-map-marker\" aria-hidden=\"true\"></i>.*<', html)
    if len(teamCountry) < 1:
        teamCountry = re.findall('fa fa-map-marker\" aria-hidden=\"true\"></i>.*</div>', html)
    if len(teamCountry) < 1:
        return True

    # print teamName
    if len(teamName) > 0:
        teamName[0] = (teamName[0].replace("<div><span class=\"subjectname\">", "")).replace("</span><br><i", "")
    else:
        teamName.append(0)

    # print teamCountry
    if len(teamCountry) > 0:
        teamCountry[0] = (teamCountry[0].replace("fa fa-map-marker\" aria-hidden=\"true\"></i> ", "")).split("<", 1)[0]
    else:
        teamCountry.append(0)

    print("%s,%s,%s" % (teamName[0], teamCountry[0], teamID))
    return "%s,%s,%s" % (teamName[0], teamCountry[0], teamID)


def getHTML(url):
    # Open the URL
    # Spoof the user agent
    request = Request(url)
    request.add_header('User-Agent', 'Mozilla/5.0')
    # Read the response as HTML
    html = urlopen(request).read().decode('ascii', 'ignore')
    return html


removeIDs = []
with open('teams.csv', encoding='utf-8') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        removeIDs.append(row[2])

teamIDs = list(range(1, 7948))
for i in range(1, len(removeIDs)):
    if int(removeIDs[i]) in teamIDs:
        teamIDs.remove(int(removeIDs[i]))


threads = multiprocessing.cpu_count()
processIDs(teamIDs, threads)
