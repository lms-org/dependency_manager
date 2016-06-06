#!/usr/bin/env python3
#Installs a dependency with all its dependencies
import sys, os
from lms_dm import install_utils

def checkIfDirIsPackage(path):
    packageFile = path+'/lms_package.json'
    if not os.path.isfile(packageFile):
        return False;
    return True;

def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

def getCMakeCallCompileDependencyMessage(packageName):
    return 'add_subdirectory({0})'.format(install_utils.getPackageAbsPath('',packageName))

def installPackageWithDependencies(packageFull):
    
    packageNameParts = packageFull.split(":")
    package = packageNameParts[0]
    print("installing package {0} with parameters {1}".format(package,packageNameParts))

    packageUrl = install_utils.getPackageUrlFromName(package)

    #check if a url was set
    if packageUrl == None:
        print('Package not found: '+package)
        sys.exit(1)

    print(packageUrl)

    #install package
    install_utils.installPackage(package,packageUrl,packageNameParts)

    #get dependencies
    dependencies = install_utils.getPackageDependencies(package)
    
    if dependencies is not None:
        for dependency in dependencies:
            print("installing dependency: " +dependency) 
            installPackageWithDependencies(dependency)
            #TODO check if dependency was already added, if not create cmake file for it


def getTargetIncludeString(target, includelist):
    return 'target_include_directories({0} PUBLIC {1})'.format(target,' '.join(includelist))


def getStringForPackageIncludes(packageName):
    ##each package has one or more binary/target, we have to catch them all!
    targets = install_utils.getPackageTargets(packageName)
    print("found targets: {0}".format(targets))
    dependencies = install_utils.getPackageDependencies(packageName,True)
    #get includes for the dependencies
    includeList = list()
    for dependency in dependencies:
        for tmp in install_utils.getPackageIncludes(dependency):
            includeList.append(tmp)
    if len(includeList) == 0:
        return ""
    res = ""
    for target in targets:
        res += getTargetIncludeString(target,includeList) + '\n'
    return res


  

#RUNNING CODE

if len(sys.argv) != 2:
    print("Usage: lms-flags <dependency>")
    sys.exit(1)

package = sys.argv[1]

#installing it
installPackageWithDependencies(package)
print("installing Done")

#get all package-dependencies
packageHierarchyList = dict();
for dir in get_immediate_subdirectories('dependencies'):
    if not checkIfDirIsPackage('dependencies/'+dir):
        print("invalid dir given: "+dir)
        continue;
    #ignore package parameters as we can't compile two times the same package with different versions (targetName fails)  
    packageHierarchyList[dir]=install_utils.getPackageDependencies(dir, True)      

print(packageHierarchyList)


#generate hierarchy CMake
cmakeFile = 'CMakeLists.txt'
#os.makedirs('lms_cmake',exist_ok=True)
with open(cmakeFile,'w') as file:
    file.write('cmake_minimum_required(VERSION 2.8) \n')
    file.write('project(TODO) \n') # TODO get the current dirname
    
    #TODO check if file exists
    file.write('include(custemCMake.txt) \n')
    packageHierarchyListCopy = packageHierarchyList.copy()

    file.write('\n \n#package compile hierachy \n')
    lastSize = len(packageHierarchyListCopy)
    while len(packageHierarchyListCopy) > 0:
        for packageDependencies in list(packageHierarchyListCopy):
            if len(packageHierarchyListCopy[packageDependencies]) == 0:
                file.write(getCMakeCallCompileDependencyMessage(packageDependencies)+'\n')
                #remove it from all other lists
                packageHierarchyListCopy.pop(packageDependencies)
                for tmp in packageHierarchyListCopy:
                    if packageDependencies in packageHierarchyListCopy[tmp]:
                        packageHierarchyListCopy[tmp].remove(packageDependencies)
        if lastSize == len(packageHierarchyListCopy):
            #TODO error handling if there is a closed loop :D
            print("Your dependencies have a closed loop! {0}".format(packageHierarchyListCopy))
            sys.exit(1)

    file.write('\n\n#target include paths \n')
    for package in list(packageHierarchyList):
        s = getStringForPackageIncludes(package)
        if len(s) != 0:
            file.write(s)

print("Done")



    
        




