#! /usr/bin/env python

# Davinci Resolve 12 and above Disk Database project backup utility.
# Igor Ridanovic, HDhead.com

import os
import sys
import getpass
import time
from shutil import make_archive
from datetime import datetime
import tkMessageBox

#---- User Configuration ----

# User set number of minutes between backups
interval = 120

# Delete backups older than maxDays
maxDays = 30

#---- End of User configuration ----

# Report error and exit
def errorwindow(report):
	tkMessageBox.showinfo('Resolve Project Backup', report)
	sys.exit(report)

sleeptime = interval * 60
version = 1.1
currentUser = getpass.getuser()

# Determine the host operating system and set OS specific variables
hostOS = sys.platform

# Windows
if hostOS == 'win32':
	eol = '\r\n'
	sourcePath = 'C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Resolve Disk Database\Resolve Projects'
	destPath = os.path.join('C:\Users', currentUser, 'Documents\ResolveProjectBackup')

# OS X
elif hostOS == 'darwin':
	eol = '\n'
	sourcePath = '/Library/Application Support/Blackmagic Design/DaVinci Resolve/Resolve Disk Database/Resolve Projects'
	destPath = os.path.join('/Users', currentUser, 'Documents/ResolveProjectBackup')

# We assume Linux host unless Windows or OS X.
# Tkinter is not included in CentOS 7.3. Use yum install tkinter.
else:
	eol = '\n'
	sourcePath = '/opt/resolve/Resolve Disk Database/Resolve Projects'
	destPath = os.path.join('/home', currentUser, 'Documents/ResolveProjectBackup')

def wincompliance(ts):
	"""remove space and colons from timestamp for Windows compliance"""
	noSpace = 'T'.join(ts.split())
	noColon = '-'.join(noSpace.split(':'))
	return noColon

# Verify if paths are valid. Create destination directory if missing.
if not os.path.isdir(sourcePath):
	errorwindow('The Resolve disk database root is not found at ' + sourcePath)
if not os.path.isdir(destPath):
	os.makedirs(destPath)

# Create log file if missing or open if exists
logName = 'ResolveBackup.log'
logPath = os.path.join(destPath, logName)
if not os.path.isfile(logPath):
	logfile = open(logPath, 'w')
	logfile.write('Resolve Disk Database Backup Tool V%s. HDhead.com' %version)
	logfile.write(eol)
	logfile.close()

# Infinite backup loop
while True:

	# Create backup
	timeStamp = str(datetime.now())[:-7]
	backupName = 'ResolveProjBackup_' + wincompliance(timeStamp)
	savePath = os.path.join(destPath, backupName)
	make_archive(savePath, 'zip', sourcePath)

	# Write a log entry
	logfile = open(logPath, 'a')
	logfile.write('Created %s.zip'%backupName)
	logfile.write(eol)
	logfile.close()
	
	# Remove old backups
	now = time.time()
	for filename in os.listdir(destPath):
		if filename.endswith('zip') == True:
			deleteFile = os.path.join(destPath, filename)
			timeStamp  = os.stat(deleteFile).st_mtime
			if maxDays + 1< (now - timeStamp) / 86400: # x/86400 converts seconds to days
				os.remove(deleteFile)

	time.sleep(sleeptime)


