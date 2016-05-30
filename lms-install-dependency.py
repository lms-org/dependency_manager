#!/usr/bin/env python3
#Installs a dependency with all its dependencies
import sys, os
from lms import install_utils

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

def installPackageWithDependencies(package):
    packageUrl = install_utils.getPackageUrlFromName(package)

    #check if a url was set
    if packageUrl == None:
        print('Package not found: '+package)
        sys.exit(1)

    print(packageUrl)

    #install package
    install_utils.installPackage(package,packageUrl)

    #get dependencies
    dependencies = install_utils.getPackageDependencies(package)
    print(dependencies)

    for dependency in dependencies:
        print("installing dependency: " +dependency) 
        installPackageWithDependencies(dependency)
        #TODO check if dependency was already added, if not create cmake file for it


def getTargetIncludeString(target, includelist):
    return 'target_include_directories({0} PUBLIC {1})'.format(target,' '.join(includelist))


def generateCMakeForPackage(packageName):
    #generate cmake file
    print("generating cmake file for: " +packageName)
    #get the targets of the package
    targets = install_utils.getPackageTargets(packageName)
    print("found targets: {0}".format(targets))
    dependencies = install_utils.getPackageDependencies(packageName)
    #get includes for the dependencies
    includeList = list()
    for dependency in dependencies:
        for tmp in install_utils.getPackageIncludes(packageName):
            includeList.append(tmp)
    #print('includeList: {0}'.format(includeList))
    #print(getTargetIncludeString(packageName,includeList))

    cmakeFile = 'lms_cmake/'+packageName+'.cmake'
    os.makedirs('lms_cmake',exist_ok=True)        
    with open(cmakeFile,'w') as file:
        file.write(getTargetIncludeString(packageName,includeList))
    print("DONE generating cmake")


  

if len(sys.argv) != 2:
    print("Usage: lms-flags <dependency>")
    sys.exit(1)


#RUNNING CODE
package = sys.argv[1]  

#installing it
installPackageWithDependencies(package)

#generate CMake for one package
generateCMakeForPackage(package)

#generate hierarchy CMake
#get all packages
packageHierarchyList = dict();
for dir in get_immediate_subdirectories('dependencies'):
    if not checkIfDirIsPackage(dir):
        print("invalid dir given: "+dir)
        continue;
    packageHierarchyList[dir]=install_utils.getPackageDependencies(dir)

cmakeFile = 'lms_cmake/CMakeLists.txt'
os.makedirs('lms_cmake',exist_ok=True)        
with open(cmakeFile,'w') as file:
    lastSize = len(packageHierarchyList)
    while len(packageHierarchyList) > 0:
        for packageDependencies in list(packageHierarchyList):
            if len(packageHierarchyList[packageDependencies]) == 0:
                file.write(getCMakeCallCompileDependencyMessage(packageDependencies)+'\n')
                #remove it from all other lists
                packageHierarchyList.pop(packageDependencies)
                for tmp in packageHierarchyList:
                    if packageDependencies in packageHierarchyList[tmp]:
                        packageHierarchyList[tmp].remove(packageDependencies)
        if lastSize == len(packageHierarchyList):
            #TODO error handling if there is a closed loop :D
            print("Your dependencies have a closed loop! {0}".format(packageHierarchyList))
            sys.exit(1)
    #glob all the files
    file.write('''\n
file(GLOB toInclude *.cmake)
foreach(myPath ${toInclude})
    include(${myPath})
endforeach(myPath)''')



    
        




