import os
import shutil
import sys

workdir = sys.argv[1]
print 'making new work directory', workdir
os.makedirs(workdir+'/output')
os.makedirs(workdir+'/patients')
print 'copying settings from settings'
shutil.copytree('settings', workdir+'/settings')
