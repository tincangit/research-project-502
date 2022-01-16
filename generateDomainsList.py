import json
import os
import datetime

domainsDir = os.getcwd() + "\domains"
domainsList = []
logf = open("domainsList.txt", "w")
for root, dirs, files in os.walk(domainsDir):
    for fname in files:
        if not(fname[:-5] in domainsList):
            domainsList.append(fname[:-5])
            logf.write(fname[:-5] + "\n")

logf.close()