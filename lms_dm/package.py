#!/usr/bin/env python3
import package_manager

class Package:
        self.workingDir = "" #relative path, should be <.../dependency>
        self.nameWithExtensions = ""#name with extension, for example lms:develop
        self.name = "" #name of the package
        self.url = ""#url to the "parent, for example at github

############################################################
##### static functions

    def getPurePackageName(packageFull):
        return packageFull.split(":")[0]


    def isDirPackage(path):
        packageFile = path+'/lms_package.json'
        if not os.path.isfile(packageFile):
            return False
        return True

    def getPackageNameFromPath(path):
        packageFile = path+'/lms_package.json'
        if not os.path.isfile(packageFile):
            print('lms_package.json does not exist in: ' + package)
            return;
        packageData = parseJson(packageFile) #TODO error handling
        self.name = packageData['name']  

    def fromPath(path):
        if not isDirPackage(path)
            return #TODO error handling
        p = Package(getPackageNameFromPath(path))
        p.setPackageDir(path)
        return p

#############################################################
#####

    
    def __init__(self,nameWithExtensions,workingDir):
        self.nameWithExtensions = nameWithExtensions
        self.name = getPurePackageName(nameWithExtensions)

    def getDir(self):
        return os.path.join(self.workingDir,self.name)

    def installedGlobally(self):
        return isPackageInstalledGlobally(self)

    def installWithDependencies(self, ignoreGlobal=False):
        #install or update the current package
        self.installOrUpdate(ignoreGlobal)
        #get all dependencies
        dependencies = self.getPackageDependencies(dependencyDir+'/'+package)
        print("DEPENDENCIES: {0}".format(dependencies))
        for dependency in dependencies:
            dependency.installWithDependencies(ignoreGlobal)


    def installOrUpdate(self, ignoreGlobal=False):
        #check if it is installed globally
        if not ignoreGlobal and installedGlobally:
            print(self.name + " already installed globally, you might have to update it manually")
            return
        #set the url
        self.setUrl(package_manager.getPackageUrlFromName(package))
            #check if a url was set
        if self.url == None or len(self.url)==0:
            print('Package not found: '+package)
            sys.exit(1)

        ###get current source
        #create path
        os.makedirs(workingDir, exist_ok=True)
        myDir = self.getDir()
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
            else : 
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
            print('handle local package: ' +packageName)
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
        return os.path.join(self.packageDir,'lms_package.json')

    def getPackageDependencies(self):
        res = list()
        packageFile = self.getPackageFilePath()
        if not os.path.isdir(self.packageDir):
            print('package does not exist: ' + self.getDir())
            return
        if not os.path.isfile(packageFile):
            print('lms_package.json does not exist in: ' + self.getDir())
            return
        packageData = parseJson(packageFile) #TODO error handling
        if 'dependencies' in packageData:
            names = packageData['dependencies']
            for tmp in names:
                res.append(Package(tmp,self.workingDir)
            return res
        return res

    #returns a list with all binaries that have to be linked
    def getPackageTargets(self):
        packageFilePath = self.getPackageFilePath()
        json = parseJson(packageFilePath)
        if 'targets' in json:
            return json['targets']
        targets = list()
        targets.append(packageName)
        return targets


    def getPackageIncludes(packageDir, absPath=True):
        packageFilePath = self.getPackageFilePath()
        json = parseJson(packageFilePath)
        if 'includes' in json:
            includes = json['includes']
        else:
            includes = list()
            includes.add('include')
            
        result = list()
        for include in includes:
            if absPath:
                result.append(os.path.abspath(self.packageDir+'/'+include))
            else:
                result.append(include)
        return result
