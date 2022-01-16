import json
import os
import datetime

jsonDir = os.getcwd() + "\jsonsToAnalyze"

domainsFile = open("domainsList.txt")
Lines = domainsFile.readlines()
domainsList = []
for line in Lines:
    domainsList.append(line.strip())

try:
    os.chdir(jsonDir)
except:
    print("jsonsToAnalyze directory not found. Please make a directory named jsonsToAnalyze. Quitting.")
    quit()

rootDir = os.getcwd()

for root, dirs, files in os.walk(rootDir):
    for name in dirs:
        dirPath = os.path.join(root, name)
        os.chdir(dirPath)
        analyzeFolder = False
        for fileName in os.listdir(os.getcwd()):
            if fileName.endswith(".json"):
                analyzeFolder = True
                break

        if analyzeFolder:
            startDTime = datetime.datetime.now()
            string = name + " Analysis " + startDTime.strftime("%d-%m-%Y %H-%M-%S") + ".txt"
            logf = open(string, "a")
            msg = "Analysis session started for " + os.path.dirname(os.getcwd()) + ", " + datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            print(msg)
            logf.write(msg + "\n")

            string = name + " csv " + startDTime.strftime("%d-%m-%Y %H-%M-%S") + ".txt"
            logfCSV = open(string, "a")
            logfCSV.write("Candidate - Website,# of entries,# of sites outside the host,# of Tracking sites,Tracking sites urls,# of POST requests,# of potential tracking pixels\n")

            for fileName in os.listdir(os.getcwd()):
                if fileName.endswith(".json"):
                    f = open(fileName, encoding='utf-8')
                    data = json.load(f)
                    f.close()
                    siteURL = data["log"]["entries"][0]["request"]["url"]
                    siteName = (siteURL.split("//")[1]).split("/")[0]

                    logfCSV.write(data["log"]["pages"][0]["id"] + " - " + siteURL + ",")

                    msg = "---"
                    print(msg)
                    logf.write(msg + "\n")

                    print(fileName)
                    logf.write(fileName + "\n")

                    entriesNum = len(data["log"]["entries"])
                    msg = "Num of entries = " + str(entriesNum)
                    print(msg)
                    logf.write(msg + "\n")
                    logfCSV.write(str(entriesNum) + ",")

                    otherSitesDict = {}
                    postRequests = []
                    trackingPixels = []
                    entryIndex = 0
                    for entry in data["log"]["entries"]:
                        url = entry["request"]["url"]
                        if entry["request"]["method"] == "POST":
                            postRequests.append(url)
                        site = (url.split("//")[1]).split("/")[0]
                        if not (siteName in site):
                            if site[0:4] == "www.":
                                site = site[4:]
                            otherSitesDict.setdefault(site, []).append((url, entryIndex))
                        if entry.get("response").get("content").get("mimeType") is not None:
                            if ("image" in entry.get("response").get("content").get("mimeType")) and (entry.get("response").get("content").get("size") > 0) and (entry.get("response").get("content").get("size") < 100):
                                trackingPixels.append(entryIndex)
                        entryIndex += 1

                    msg = (str(len(otherSitesDict)) + " sites outside the host:")
                    print(msg)
                    logf.write(msg + "\n")

                    siteTrackers = []

                    otherSitesEntries = 0
                    for site in otherSitesDict:
                        num = len(otherSitesDict[site])
                        otherSitesEntries = otherSitesEntries + num
                        entriesIndices = ""
                        for elem in otherSitesDict[site]:
                            entriesIndices += str(elem[1])
                            entriesIndices += " "
                        msg = ("- " + site + ", " + str(num) + " entries: " + entriesIndices)

                        if site in domainsList:
                            siteTrackers.append(site)
                            msg = msg + " TRACKER"

                        print(msg)
                        logf.write(msg + "\n")

                    msg = ("Total number of requests to external sites: " + str(otherSitesEntries) + " out of " + str(entriesNum))
                    print(msg)
                    logf.write(msg + "\n")
                    logfCSV.write(str(len(otherSitesDict)) + ",")
                    logfCSV.write(str(len(siteTrackers)) + ",")
                    for site in siteTrackers:
                        logfCSV.write(site + "&&")
                    logfCSV.write(",")


                    msg = ("Number of POST Requests made: " + str(len(postRequests)) + " out of " + str(entriesNum))
                    print(msg)
                    logf.write(msg + "\n")
                    logfCSV.write(str(len(postRequests)) + ",")


                    for i in postRequests:
                        msg = ("POST: " + i)
                        print(msg)
                        logf.write(msg + "\n")

                    msg = ("Number of requests to known trackers made: " + str(len(siteTrackers)) + " out of " + str(entriesNum))
                    print(msg)
                    logf.write(msg + "\n")

                    for domain in siteTrackers:
                        print(domain)
                        logf.write(domain + "\n")

                    msg = "Potential tracking pixel entries: "
                    for i in trackingPixels:
                        msg = msg + str(i) + " "
                    print(msg)
                    logf.write(msg + "\n")
                    logfCSV.write(str(len(trackingPixels)) + "\n")

                    msg = "\n\n"
                    print(msg)
                    logf.write(msg)

            endDtime = datetime.datetime.now()
            # timeTaken = endDtime - startDTime
            msg = ("Analysis session ended " + endDtime.strftime("%d/%m/%Y, %H:%M:%S"))
            print(msg)
            logf.write(msg + "\n")
            logf.close()
            logfCSV.close()
