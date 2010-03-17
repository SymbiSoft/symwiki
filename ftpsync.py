# -*- coding: utf-8; -*-
# ftpsync.py: simple ftp synchronization

import sys
import os
if sys.platform == 'symbian_s60':
    sys.path.append('E:\\Python')
    cfgpath = 'E:\\Python'
else:
    cfgpath = os.path.split(sys.argv[0])[0]

from ftplib import FTP

def getRList(ftp, rdir):
    '''Return a dictionary with contents of the remote directory rdir
    each element is {'filename': time}
    where size is int in bytes, time is str in format: "YYYY-MM-DD HH:MM"
    '''
    result = dict()
    ftp.cwd(rdir)
    for fn in ftp.nlst():
        if fn.startswith('.'): continue # skip . and ..
        response = ftp.sendcmd('MDTM ' + fn)
        try:
            rc, timestamp = response.split(' ', 1)
        except:
            timestamp = '0' * 14
        result[fn] = timestamp
    return result

def getLList(ldir):
    '''Return a list with contents of the local directory ldir
    each element is {'filename': time}
    where size is int in bytes, time is str in format: "YYYY-MM-DD HH:MM"
    '''
    import time
    result = dict()
    for fname in os.listdir(ldir):
        stat = os.stat(os.path.join(ldir, fname))
        ftime = time.strftime('%Y%m%d%H%M%S', time.gmtime(stat.st_mtime))
        result[fname] = ftime
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
            ldate = llst[fname]
        except KeyError:
            result[fname] = 'D' # no file in local dir
            continue
        try:
            rdate = rlst[fname]
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
        print fname, '\t', data[fname]

def readConfig():
    cfgname = 'ftp.cfg'
    cfgfile = os.path.join(cfgpath, cfgname)
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
    buf = list()
    save = lambda line: fd.write('%s\n' % line)
    ftp.cwd(rdir)
    ftp.retrlines('RETR ' + fname, buf.append)
    fd = open(os.path.join(ldir, fname), 'w')
    fd.write('\n'.join(buf))
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
    print 'Remote dir:'
    printList(rlst)
    ldir = cfg['local']
    llst = getLList(ldir)
    print 'Local dir:'
    printList(llst)
    dl = diffLists(llst, rlst)
    fnames = dl.keys()
    fnames.sort()
    print
    print 'Syncing...'
    for fname in fnames:
        try:
            sltime = llst[fname]
        except KeyError:
            sltime = '0' * 14
        try:
            srtime = rlst[fname]
        except KeyError:
            srtime = '0' * 14
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
