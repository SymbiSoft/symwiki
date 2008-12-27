# symwiki.py: Simple personal wiki for S60 Ed.3 smartphones
# 
# Copyright (C) Dmitri Brechalov, 2008
#
# Project URL: http://code.google.com/p/symwiki/
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
import sys
import re

#### in case the program runs as a script
sys.path.append('C:\\Python')
sys.path.append('E:\\Python')

from utils import *
from xtext import xText

UID = u"e3e34da3"
VERSION = '0.1'

class WikiEditor(xText):
    version = VERSION
    title = u('SymWiki %s' % (version))
    frontpage = 'Home'
    def __init__(self):
        xText.__init__(self)
        self.history = list()
        self.wikidir = 'E:/Wiki'

    def openPage(self, name):
        if self.fname is not None:
            self.doSave()
        appuifw2.app.title = u(name)
        self.fname = os.path.join(self.wikidir, name)
        if not os.path.exists(self.fname):
            fn = open(self.fname, 'w')
            if name != self.frontpage:
                backlink = '[[%s]]\n' % self.frontpage
            else:
                backlink = ''
            fn.write('%s\n%s' % (name, backlink))
            fn.close()
        self.doOpen()

    def findLink(self):
        '''Search the [[link]] around cursor
        Return u"text" of the link or None
        '''
        pos = self.editor.get_pos()
        m = re.search('\\[\\[([^]]*)$', self.editor.get(0, pos))
        if not m:
            return None
        lpos = pos - len(m.group(1))
        m = re.search('^([^[]*?)\\]\\]', self.editor.get(pos))
        if not m:
            return None
        rpos = pos + len(m.group(1))
        txt = self.editor.get(lpos, rpos-lpos)
        return s(txt)
        
    def insertLink(self):
        link = appuifw2.query(u('Link'), 'text')
        if link is not None:
            self.editor.add(u('[[%s]]') % link)
    
    def clickEvent(self):
        txt = self.findLink()
        if txt is not None:
            self.openPage(txt)

    def quit(self):
        self.doSave()
        self.app_lock.signal()
        if appuifw2.app.uid() == UID:
            appuifw2.app.set_exit() # running as app

    def run(self):
        self.app_lock = e32.Ao_lock()
        if not os.path.exists(self.wikidir):
            os.mkdir(self.wikidir)
        self.openPage(self.frontpage)
        appuifw2.app.menu = [
            (u("Insert link"), self.insertLink),
            (u("Edit"), ((u("Undo"), self.undo),
                         (u("Cut"), self.cut),
                         (u("Copy"), self.copy),
                         (u("Paste"), self.paste),
                         (u("Select All"), self.selectAll),
                         (u("Select None"), self.selectNone))),
            (u("Search"), ((u("Find Forward"), self.findTextForward),
                           (u("Find Backward"), self.findTextBackward),
                           (u("Replace"), self.replaceText))),
            (u("About"), self.dummy),
            (u("Exit"), self.quit)
            ]
        self.bindExitKey((u('Back'), self.dummy))
        self.bindSelectKey(self.clickEvent)
        self.editor.has_changed = False
        e32.ao_yield()
        appuifw2.app.body = self.editor

        old_exit_key_text = appuifw2.app.exit_key_text
        old_menu_key_text = appuifw2.app.menu_key_text
        appuifw2.app.menu_key_text = u("Options")
        self.rebindFunKeys()
        self.app_lock.wait()
        appuifw2.app.exit_key_text = old_exit_key_text

if __name__ == '__main__':
    editor = WikiEditor()
    editor.run()
