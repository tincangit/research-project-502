import json
import os
import datetime

jsonDir = "C:/Users/TL/PycharmProjects/researchProj/jsonsToAnalyze"

try:
    os.chdir(jsonDir)
except:
    print("jsonsToAnalyze directory not found. Please make a directory named jsonsToAnalyze. Quitting.")
    quit()

rootDir = os.getcwd()

for root, dirs, files in os.walk(rootDir):
    for name in dirs:
        dirPath = os.path.join(root, name)
        # print(dirPath)
        os.chdir(dirPath)
        analyzeFolder = False
        for fileName in os.listdir(os.getcwd()):
            if fileName.endswith(".json"):
                analyzeFolder = True
                break
        # print(name)
        # print(analyzeFolder)

        if analyzeFolder:
            string = name + " Analysis " + datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S") + ".txt"
            logf = open(string, "a")
            msg = "Analysis session started for " + os.path.dirname(os.getcwd()) + ", " + datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            print(msg)
            logf.write(msg + "\n")
            for fileName in os.listdir(os.getcwd()):
                if fileName.endswith(".json"):
                    f = open(fileName, encoding='utf-8')
                    data = json.load(f)
                    f.close()
                    siteURL = data["log"]["entries"][0]["request"]["url"]
                    siteName = (siteURL.split("//")[1]).split("/")[0]

                    msg = "---"
                    print(msg)
                    logf.write(msg + "\n")

                    print(fileName)
                    logf.write(fileName + "\n")

                    entriesNum = len(data["log"]["entries"])
                    msg = "Num of entries = " + str(entriesNum)
                    print(msg)
                    logf.write(msg + "\n")

                    otherSitesDict = {}
                    postRequests = []
                    entryIndex = 0
                    for entry in data["log"]["entries"]:
                        url = entry["request"]["url"]
                        if entry["request"]["method"] == "POST":
                            postRequests.append(url)
                        site = (url.split("//")[1]).split("/")[0]
                        if not (siteName in site):
                            otherSitesDict.setdefault(site, []).append((url, entryIndex))
                        entryIndex += 1

                    msg = (str(len(otherSitesDict)) + " sites outside the host:")
                    print(msg)
                    logf.write(msg + "\n")

                    otherSitesEntries = 0
                    for site in otherSitesDict:
                        num = len(otherSitesDict[site])
                        otherSitesEntries = otherSitesEntries + num
                        entriesIndices = ""
                        for elem in otherSitesDict[site]:
                            entriesIndices += str(elem[1])
                            entriesIndices += " "
                        msg = ("- " + site + ", " + str(num) + " entries: " + entriesIndices)
                        print(msg)
                        logf.write(msg + "\n")

                    msg = ("Total number of requests to external sites: " + str(otherSitesEntries) + " out of " + str(entriesNum))
                    print(msg)
                    logf.write(msg + "\n")

                    msg = ("Number of POST Requests made: " + str(len(postRequests)) + " out of " + str(entriesNum))
                    print(msg)
                    logf.write(msg + "\n")

                    for i in postRequests:
                        msg = ("POST: " + i)
                        print(msg)
                        logf.write(msg + "\n")

                    msg = "\n\n"
                    print(msg)
                    logf.write(msg)

            msg = ("Analysis session ended " + datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))
            print(msg)
            logf.write(msg + "\n")
            logf.close()
