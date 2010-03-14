# symwiki.py: Simple personal wiki for S60 Ed.3 smartphones
# -*- coding: utf-8 -*-
# 
# Copyright (C) Dmitri Brechalov, 2009
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
VERSION = '1.5.1'

ParaChar = u"\u2029"

class WikiEditor(xText):
    version = VERSION
    title = u('SymWiki')
    frontpage = 'Home'
    def __init__(self):
        xText.__init__(self)
        self.history = list()
        self.wikidir = 'E:/Wiki'
        self.page = ''

    def saveHistory(self):
        self.history.append((self.page, self.editor.get_pos()))
        self.setExitKeyText()

    def __fileName(self, name):
        '''Return full filename for the page name
        '''
        return os.path.join(self.wikidir, name.lower().replace(' ', '-')) + '.txt'

    def doSave(self):
        if len(self.editor.get()) > 0:
            if self.editor.has_changed:
                xText.doSave(self)
        else:                   # empty file - remove
            os.remove(self.fname)

    def openPage(self, name, pos=0, noHistory=False):
        if self.fname is not None:
            self.doSave()
            if not noHistory:   # do not add to history if going back
                self.saveHistory()
        appuifw2.app.title = u('%s - %s') % (self.title, u(name))
        fname = self.__fileName(name)
        if fname != self.fname:
            self.fname = fname
            self.page = name
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
            self.setExitKeyText()
            self.doOpen()
        self.editor.set_pos(pos)

    def goBack(self):
        try:
            (name, pos) = self.history.pop()
            self.openPage(name, pos, True)
        except IndexError:
            self.quit()

    def goHome(self):
        self.openPage(self.frontpage)

    def setExitKeyText(self):
        if len(self.history) == 0:
            txt = u('Exit')
        else:
            txt = u('Back')
        appuifw2.app.exit_key_text = txt
        self.bindExitKey((txt, self.goBack), (u('Insert'), self.insertWikiSyntax))

    def moveMenu(self):
        self.rebindFunKeys()
        ans = appuifw2.popup_menu([
                u('Section'),
                u('Top'),
                u('Bottom'),
                u('Goto line')])
        if ans is not None:
            if ans == 0:
                self.listHeadings()
            elif ans == 1:
                schedule(self.moveCursor, 0, appuifw2.EFNoMovement)
            elif ans == 2:
                schedule(self.moveCursor, len(self.editor.get()), appuifw2.EFNoMovement)
            elif ans == 3:
                schedule(self.gotoLine)
        self.moveEvent()
        
    def findLink(self):
        '''Search the [[link|label]] around cursor
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
        txt = s(self.editor.get(lpos, rpos-lpos))
        try:
            link, label = txt.split('|', 1)
        except:
            link = txt
        return link

    def findNextLink(self):
        self.doFind(u('[['))
        
    def insertMarkup(self, markup, prompt=''):
        (pos, anchor, text) = self.editor.get_selection()
        if not text:
            if prompt:
                text = appuifw2.query(u(prompt), 'text')
                if text is None: return
            else:
                text = ''
        if markup.find('%s') > 0:
            text = u(markup) % (text)
        else:
            text = u(markup)
        if pos > anchor:
            pos, anchor = anchor, pos
        self.editor.delete(pos, anchor-pos)
        self.editor.set_pos(pos)
        self.editor.add(text)

    def insertCustomMarkup(self):
        text = appuifw2.query(u('Text to insert:'), 'text')
        if text is None: return
        self.insertMarkup(s(text))

    def insertLink(self):
        self.insertMarkup('[[%s]]', 'Page name')

    def insertWikiSyntax(self):
        markup = (
            # (Label,            Markup)
            ('Link',            self.insertLink),
            ('Bold',            '**%s**'),
            ('Italic',          '//%s//'),
            ('Underlined',      '__%s__'),
            ('Preformated',     '{{{%s}}}'),
            ('List unord.',     '* '),
            ('List ordered',    '# '),
            ('Header 1',        '= %s'),
            ('Header 2',        '== %s'),
            ('Header 3',        '=== %s'),
            ('Header 4',        '==== %s'),
            ('Header 5',        '===== %s'),
            ('Header 6',        '====== %s'),
            ('Image',           '{{%s}}'),
            ('Horizontal rule', '\n----\n'),
            ('Line break',      r'\\'),
            ('Custom...',       self.insertCustomMarkup),
            )
        labels = map(lambda x: u(x[0]), markup)
        data = map(lambda x: x[1], markup)
        ans = appuifw2.selection_list(labels, 1)
        if ans is None: return
        selected = data[ans]
        if callable(selected):
            selected()
        else:
            self.insertMarkup(selected)
        
    def insertNewlineAndIndent(self):
        def getCurrentLine():
            pos = self.editor.get_pos()
            txt = self.editor.get()[:pos]
            # look for the start of line
            i = pos-1
            while i >= 0 and txt[i] != ParaChar:
                i -= 1
            return txt[i+1:]
        line = getCurrentLine()
        indentchars = u''
        mo = re.match(u'^([#* ]+ )', line)
        if mo is not None:
                indentchars += mo.group(1)
        self.editor.add(ParaChar+indentchars)

    def clickEvent(self):
        txt = self.findLink()
        if txt is not None:
            try:
                pagename, anchor = txt.split('#')
            except:
                pagename = txt
                anchor = None
            self.openPage(pagename)
        else:
            self.insertNewlineAndIndent()

    def __getPageList(self):
        lst = os.listdir(self.wikidir)
        lst = [ os.path.splitext(item)[0] for item in lst ]
        lst.sort()
        return lst

    def listPages(self):
        lst = self.__getPageList()
        ans = appuifw2.selection_list(map(u, lst), 1)
        if ans is None or ans not in range(len(lst)): return
        fname = lst[ans]
        self.openPage(fname)

    def __doSearch(self, text):
        result = list()
        for pname in self.__getPageList():
            fname = self.__fileName(pname)
            if open(fname, 'r').read().find(text) >= 0:
                result.append(pname)
        return result

    def searchPages(self):
        ans = appuifw2.query(u("Search text"), "text", self.find_text)
        if ans is None: return
        self.find_text = ans
        lst = self.__doSearch(s(ans))
        ans = appuifw2.selection_list(map(u, lst), 1)
        if ans is None or ans not in range(len(lst)): return
        fname = lst[ans]
        self.openPage(fname)

    def listHeadings(self):
        ln = list()
        lp = list()
        txt = self.editor.get()
        count = 1
        for mo in re.finditer(u'(^|\u2029)(=+)(.+?)=*($|\u2029)', txt):
            n = len(mo.group(2)) - 1
            hdr = u'  ' * n + mo.group(3).strip()
            ln.append(hdr)
            lp.append(mo.start())
            count += 1
        ans = appuifw2.selection_list(ln, 1)
        if ans is None: return
#         self.saveHistory()
        pos = lp[ans]
        self.editor.set_pos(pos+1)

    def aboutDlg(self):
        appuifw2.query(u('SymWiki\nVersion %s\n(C) Dmitri Brechalov, 2009' % (self.version)), 'query', ok=u(''), cancel=u('Close'))

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
            (u('Home'), self.goHome),
            (u("Pages"), self.listPages),
            (u("Edit"), ((u("Undo"), self.undo),
                         (u("Cut"), self.cut),
                         (u("Copy"), self.copy),
                         (u("Paste"), self.paste),
                         (u("Select All"), self.selectAll),
                         (u("Select None"), self.selectNone))),
            (u("Search"), ((u("Search Pages"), self.searchPages),
                           (u("Find Forward"), self.findTextForward),
                           (u("Find Backward"), self.findTextBackward),
                           (u("Replace"), self.replaceText))),
            (u("About"), self.aboutDlg),
            (u("Exit"), self.quit)
            ]
        self.setExitKeyText()
        self.bindSelectKey(self.clickEvent)
        self.bindYesKey(self.findNextLink)
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
