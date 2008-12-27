# utils.py: Useful utilities for Pys60 programs
# 
# Copyright (C) Dmitri Brechalov, 2008
#
# Project URL: http://code.google.com/p/s60htmled/
# 
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.

import appuifw2
import e32
import key_codes
import os

u = lambda s: s.decode('utf-8')
s = lambda s: s.encode('utf-8')

schedule = appuifw2.schedule

def fileBrowser(label, dironly=False, dirname=''):
    isdir = lambda fname: os.path.isdir(os.path.join(dirname, fname))
    isfile = lambda fname: not os.path.isdir(os.path.join(dirname, fname))
    markdir = lambda fname: fname + '/'
    def chkdir(d):      # os.path uses '/' as a dir separator but os.path.join
        d = s(d)        # adds no '/' between drive name and file path
        if not (d.endswith('/') or d.endswith('\\')):
            return d + '/'      # content handler return an error when there is
        else:                   # no separator after drive name
            return d
    while True:
        if not dirname:
            items = map(chkdir, e32.drive_list())
        else:
            lst = os.listdir(dirname)
            dirs = map(markdir, filter(isdir, lst))
            dirs.sort()
            if not dironly:
                files = filter(isfile, lst)
                files.sort()
            else:
                files = []
            items = ['..'] + dirs + files
        ans = appuifw2.popup_menu(map(u, items), u(label))
        if ans is None: return None
        fname = items[ans]
        if fname == '..':
            return fname
        fname = os.path.join(dirname, fname)
        if os.path.isdir(fname):
            ans = fileBrowser(fname, dironly, fname)
            if ans != '..': return ans
            if dironly and ans == '..': return fname
        else:
            return fname

# end of utils.py
