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
VERSION = '0.2'

class WikiEditor(xText):
    version = VERSION
    title = u('SymWiki')
    frontpage = 'Home'
    def __init__(self):
        xText.__init__(self)
        self.history = list()
        self.wikidir = 'E:/Wiki'

    def openPage(self, name, noHistory=False):
        if self.fname is not None:
            self.doSave()
            if not noHistory:   # do not add to history if going back
                self.history.append(self.fname)
        appuifw2.app.title = u('%s - %s') % (self.title, name)
        self.fname = os.path.join(self.wikidir, name)
        if not os.path.exists(self.fname):
            fn = open(self.fname, 'w')
            if name == self.frontpage:
                txt = '''Welcome to SymWiki - your personal Wiki on S60 device!

This is a Home page, the main page of the Wiki. Replace its contents with your own.

To insert link to another page press *Options*, select *Insert link* and type the name of the page.

To open a link put the cursor on the link between double brackets and press *Select* button.
'''
            else:
                txt = ''
            fn.write(txt)
            fn.close()
        self.doOpen()

    def goBack(self):
        try:
            name = self.history.pop()
            self.openPage(name, True)
        except IndexError:
            appuifw2.note(u('No previous page available!'))

    def goHome(self):
        self.openPage(self.frontpage)
        
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
        link = appuifw2.query(u('Page name'), 'text')
        if link is not None:
            self.editor.add(u('[[%s]]') % link)
    
    def clickEvent(self):
        txt = self.findLink()
        if txt is not None:
            self.openPage(txt)

    def aboutDlg(self):
        appuifw2.query(u('SymWiki\nVersion %s\n(C) Dmitri Brechalov, 2008' % (self.version)), 'query', ok=u(''), cancel=u('Close'))

    def quit(self):
        self.doSave()
        self.app_lock.signal()
        if appuifw2.app.uid() == UID:
            appuifw2.app.set_exit() # running as app

    def run(self):
        self.app_lock = e32.Ao_lock()
        if not os.path.exists(self.wikidir):
            os.mkdir(self.wikidir)
        self.goHome()
        appuifw2.app.menu = [
            (u("Insert link"), self.insertLink),
            (u("Home page"), self.goHome),
            (u("Edit"), ((u("Undo"), self.undo),
                         (u("Cut"), self.cut),
                         (u("Copy"), self.copy),
                         (u("Paste"), self.paste),
                         (u("Select All"), self.selectAll),
                         (u("Select None"), self.selectNone))),
            (u("Search"), ((u("Find Forward"), self.findTextForward),
                           (u("Find Backward"), self.findTextBackward),
                           (u("Replace"), self.replaceText))),
            (u("About"), self.aboutDlg),
            (u("Exit"), self.quit)
            ]
        self.bindExitKey((u('Back'), self.goBack))
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
