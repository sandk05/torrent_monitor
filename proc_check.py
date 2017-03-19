#!/usr/bin/python
import re
import subprocess
import psutil
import time
import os
import sys
import shutil
from stat import *
def isRunning():
    "This checks if the requested process is running"
    for proc in psutil.process_iter():
         process = psutil.Process(proc.pid)
         pname = process.name()
         if pname == "qbittorrent":
              return True
    return False
         

def getLocalPath ( qb ):
    "This gets the path in which downloads are saved "
    preference = qb.preferences()
    return preference['save_path']

def getInprogressDownloads( qb ):
    "Check if any download is in progress"
    inProgress = qb.torrents(filter='downloading')
    if inProgress:
         return True;
    isStalled  = qb.torrents(filter='stalled')
    if isStalled:
         return True;

    return False;

def getHashList( qb ):
    "Get the hash list of Seeding Downloads"
    hash_list = list()
    completed = qb.torrents(filter='seeding')
    if completed:
         for torr in completed:
              hash_list.append(torr['hash'])
    return hash_list;
def getNameList( qb ):
    name_list = list()
    completed = qb.torrents(filter='seeding')
    if completed:
         for torr in completed:
              name_list.append(torr['name'])
    return name_list;
         
if __name__ == "__main__":
    status = isRunning()
    if status:
         print "qbittorrent is running"
    else:
         print "qbittorrent is not running"
         p = subprocess.Popen(["qbittorrent", "&" ])
         time.sleep(10);
    
    from qbittorrent import Client
    qb = Client('http://127.0.0.1:8080/')
    qb.login('admin','Pass@1234')

    shouldContinue = getInprogressDownloads(qb)
    done_list = getHashList(qb)
    name_list = getNameList(qb)
    path = getLocalPath(qb)

    if done_list:
         print "path %s " %path
         print "Hash to delete are "
         for name in name_list:
              print name;
         for did in done_list:
              print did;
     

    if done_list:
         DEST_DIR = "/media/sandeep/My Passport/";
         if os.path.isdir(DEST_DIR):
              os.chdir(path)
              DIR = os.getcwd();
              for name in name_list:
                   pathname = os.path.join(DIR,name)
                   if not os.path.exists(pathname):
                        continue
                   mode = os.stat(pathname)[ST_MODE]
                   if S_ISDIR(mode):
                        print 'Is A Directory'
                   elif S_ISREG:
                        print 'Is A Regular File'
                        extention = os.path.splitext(name)[1]
                        filename  = os.path.splitext(name)[0]
                        size      = filename.rsplit(None, 1)[-1]
                        eType     = filename.rsplit(None, 2)[-2]
                        rType     = filename.rsplit(None, 3)[-3]
                        Language  = filename.rsplit(None, 4)[-4]+"/"
                        year      = filename.rsplit(None, 5)[-5]
                        fName     = re.search('%s(.*)%s' %("-", year),name).group(1).strip('()').strip()
                        cName     = fName+extention
                        DEST_FOLDER = DEST_DIR+"Movies/"+Language+fName
                        if not os.path.exists(DEST_FOLDER):
                             os.makedirs(DEST_FOLDER)
                        DEST      = DEST_FOLDER+cName
                        print "FROM " +pathname +" TO "  +DEST
                        shutil.move(pathname,DEST) 
                   else:
                        print 'Skipping %s' % pathname
         qb.delete(done_list)
         qb.logout()
    if not shouldContinue:
         print "No Download In Progress Exiting qbittorrent and monitor script"
         qb.shutdown();
         sys.exit()
    print "Some Downloads are in progress will recheck after 10 mins"
    time.sleep(600)
