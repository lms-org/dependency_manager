#!/usr/bin/env python3
import sys, os

from lms_dm import install_utils


def getDefaultPackageList():
    homeDir = os.path.expanduser("~")
    return  homeDir+'/.lms/packagelist.json'

def getPackageLists():
    result = set()
#   TODO hier später alle möglichen ausführen
    result.add(getDefaultPackageList())
    return result

def getPackageList():
    data = dict()
    for packageListPath in getPackageLists():
        if not os.path.isfile(packageListPath):
            print('packageFile does not exist: '+packageListPath)
            continue
        data[packageListPath] = install_utils.parseJson(packageListPath)
    return data


#def isPackageInstalledGlobally(package):
#    if os.path.isdir(os.path.join(getPackageManagerGlobalDependencyDir(),package.name)):
#        return True
#    return False

def getSrcDir():
    return os.path.join(getDir(),"dependencies")

def getDir():
    return os.path.expanduser('~/.lms/lms_pm/')

def getBinDir():
    return os.path.join(getDir,"bin")

def getLibDir():
    return os.path.join(getDir,"lib")

def getIncludeDir():
    return os.path.join(getDir,"include")


def getPackageUrlFromName(packageName):
    for packageListPath in getPackageLists():
        if not os.path.isfile(packageListPath):
            print('packageFile does not exist: '+packageListPath)
            continue
        packagesData = install_utils.parseJson(packageListPath)
        if packageName in packagesData:
            return packagesData[packageName]['path']

######################################################################
##### environment variables

def checkEnvironmentVariable(key,value):
   # isSet = False
    #envString = '';
    if key in os.environ:
        envString = os.environ[key]
        pathsplit = envString.split(':')
        if value in pathsplit:
            return True
    return False

def checkEnviromentVariables():
    packageManagerDir = os.path.expanduser('~/.lms/package_manager/')
    #http://stackoverflow.com/questions/5971635/setting-reading-up-environment-variables-in-python
    #check PATH
    #export PATH="$PATH:~/.lms/package_manager/bin"
    pathDir = os.path.join(packageManagerDir,'bin')
    cpathDir = os.path.join(packageManagerDir,'include')
    ldpathDir = os.path.join(packageManagerDir,'lib')

    anyMissing=False
    missing = not checkEnvironmentVariable('PATH',pathDir)
    if missing:
        anyMissing = True
        print("PATH NOT set correctly")
    missing = not checkEnvironmentVariable('CPATH',cpathDir)
    if missing:
        anyMissing = True
        print("CPATH NOT set correctly")
    missing = not checkEnvironmentVariable('LD_LIBRARY_PATH',ldpathDir)
    if missing:
        anyMissing = True
        print("LD_LIBRARY_PATH NOT set correctly")
    if not anyMissing:
        print("Everything seems to be set correctly")
        return
    
    #Ask to add missing env variables
    #TODO os check http://stackoverflow.com/questions/1854/python-what-os-am-i-running-on
    #UNIX
    profileFile = os.path.expanduser('~/.profile')
    lmsbash = os.path.join(getDir(),'.bashrc')

    #add the lmsbash file
    if not os.path.isfile(lmsbash):
        #write the lms bashfile
        with open(lmsbash,'w') as file:
            bashString ="""export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:{1}"
export PATH="$PATH:{2}"
export CPATH="$CPATH:{3}" """.format(getLibDir(),getBinDir(),getIncludeDir()) 
            file.write(bashString)

    #check if they were already added but not loaded
    with open(profileFile,'r') as file:
        fileRead = file.read()
        if lmsbash in fileRead:
            print("already added, you may have to relog/restart")
            print("If it doesn't work please include bash file yourself (add . "+lmsbash+" to your bashrc or HOME/.profile or to any other file, you could also set the PATH,CPATH,LD_LIBRARY_PATH yourself")
            return
        else:
            print("Missing environment variables")
    #Ask the user if we should add them in .profile
    autoEnvInstall = install_utils.query_yes_no("lpm could add the environment variables to your .profile", None)

    if autoEnvInstall and os.path.isfile(profileFile):
        #add it ot .profile
        with open(profileFile,'a') as file:
            print('you can add it to ~/.profile')
            profileString ="""\n#automatically added by the lms package manager
if [ -d "{0}" ] ; then
. "{0}"
fi
""".format(lmsbash)
            file.write(profileString)
            print("call <exec bash> to reload changes (might not work, just relog/reboot)")
                
    else:
        print('please include bash file yourself (add . "'+lmsbash+'" to your bashrc or HOME/.profile or to any other file, you could also set the PATH,CPATH,LD_LIBRARY_PATH yourself)')
    #WIN TODO

def printPackageList():
    data = install_utils.getPackageList()
    #TODO alphabetisch sortieren
    for listFile in data:
        print("file: "+listFile)
        for package in data[listFile]:
            print(package + "   " + data[listFile][package]['description'])
