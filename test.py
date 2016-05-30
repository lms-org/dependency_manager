#!/usr/bin/env python3
#parse xml file
import xml.etree.ElementTree
import json

def parseFrameworkXml(configFilePath):
    root = xml.etree.ElementTree.parse(configFilePath).getroot()
    usedPackages = set()
    for xmlUsedMods in root.findall('module'):
        usedPackages.add(xmlUsedMods.find('package').text)
    return usedPackages


def parsePackageList(packageFilePath):
    with open(packageFilePath) as file:
        return json.load(file)

def getNeededPackageUrls(neededPackages,packagesData):
#TODO später kann man selbst orte festlegen an denen packagelisten sind und somit seine lokalen versionen bevorzugen -> mehrere paketlisten
    result = dict()
    for packageName in neededPackages:
        if packageName in packagesData:
            result[packageName] = packagesData[packageName]['path']
#TODO noch überprüfen ob ein package keine url hat!
    return result

def isGitUrl(url):
    return True #TODO


#Jetzt holen wir uns zu jedem package die passende URL
#TODO version fehlt noch, wir splitten am ersten:
#TODO es fehlt noch die überprüfung ob manche packages mehrfach mit anderen URLs definiert wurden
neededPackages = parseFrameworkXml('framework_conf.xml')
packagesData = parsePackageList('packagelist.json')

packages = getNeededPackageUrls(neededPackages,packagesData);
print(packages)
#Nun müssen wir prüfen was es für eine url ist
for package in packages:
    url = packages[package]
    if isGitUrl(url):
        print('git url: '+url)
        #TODO wir downloaden das repo
    else :
        print("No valid url given for " +package + " url: " + url)

#Nun haben wir alle benötigten packages
#Fragen zu klären: 
#1. Wohin mit den externen daten?

#2. Was machen wir mit lokalen?

#Ordnerstruktur:
# config_repo
# - configs
# - dependencies

#zu 1. wir laden es in den dependencies ordner runter
#zu 2. wir erstellen einen hardlink

