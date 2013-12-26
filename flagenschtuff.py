#!/usr/bin/python

import os
import subprocess
import appindicator
import threading
import gtk
import re
import sys
import sched
import time

scheduler = sched.scheduler(time.time, time.sleep)

def get_ip(): 
	try:
		ip = subprocess.check_output('ifconfig |\
			pcregrep -oM "(?<=tun0).*\n\s*inet addr:\s*((?:[0-9]{1,3}\.){3}[0-9]{1,3})" |\
			pcregrep -o "(?:[0-9]{1,3}\.){3}[0-9]{1,3}"', shell=True)
	except subprocess.CalledProcessError:
		print "Could not get tun0 ip. Are you connected?"
		sys.exit(0)

	return ip.strip()

def get_loc(ip):
	loc = subprocess.check_output('geoiplookup {0}'.format(ip), shell=True)
	code = re.search(':\s([A-Z]{2}),', loc.strip()).group(1)
	return code.lower()

def get_icon(loc):
	return os.path.abspath("./img/{0}.png".format(loc))

def get_country(ip):
	loc = subprocess.check_output('geoiplookup {0}'.format(ip), shell=True)
	country_name = re.search(':\s[A-Z]{2},\s([A-Za-z\s]+)', loc.strip()).group(1)
	return country_name

class IPIndicator:
	def __init__(self):
		self.ip = get_ip()		
		loc = get_loc(self.ip)		
		icon = get_icon(loc)

		self.ind = appindicator.Indicator("flagenschtuff", icon, 
			appindicator.CATEGORY_APPLICATION_STATUS)		
		self.ind.set_status(appindicator.STATUS_ACTIVE)				
		self.update()
		self.ind.set_menu(self.setup_menu())
	
	def setup_menu(self):
		menu = gtk.Menu()				
		self.info = gtk.MenuItem("info")
		
		label = self.get_info_label()
		self.info.set_label(label)		
		
		self.info.set_sensitive(False)
		self.info.show()
		menu.append(self.info)

		refresh = gtk.MenuItem("Refresh")
		refresh.connect("activate", self.on_refresh)
		refresh.show()
		menu.append(refresh)

		return menu

	def update(self):
		"""
		
		Update the IP address.
		
		"""
		ip = get_ip()
		if ip != self.ip:
			self.ip = ip
			loc = get_loc(ip)
			icon = get_icon(loc)
			
			label = self.get_info_label()
			self.info.set_label(label)
			self.ind.set_icon(icon)

	def get_info_label(self):
		country = get_country(self.ip);
		return "{0} - {1}".format(self.ip, country)

	def on_refresh(self, widget):
		self.update()


if __name__ == "__main__":
	i = IPIndicator()
	gtk.main()