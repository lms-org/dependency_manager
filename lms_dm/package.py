#!/usr/bin/env python3
from lms_dm import package_manager
import os,sys
import subprocess
from lms_dm import install_utils

class Package:
#self.workingDir = "" #relative path, should be <.../dependency>
#self.nameWithExtensions = ""#name with extension, for example lms:develop
#self.name = "" #name of the package
#self.url = ""#url to the "parent, for example at github

############################################################
##### static functions
    @staticmethod
    def getPurePackageName(packageFull):
        return packageFull.split(":")[0]


    @staticmethod
    def isDirPackage(path):
        packageFile = path+'/lms_package.json'
        if not os.path.isfile(packageFile):
            return False
        return True

    @staticmethod
    def getPackageNameFromPath(path):
        packageFile = path+'/lms_package.json'
        if not os.path.isfile(packageFile):
            print('lms_package.json does not exist in: ' + package)
            return;
        packageData = parseJson(packageFile) #TODO error handling
        self.name = packageData['name']  

    @staticmethod
    def fromPath(path):
        if not isDirPackage(path):
            return #TODO error handling
        p = Package(getPackageNameFromPath(path))
        p.setPackageDir(path)
        return p

#############################################################
#####

    
    def __init__(self,nameWithExtensions,workingDir):
        self.nameWithExtensions = nameWithExtensions
        self.name = self.getPurePackageName(nameWithExtensions)
        self.workingDir = workingDir

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return (self.name == other.name)

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not(self == other)

    def getDependencyDir(self):
        return os.path.join(self.workingDir,"dependencies")

    def getDir(self):
        return os.path.join(self.getDependencyDir(),self.name)

    def installedGlobally(self):
        if os.path.isdir(os.path.join(package_manager.getSrcDir(),self.name)):
            return True
        return False

    def downloadWithDependencies(self, ignoreGlobal=False):
        #install or update the current package
        if not self.download(ignoreGlobal):
            return

        #get all dependencies
        dependencies = self.getPackageDependencies()
        if dependencies is None:
            sys.exit(1)
        for dependency in dependencies:
            dependency.downloadWithDependencies(ignoreGlobal)


    def download(self, ignoreGlobal=False):
        #check if it is installed globally
        if not ignoreGlobal and self.installedGlobally():
            print(self.name + " already installed globally, you might have to update it manually")
            return False
        #set the url
        self.setUrl(package_manager.getPackageUrlFromName(self.name))
            #check if a url was set
        if self.url == None or len(self.url)==0:
            print('Package not found: '+self.name)
            sys.exit(1)

        ###get current source
        #create path
        myDir = self.getDir()
        os.makedirs(self.getDependencyDir(), exist_ok=True)
        dirAbs = os.path.abspath(myDir)
        if self.isGitUrl():
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
            else : 
                p = subprocess.Popen(['git', 'clone', self.getUrl()], cwd=self.getDependencyDir())
                output, err = p.communicate()
                if err is not None:
                    print(output)
                    print("clone failed: "+ myDir)
                    sys.exit(1)
                print("cloned package")

            packageNameParts= self.nameWithExtensions.split(":")
            print("LEN: {0}".format(len(packageNameParts)))
            if len(packageNameParts) > 1:
                print("checking out: "+packageNameParts[1])
                p = subprocess.Popen(['git', 'checkout',packageNameParts[1]], cwd=myDir)
                output, err = p.communicate()
                if err is not None:
                    print(output)
                    print("can't checkout: "+packageNameParts[1])
                    sys.exit(1)

        elif self.isLocalFolder() :
            print('handle local package: ' +packageName)
            if not os.path.isabs(self.getUrl()):
                self.setUrl(os.path.abspath(self.getUrl()));
            #create symlink
            #check if symlink already exists TODO check if valid
            if not os.path.exists(dirAbs):
                os.symlink(self.getUrl(), dirAbs, True)
            else:
                print(dirAbs + ' already exists')
        else :
            print("no valid url-type given")
            sys.exit(1)

        return True
        
        

        

    def hasBinary(self):
        #TODO
        return False


    def hasSource(self):
        #TODO
        return True


