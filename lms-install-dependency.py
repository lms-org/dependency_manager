#!/usr/bin/env python3
#Installs a dependency with all its dependencies
import sys, os
import argparse
import subprocess
from lms_dm import install_utils

def checkIfDirIsPackage(path):
    packageFile = path+'/lms_package.json'
    if not os.path.isfile(packageFile):
        return False;
    return True;

def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

def getCMakeCallCompileDependencyMessage(packageDir):
    return 'add_subdirectory({0})'.format(os.path.abspath(packageDir))

def collectPackageWithDependencies(packageFull, dependencyDir):
    """Installs (prepares) the package (downloads it or creates symlink), same for each dependency
    """
    
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
    install_utils.installPackage(package,packageUrl,packageNameParts,dependencyDir=dependencyDir)
    
    #get dependencies
    dependencies = install_utils.getPackageDependencies(dependencyDir+'/'+package)
    print("DEPENDENCIES: {0}".format(dependencies))
    if dependencies is not None:
        for dependency in dependencies:
            print("installing dependency: {0}".format(dependency)) 
            collectPackageWithDependencies(dependency,dependencyDir)
            #TODO check if dependency was already added, if not create cmake file for it


def getTargetIncludeString(target, includelist):
    return 'target_include_directories({0} PUBLIC {1})'.format(target,' '.join(includelist))


def getStringForPackageIncludes(packageName, dependencyDir):
    ##each package has one or more binary/target, we have to catch them all!
    targets = install_utils.getPackageTargets(packageName,dependencyDir)
    print("found targets: {0}".format(targets))
    dependencies = install_utils.getPackageDependencies(os.path.join(dependencyDir,packageName),True)
    #get includes for the dependencies
    includeList = list()
    for dependency in dependencies:
        for tmp in install_utils.getPackageIncludes(os.path.join(dependencyDir,dependency)):
            includeList.append(tmp)
    if len(includeList) == 0:
        return ""
    res = ""
    for target in targets:
        res += getTargetIncludeString(target,includeList) + '\n'
    return res

def downloadAndCreateCMake(package, installDir=''):
    """install package in <installDir>dependencies (has to end with /)
    """
    dependencyDir = installDir+'dependencies'
    collectPackageWithDependencies(package,dependencyDir)
    print("installing Done")

    #get all package-dependencies
    packageHierarchyList = dict()
    for subdir in get_immediate_subdirectories(dependencyDir):
        if not checkIfDirIsPackage(dependencyDir+'/'+subdir):
            print("invalid dir given: "+subdir)
            continue;
        #ignore package parameters as we can't compile two times the same package with different versions (targetName fails)  
        packageHierarchyList[subdir]=install_utils.getPackageDependencies(dependencyDir+'/'+subdir, True)      

    print(packageHierarchyList)


    #generate hierarchy CMake
    cmakeFile = installDir+'CMakeLists.txt'
    #os.makedirs('lms_cmake',exist_ok=True)
    with open(cmakeFile,'w') as file:
        file.write('cmake_minimum_required(VERSION 2.8) \n')
        file.write('project(TODO) \n') # TODO get the current dirname
        
        file.write('include(customCMake.txt) \n')
        packageHierarchyListCopy = packageHierarchyList.copy()

        file.write('\n \n#package compile hierachy \n')
        lastSize = len(packageHierarchyListCopy)
        while len(packageHierarchyListCopy) > 0:
            for packageDependencies in list(packageHierarchyListCopy):
                if len(packageHierarchyListCopy[packageDependencies]) == 0:
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

        file.write('\n\n#target include paths \n')
        for package in list(packageHierarchyList):
            s = getStringForPackageIncludes(package,dependencyDir) #TODO packageName
            if len(s) != 0:
                file.write(s)
    #generatre custom CMake file
    customCmake = os.path.join(installDir,'customCMake.txt')
    if not os.path.isfile(customCmake): 
        with open(customCmake,'w') as file:
            file.write("#Add your cmake stuff here")
            #
    
    print("Done")

def prepareGlobally(package):
    #install package globally
    path = os.path.expanduser('~/.lms/lms_pm/')
    downloadAndCreateCMake(package,path)
    return path

def prepareLocally(package):
    downloadAndCreateCMake(package)
    return ''



#RUNNING CODE
#configure argument parser
parser = argparse.ArgumentParser(description='Process install command.')
parser.add_argument('package', help='packageName with extensions')
parser.add_argument('-g','--global', dest='installGlobally', help='install package globally', action='store_true')
parser.add_argument('-m','--make', dest='make', help='run cmake and make', action='store_true')

#parse args
resultArgs = parser.parse_args()
installDir = ''
if resultArgs.installGlobally:
    installDir = prepareGlobally(resultArgs.package)
    #TODO generate cmake for make install
else:
    installDir = prepareLocally(resultArgs.package)

#compile it if required
if resultArgs.make:
    #create build dir
    buildDir = os.path.join(installDir,'build')
    os.makedirs(buildDir,exist_ok=True)
    p = subprocess.Popen(['cmake', '..'], cwd=buildDir)
    output, err = p.communicate()
    if err is not None:
        print(output)
        print("cmake failed")
        sys.exit(1)
    if resultArgs.installGlobally:
        p = subprocess.Popen(['make install'], cwd=buildDir)      
    else:
        p = subprocess.Popen(['make'], cwd=buildDir)
    output, err = p.communicate()
    if err is not None:
        print(output)
        print("make failed")
        sys.exit(1)




    
        




