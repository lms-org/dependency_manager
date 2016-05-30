#!/usr/bin/env python3
#Register a dependency
import sys, os
from lms import install_utils

dependencyDir = ''
dependencyName = ''

if len(sys.argv) == 1:
    print("register current folder")
    if not os.path.isfile('lms_package.json'):
        print("no lms_package.json file given")
        
    dependencyDir = os.getcwd()
    dependencyName = install_utils.getPackageNameFromPath(dependencyDir)
    
    if dependencyName == None:
        print("Package not found: "+dependencyDir + ' no packagename set!')
        sys.exit(1)

elif len(sys.argv) == 3:
    print("register given dependency")
    dependencyName = sys.argv[1]
    dependencyDir = sys.argv[2]
else :
    print("no params if you are in a valid package")
    print("use <dependencyUrl> <dependencyName>")
    sys.exit(1)
    
packageList = install_utils.getDefaultPackageList()

#TODO



    
    
