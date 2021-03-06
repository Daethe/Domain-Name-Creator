#!/usr/bin/python
import subprocess
import os
import getpass
from gi.repository import Gtk
from LangLoader import LangLoader

class AddDomain(object):

    windowAdd = False
    progressValue = 0.0

    componentName = ["title", "title", "title", "title", "iDesc1", "iDesc2", "domainLbl", "iDesc3", "cDesc1", "cDesc2"]
    component     = []

    def getAddDomain(this):
        mdi = Gtk.Builder()
        mdi.add_from_file('interface/addDomain.glade')

        this.windowAdd = mdi.get_object("addDomain")
        this.windowAdd.domainName = mdi.get_object("informationDomain_domainName")
        this.windowAdd.log = mdi.get_object("progressDomain_log")
        this.windowAdd.progress = mdi.get_object("progressDomain_progress")

        this.component = LangLoader().initVarForLang("langAdd", mdi, this.componentName)

        this.windowAdd.show_all()
        mdi.connect_signals(AddHandler(this.windowAdd))

class AddHandler(AddDomain):

    def __init__(self, window):
        self.window = window

    def destroy(self, *args):
        self.window.destroy()

    def prepare(self, w, new_page):
    	cur = self.window.get_current_page()
    	if cur == 1:
    		self.window.domainName.connect('changed', self.domainName_changed, cur)
    	elif cur == 2:
            self.createDomain()
            self.complete(cur)
        elif cur == 3:
            self.complete(cur)

    def complete(self, stepNumber):
	    self.window.set_page_complete(self.window.get_nth_page(stepNumber), True)

    def domainName_changed(self, w, uParam):
        self.domainNameText = self.window.domainName.get_text()
        self.complete(uParam)

    def createDomain(self):
        self.step(["mkdir", "-p", "/var/www/" + self.domainNameText + "/public_html"], True, "Creation des dossiers")
        self.step(["mkdir", "-p", "/var/www/" + self.domainNameText + "/logs"], False, "")
        self.window.log.set_text("Ajout de la page d'exemple")
        self.createDomain_file("file", "/var/www/" + self.domainNameText + "/public_html/index.html", "<html><head><title>Welcome to " + self.domainNameText + "!</title></head><body><h1>Success!  The " + self.domainNameText + " virtual host is working!</h1></body></html>")
        self.progressValue = self.progressValue + 0.1
        self.window.progress.set_fraction(self.progressValue)
        self.window.log.set_text("Configuration de l'hote virtuel")
        self.createDomain_file("file", os.path.dirname(__file__) + "/vhosts/" + self.domainNameText + ".conf", "<VirtualHost *:80>" + "\nServerName " + self.domainNameText + "\nServerAlias www." + self.domainNameText + "\nServerAdmin admin@" + self.domainNameText + "\nDocumentRoot /var/www/" + self.domainNameText + "/public_html/ \nErrorLog /var/www/" + self.domainNameText + "/logs/error.log \nCustomLog /var/www/" + self.domainNameText + "/logs/access.log combined \n</VirtualHost>")
        self.progressValue = self.progressValue + 0.1
        self.window.progress.set_fraction(self.progressValue)
        self.step(["cp", os.path.dirname(__file__) + "/vhosts/" + self.domainNameText + ".conf", "/etc/apache2/sites-available/" + self.domainNameText + ".conf"], False, "")
        self.step(["a2ensite", self.domainNameText + ".conf"], True, "Activation de l'hote virtuel")
        self.step(["service", "apache2", "restart"], True, "Redemarrage du service apache")
        self.step(["chown", "-R", getpass.getuser() + ":" + getpass.getuser(), "/var/www/" + self.domainNameText + "/public_html"], True, "Ajout des permissions utilisateurs")
        self.step(["chmod", "-R", "755", "/var/www/"], False, "")
        self.step(["cp", "/etc/hosts", os.path.dirname(__file__) + "/backup/hosts"], True, "Ajout de la configuration au fichier hosts")
        self.createDomain_file("hostsAndData", "/etc/hosts", "127.0.0.1 " + self.domainNameText)
        self.createDomain_file("hostsAndData", os.path.dirname(__file__) + "/data/domain.dnc", self.domainNameText)
        self.window.log.set_text("Nom de domaine pret a l'emploi")

    def createDomain_file(self, forFile, path, data):
        data2 = ""
        if (forFile == "hostsAndData"):
            for line in open(path, "r").readlines():
                data2 = data2 + line
        fo = open(path, "w")
        fo.write(data2 + data)
        fo.close()

    def step(self, command, withText, text):
        if (withText):
            self.window.log.set_text(text)
        subprocess.call(command)
        self.progressValue = self.progressValue + 0.1
        self.window.progress.set_fraction(self.progressValue)
