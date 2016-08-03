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

    def getDependencyDir(self):
        return os.path.join(self.workingDir,"dependencies")

    def getDir(self):
        return os.path.join(self.getDependencyDir(),self.name)

    def installedGlobally(self):
        if os.path.isdir(os.path.join(package_manager.getSrcDir(),self.name)):
            return True
        return False

    def installWithDependencies(self, ignoreGlobal=False):
        #install or update the current package
        if not self.installOrUpdate(ignoreGlobal):
            return

        #get all dependencies
        dependencies = self.getPackageDependencies()
        print("DEPENDENCIES: {0}".format(dependencies))
        if dependencies is None:
            sys.exit(1)
        for dependency in dependencies:
            dependency.installWithDependencies(ignoreGlobal)


    def installOrUpdate(self, ignoreGlobal=False):
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
    def getPackageTargets(self):
        packageFilePath = self.getPackageFilePath()
        json = install_utils.parseJson(packageFilePath)
        if 'targets' in json:
            return json['targets']
        targets = list()
        targets.append(packageName)
        return targets


    def getPackageIncludes(absPath=True):
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

    def generateCMake(self, dir):

        libPath = os.path.abspath(os.path.join(dir,"lib"))
        binPath = os.path.abspath(os.path.join(dir,"bin"))
        includePath = os.path.abspath(os.path.join(dir,"includePath"))
        #get all package-dependencies
        packageHierarchyList = dict()
        for subdir in get_immediate_subdirectories(dependencyDir):
            if not package.isDirPackage(dependencyDir+'/'+subdir):
                print("invalid dir given: "+subdir)
                continue;
            #ignore package parameters as we can't compile two times the same package with different versions (targetName fails)  
            result=install_utils.getPackageDependencies(dependencyDir+'/'+subdir, True)  
            #remove globally installed packages
            for tmp in result:
                if isPackageInstalledGlobally(tmp):
                    result.remove(tmp)
            packageHierarchyList[subdir] = result

        print(packageHierarchyList)


        #generate hierarchy CMake
        cmakeFile = os.path.join(installDir,'CMakeLists.txt')
        print("CMAKE FILE: "+cmakeFile)
        #os.makedirs('lms_cmake',exist_ok=True) 
        with open(cmakeFile,'w') as file:
            file.write("""cmake_minimum_required(VERSION 2.8)
    project({0})
    set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY {1})
    set(CMAKE_LIBRARY_OUTPUT_DIRECTORY {1})
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY {2})
    """.format("NAME_OF_THE_PROJECT_TODO",os.path.abspath("lib"),os.path.abspath("bin"))) # TODO get the current dirname
            
            file.write('include(customCMake.txt) \n')
            packageHierarchyListCopy = packageHierarchyList.copy()

            file.write('\n \n#package compile hierachy \n')
            lastSize = len(packageHierarchyListCopy)
            while len(packageHierarchyListCopy) > 0:
                for packageDependencies in list(packageHierarchyListCopy):
                    installedGlobally = isPackageInstalledGlobally(packageDependencies)
                    if isGlobal:
                        installedGlobally = False #TODO Hack to enable installation of global packages....
                    print(packageDependencies+" installedGlobally: {0}".format(installedGlobally))
                    if len(packageHierarchyListCopy[packageDependencies]) == 0 or installedGlobally:
                        if not installedGlobally:
                            file.write(getCMakeCallCompileDependencyMessage(dependencyDir+'/'+packageDependencies)+'\n')
                        #remove it from all other lists
                        packageHierarchyListCopy.pop(packageDependencies)
                        for tmp in packageHierarchyListCopy:
                            if packageDependencies in packageHierarchyListCopy[tmp]:
                                packageHierarchyListCopy[tmp].remove(packageDependencies)
                if lastSize == len(packageHierarchyListCopy):
                    #TODO error handling if there is a closed loop :D
                    print("Your dependencies have a closed loop! {0}".format(packageHierarchyListCopy))
                    sys.exit(1)
                lastSize = len(packageHierarchyListCopy)

            file.write('\n\n#target include paths \n')
            for package in list(packageHierarchyList):
                s = getStringForPackageIncludes(package,dependencyDir,globalHack=isGlobal) #TODO packageName
                if len(s) != 0:
                    file.write(s)
        #generatre custom CMake file
        customCmake = os.path.join(installDir,'customCMake.txt')
        if not os.path.isfile(customCmake): 
            with open(customCmake,'w') as file:
                file.write("#Add your cmake stuff here")
                



