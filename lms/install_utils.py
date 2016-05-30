#!/usr/bin/env python3
#parse xml file
import xml.etree.ElementTree
import json
import sys, os
import subprocess

def parseFrameworkXml(configFilePath):
    root = xml.etree.ElementTree.parse(configFilePath).getroot()
    usedPackages = set()
    for xmlUsedMods in root.findall('module'):
        usedPackages.add(xmlUsedMods.find('package').text)
    return usedPackages


def parseJson(packageFilePath):
    with open(packageFilePath) as file:
        return json.load(file)

def getDefaultPackageList():
    homeDir = os.path.expanduser("~")
    return  homeDir+'/lms/packagelist.json'

def getPackageLists():
    result = set()
    result.add('packagelist.json') # TODO hier später alle möglichen ausführen
    result.add(getDefaultPackageList())
    return result

def getPackageUrlFromName(packageName):
    for packageListPath in getPackageLists():
        if not os.path.isfile(packageListPath):
            print('packageFile does not exist: '+packageListPath)
            continue
        packagesData = parseJson(packageListPath)
        if packageName in packagesData:
            return packagesData[packageName]['path']

def getNeededPackageUrls(neededPackages,packagesData):
#TODO später kann man selbst orte festlegen an denen packagelisten sind und somit seine lokalen versionen bevorzugen -> mehrere paketlisten
    result = dict()
    for packageName in neededPackages:
        if packageName in packagesData:
            result[packageName] = packagesData[packageName]['path']
#TODO noch überprüfen ob ein package keine url hat!
    return result

def isGitUrl(url):
    if 'github.com' in url: #TODO
        return True
    return False

def isLocalFolder(url):
    if os.path.isdir(url):
        return True
    return False

def isZipFile(url):
    return False #TODO

def installPackage(packageName,packageUrl):
    dir = 'dependencies/'+packageName;
    dirAbs = os.path.abspath(dir)
    if isGitUrl(packageUrl):
        #check if folder already exists
        if os.path.isdir(dir):
            #pull the dir
            p = subprocess.Popen(['git', 'pull'], cwd=dir)
            output, err = p.communicate();
            if output != 0:
                print("pull failed")
                sys.exit(1)
            #TODO error handling
        else : 
            ret = call(["git","clone",packageUrl, dir])
        if ret != 0:
            print("clone failed")
            sys.exit(1)
        print("cloned package")
    elif isLocalFolder(packageUrl) :
        print('hadle local package: ' +packageName)
        if not os.path.isabs(packageUrl):
            packageUrl = os.path.abspath(packageUrl);
        #create symlink
        #check if symlink already exists TODO check if valid
        if not os.path.exists(dirAbs):
            os.symlink(packageUrl, dirAbs, True)
        else:
            print(dirAbs + ' already exists')
    else :
        print("no valid url-type given")
        sys.exit(1)

def getPackageNameFromPath(path):
    packageFile = path+'/lms_package.json'
    if not os.path.isfile(packageFile):
        print('lms_package.json does not exist in: ' + package)
        return;
    packageData = parseJson(packageFile) #TODO error handling
    return packageData['name']
        

def getPackageDependencies(packageName):
    dir = 'dependencies/'+packageName
    packageFile = dir+'/lms_package.json'
    if not os.path.isdir(dir):
        print('package does not exist: ' + packageName)
        return;
    if not os.path.isfile(packageFile):
        print('lms_package.json does not exist in: ' + package)
        return;
    packageData = parseJson(packageFile) #TODO error handling
    if 'dependencies' in packageData:
        return packageData['dependencies']
    return list()


def registerPackage(packageName,packageUrl, packageListUrl):
    json.dump({packageName : {'path':packageListUrl}}, sort_keys=True, indent=4)
    print('registering package: ' +packageName + packageUrl)
    if os.path.isfile(packageListPath):
        json = parseJson(packageListPath)
    else:
        print(".")
    #TODO write to file
    #TODO errorhandling
    #json.add
    

def getPackageTargets(packageName):
    dir = 'dependencies/'+packageName
    packageFilePath = dir+'/lms_package.json'
    json = parseJson(packageFilePath)
    if 'targets' in json:
        return json['targets']
    targets = list()
    targets.add(packageName)
    return targets

def getPackageAbsPath(relativePath, packageName):
    dir = 'dependencies/'+packageName+'/'+relativePath;
    return os.path.abspath(dir)

def getPackageIncludes(packageName, absPath=True):
    dir = 'dependencies/'+packageName
    packageFilePath = dir+'/lms_package.json'
    json = parseJson(packageFilePath)
    if 'includes' in json:
        includes = json['includes']
    else:
        includes = list()
        includes.add('include')
        
    result = list()
    for include in includes:
        if absPath:
            result.append(getPackageAbsPath(include,packageName))
        else:
            result.append(include)
    return result
    
