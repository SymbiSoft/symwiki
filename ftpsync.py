# -*- coding: utf-8; -*-
# ftpsync.py: simple ftp synchronization

import sys
import os
sys.path.append('E:\\Python')

from ftplib import FTP

def parseline(data):
    '''Parse line of FTP.dir output and return tuple (filename, size, time)
    '''
    months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
    import time
    year = time.localtime()[0]
    fields = data.split()
    size = int(fields[4])
    sm = fields[5]
    month = 0
    for i in range(len(months)):
        if sm == months[i]:
            month = i + 1
    day = int(fields[6])
    time = fields[7]
    if time.find(':') < 0:
        year = time
        time = '00:00'
    date = '%4s-%02i-%02i %s' % (year, month, day, time)
    name = fields[8]
    return (name, size, date)

def getRList(ftp, rdir):
    '''Return a dictionary with contents of the remote directory rdir
    each element is {'filename': (size, time)}
    where size is int in bytes, time is str in format: "YYYY-MM-DD HH:MM"
    '''
    result = dict()
    def callback(x):
        item = parseline(x)
        if not item[0].startswith('.'):
            fdata = parseline(x)
            result[fdata[0]] = fdata[1:]
    ftp.dir(rdir, callback)
    return result

def getLList(ldir):
    '''Return a list with contents of the local directory ldir
    each element is {'filename': (size, time)}
    where size is int in bytes, time is str in format: "YYYY-MM-DD HH:MM"
    '''
    import time
    result = dict()
    for fname in os.listdir(ldir):
        stat = os.stat(os.path.join(ldir, fname))
        fsize = stat.st_size
        ftime = time.strftime('%Y-%m-%d %H:%M', time.gmtime(stat.st_mtime))
        result[fname] = (fsize, ftime)
    return result

def diffLists(llst, rlst):
    '''Return a list with files need to sync:
    {'filename': 'U' or 'D'} 'U' means the file needs to be uploaded to
    remote dir, 'D' means the file needs to be downloaded to local dir
    '''
    result = dict()
    allfiles = llst.keys()
    for f in rlst.keys():
        if f not in allfiles: allfiles.append(f)
    for fname in allfiles:
        try:
            ldate = llst[fname][1]
        except KeyError:
            result[fname] = 'D' # no file in local dir
            continue
        try:
            rdate = rlst[fname][1]
        except KeyError:
            result[fname] = 'U' # no file in remote dir
            continue
        if ldate < rdate:
            result[fname] = 'D'
        elif ldate > rdate:
            result[fname] = 'U'
    return result

def printList(data):
    fnames = data.keys()
    fnames.sort()
    for fname in fnames:
        print fname, '\t', data[fname][0], '\t', data[fname][1]

def readConfig():
    cfgname = 'ftp.cfg'
    cfgpath = os.path.split(sys.argv[0])[0]
    cfgfile = os.path.join(cfgpath, cfgname)
    try:
        cfg = open(cfgfile, 'r')
    except:
        cfgfile = 'E:\\Python\\' + cfgname # temp workaround for s60
        cfg = open(cfgfile, 'r')
    result = dict()
    for line in cfg.readlines():
        line = line.strip()
        if not line or line.startswith('#'): continue
        try:
            k, v = line.split('=', 1)
        except:
            print 'Wrong file format:', line
            sys.exit(1)
        result[k.strip()] = v.strip()
    return result

def downloadFile(ftp, ldir, rdir, fname):
    fd = open(os.path.join(ldir, fname), 'w')
    save = lambda line: fd.write('%s\n' % line)
    ftp.cwd(rdir)
    ftp.retrlines('RETR ' + fname, save)
    fd.close()

def uploadFile(ftp, ldir, rdir, fname):
    fd = open(os.path.join(ldir, fname), 'r')
    ftp.cwd(rdir)
    ftp.storlines('STOR ' + fname, fd)
    fd.close()

if __name__ == '__main__':
    cfg = readConfig()
    ftp = FTP(cfg['host'])
    ftp.login(cfg['login'], cfg['password'])
    rdir = cfg['remote']
    rlst = getRList(ftp, rdir)
    ldir = cfg['local']
    llst = getLList(ldir)
    dl = diffLists(llst, rlst)
    fnames = dl.keys()
    fnames.sort()
    print
    print 'Syncing...'
    for fname in fnames:
        try:
            sltime = llst[fname][1]
        except KeyError:
            sltime = 'missing'
        try:
            srtime = rlst[fname][1]
        except KeyError:
            srtime = 'missing'
        print fname, 'L:', sltime, 'R:', srtime,
        if dl[fname] == 'U':
            uploadFile(ftp, ldir, rdir, fname)
            print '- uploaded'
        elif dl[fname] == 'D':
            downloadFile(ftp, ldir, rdir, fname)
            print '- downloaded'
        else:
            print dl[fname], 'mode is not implemented yet'
    ftp.close()
    print 'Done.'
