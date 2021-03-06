#!/usr/bin/env python3
#parse xml file
import xml.etree.ElementTree
import json
import sys, os
import subprocess
#from subprocess import call

def parseFrameworkXml(configFilePath):
    root = xml.etree.ElementTree.parse(configFilePath).getroot()
    usedPackages = set()
    for xmlUsedMods in root.findall('module'):
        usedPackages.add(xmlUsedMods.find('package').text)
    return usedPackages


def parseJson(packageFilePath):
    with open(packageFilePath) as file:
        return json.load(file)

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

def installPackage(packageName,packageUrl, packageNameParts, dependencyDir):
    #create path
    os.makedirs(dependencyDir, exist_ok=True)
    myDir = os.path.join(dependencyDir,packageName)
    dirAbs = os.path.abspath(myDir)
    if isGitUrl(packageUrl):
        #check if folder already exists
        print("mydir: " + myDir)
        if os.path.isdir(myDir):
            #pull the dir
            p = subprocess.Popen(['git', 'pull'], cwd=myDir)
            output, err = p.communicate()
            if err is not None:
                print(output)
                print("pull failed")
                sys.exit(1)
            print("pulled package")
            #TODO error handling
        else : 
            #ret = subprocess.call(["git","clone",packageUrl, dir])
            p = subprocess.Popen(['git', 'clone', packageUrl], cwd=dependencyDir)
            output, err = p.communicate()
            if err is not None:
                print(output)
                print("clone failed: "+ myDir)
                sys.exit(1)
            print("cloned package")
        print("LEN: {0}".format(len(packageNameParts)))
        if len(packageNameParts) > 1:
            print("checking out: "+packageNameParts[1])
            p = subprocess.Popen(['git', 'checkout',packageNameParts[1]], cwd=myDir)
            output, err = p.communicate()
            if err is not None:
                print(output)
                print("can't checkout: "+packageNameParts[1])
                sys.exit(1)

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
        

def getPackageDependencies(packageDir, withoutExtensions=False):
    packageFile = packageDir+'/lms_package.json'
    if not os.path.isdir(packageDir):
        print('package does not exist: ' + packageDir)
        return;
    if not os.path.isfile(packageFile):
        print('lms_package.json does not exist in: ' + packageDir)
        return;
    packageData = parseJson(packageFile) #TODO error handling
    if 'dependencies' in packageData:
        res = packageData['dependencies']
        if withoutExtensions:
            for tmp in res:
                packageSplit= tmp.split(':')
                if len(packageSplit) > 1:
                    res.remove(tmp)
                    res.append(packageSplit[0])
        return res
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
    
#returns a list with all binaries that have to be linked
def getPackageTargets(packageName,dependencyDir):
    packageFilePath = os.path.join(dependencyDir,packageName,'lms_package.json')
    json = parseJson(packageFilePath)
    if 'targets' in json:
        return json['targets']
    targets = list()
    targets.append(packageName)
    return targets


def getPackageIncludes(packageDir, absPath=True):
    packageFilePath = packageDir+'/lms_package.json'
    json = parseJson(packageFilePath)
    if 'includes' in json:
        includes = json['includes']
    else:
        includes = list()
        includes.add('include')
        
    result = list()
    for include in includes:
        if absPath:
            result.append(os.path.abspath(packageDir+'/'+include))
        else:
            result.append(include)
    return result
    
#from http://stackoverflow.com/questions/3041986/python-command-line-yes-no-input

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