###############################################################
#####Set functions
    
    def setUrl(self,url):
        self.url = url;
    
    def getUrl(self):
        return self.url

    def setPackageDir(self,packageDir):
        self.packageDir = packageDir;

    def isGitUrl(self):
        if 'github.com' in self.url: #TODO
            return True
        return False

    def isLocalFolder(self):
        if os.path.isdir(self.url):
            return True
        return False

    def isZipFile(self):
        return False #TODO

    def getPackageFilePath(self):
        return os.path.join(self.getDir(),'lms_package.json')

    def getPackageDependencies(self):
        res = list()
        packageFile = self.getPackageFilePath()
        if not os.path.isdir(self.getDir()):
            print('package does not exist: ' + self.getDir())
            return
        if not os.path.isfile(packageFile):
            print('lms_package.json does not exist in: ' + self.getDir())
            return
        packageData = install_utils.parseJson(packageFile) #TODO error handling
        if 'dependencies' in packageData:
            names = packageData['dependencies']
            for tmp in names:
                res.append(Package(tmp,self.workingDir))
        return res

    #returns a list with all binaries that have to be linked
    def getTargets(self):
        packageFilePath = self.getPackageFilePath()
        json = install_utils.parseJson(packageFilePath)
        if 'targets' in json:
            return json['targets']
        targets = list()
        targets.append(self.name)
        return targets


    def getPackageIncludes(self,absPath=True):
        packageFilePath = self.getPackageFilePath()
        json = install_utils.parseJson(packageFilePath)
        if 'includes' in json:
            includes = json['includes']
        else:
            includes = list()
            includes.add('include')
            
        result = list()
        for include in includes:
            if absPath:
                result.append(os.path.abspath(os.path.join(self.getDir(),include)))
            else:
                result.append(include)
        return result

    def getStringForPackageIncludes(self):
        #each package has one or more binary/target, we have to catch them all!
        targets = self.getTargets()
        print("found targets: {0}".format(targets))
        dependencies = self.getPackageDependencies()
        #get includes for the dependencies
        includeList = list()
        for dependency in dependencies:
            for tmp in dependency.getPackageIncludes():
                includeList.append(tmp)
        if len(includeList) == 0:
            return ""
        res = ""
        for target in targets:
            res += 'target_include_directories({0} PUBLIC {1})'.format(target,' '.join(includeList)) + '\n'
        return res


    def getPackageHierachyDict(self,d=None):
        if d is None:
            d = dict()
        d[self] = self.getPackageDependencies()
        for dep in d[self]:
            dep.getPackageHierachyDict(d)
        return d

    def getCMakeCallCompileDependencyMessage(self):
        return 'add_subdirectory({0})'.format(os.path.abspath(self.getDir()))
    

    def generateCMake(self):
        libPath = os.path.abspath(os.path.join(self.workingDir,"lib"))
        binPath = os.path.abspath(os.path.join(self.workingDir,"bin"))
        includePath = os.path.abspath(os.path.join(self.workingDir,"includePath"))

        #get all package-dependencies
        packageHierarchyList = self.getPackageHierachyDict()
        for p in packageHierarchyList:
            res = list()
            for dp in packageHierarchyList[p]:
                if not dp.installedGlobally():
                    res.append(dp)
            packageHierarchyList[p] = res
        
        #generate hierarchy CMake
        cmakeFile = os.path.join(self.workingDir,'CMakeLists.txt')
        print("CMAKE FILE: "+cmakeFile)
        #os.makedirs('lms_cmake',exist_ok=True) 
        with open(cmakeFile,'w') as file:
            file.write("""cmake_minimum_required(VERSION 2.8)
project({0})
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY {1})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY {1})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY {2})
""".format("NAME_OF_THE_PROJECT_TODO",libPath,binPath))

            file.write('include(customCMake.txt) \n')
            file.write('\n \n#package compile hierachy \n')
            lastSize = 0
            while len(packageHierarchyList) > 0:
                if lastSize == len(packageHierarchyList):
                    #TODO error handling if there is a closed loop :D
                    print("Your dependencies have a closed loop! {0}".format(packageHierarchyList))
                    sys.exit(1)
                lastSize = len(packageHierarchyList)
                toRemove = list()
                for p in packageHierarchyList:
                    if len(packageHierarchyList[p]) == 0:
                        #write the dependency
                        file.write(p.getCMakeCallCompileDependencyMessage()+"\n")
                        #remove it from others
                        toRemove.append(p)
                        for c  in packageHierarchyList:
                            if p in packageHierarchyList[c]:
                                packageHierarchyList[c].remove(p)
                for p in toRemove:
                    packageHierarchyList.pop(p)
            
            #set include paths
            file.write('\n\n#target include paths \n')
            packageHierarchyList = self.getPackageHierachyDict()
            for package in list(packageHierarchyList):
                s = package.getStringForPackageIncludes()
                if len(s) != 0:
                    file.write(s)

        #generatre custom CMake file if it's missing
        customCmake = os.path.join(self.workingDir,'customCMake.txt')
        if not os.path.isfile(customCmake): 
            with open(customCmake,'w') as file:
                file.write("#Add your cmake stuff here")
                



