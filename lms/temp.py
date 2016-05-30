
#Jetzt holen wir uns zu jedem package die passende URL
#TODO version fehlt noch, wir splitten am ersten:
#TODO es fehlt noch die überprüfung ob manche packages mehrfach mit anderen URLs definiert wurden
#neededPackages = parseFrameworkXml('framework_conf.xml')
+packagesData = parsePackageList('packagelist.json')

+packages = getNeededPackageUrls(neededPackages,packagesData);
+print(packages)
#Nun müssen wir prüfen was es für eine url ist
for package in packages:
    url = packages[package]
    if isGitUrl(url):
        print('git url: '+url)
        #TODO wir downloaden das repo
    else :
        print("No valid url given for " +package + " url: " + url)

#Nun haben wir alle benötigten packages
#Fragen zu klären: 
#1. Wohin mit den externen daten?

#2. Was machen wir mit lokalen?

#Ordnerstruktur:
# config_repo
# - configs
# - dependencies

#zu 1. wir laden es in den dependencies ordner runter
#zu 2. wir erstellen einen hardlink

