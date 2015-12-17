# User Manual #

**SymWiki** is a personal wiki designed for Symbian S60 devices. You can use it as your personal information manager, knowledge base etc.

SymWiki uses a simple [Creole markup](http://www.wikicreole.org/wiki/CheatSheet) -- actually a common subset of other wikis.

## Usage ##

The main screen always contains any wiki page. When you start the program you see your Home page -- the main page of your wiki.

You can scroll the page using the keyboard, type or edit text of the page.

### Viewing and editing pages ###

Enhanced text editor has been implemented in SymWiki. It provides more features to edit and move through the text.

There is one "functional" key which works like `Control` key on PC modifying behaviour of the next key pressed. "Call" key or "Green tube" is that key. It is reffered as `Func` key in the rest of the document.

While arrow keys move cursor by one character or line, `Func+Up/Down/Left/Right` work as Page Up, Page Down, Home and End keys on PC respectively.

`Select` key (joystic center button) usually works as Enter key inserting new line (with indentation if any), or opens the page under the cursor when it is inside a link.

SymWiki keeps a history of visited pages. You always can go back to the previous key pressing `Back` button (Right softkey). Note, that Right softkey closes the application when the history is empty.

`Func+Select` key opens navigation menu which allows you:

  * Go to the nearest link in the text
  * View sections list (table of contents) and jump quickly to arbitraly section of the document
  * Go to the top or the bottom of the document
  * Jump to the line by number

Also you can use the main menu `Options` to access the list of all pages of your wiki, cut/copy/paste operations and search and replace functions.

Please note, there is no "Save" option in the menu -- you don't need to save your pages manually. All pages have been automatically saved when you open new page or quit the program.

Also a limited undo feature available throug the main menu.

### Links. Creating new pages ###

As usual link looks like a text in double brackets: `[[link]]`. To open the link note the cursor inside the brackets and press Select key. The current page will be saved and the selected page will be opened. If there is no page with such name, the new page will be created.

It is a common way to create new pages in wiki: create a link to new page in other page and then open this link.

### Inserting wiki markup ###

Use `Func+Right softkey` to insert wiki markup. This key combination opens markup menu where you can select necessary item scrolling the list. Also you can search it quickly typing a few letters of its name.

## Wiki markup ##

**Paragraphs** are created by simply typing the text. To separate paragraphs, just leave an empty line between them. Line ends will be preserved inside paragraphs. You can use `\\` to force a line break most everywhere.

**Emphasis** can be marked `//like this//` or `**like this**`, to produce italic text or bold text.

**Link** to a `[[wiki page]]` will render as wiki page. You can also use `[[wiki page|different text]]` that will show different text. Web page addresses, like `[[http://wikicreole.org|WikiCreole]]` can be also used and will display as [WikiCreole](http://wikicreole.org).

**Images** are included with `{{http://site.url/viki.png|Alt text}}`, the text is displayed when the image cannot be shown. You can put images inside links: `[[URL|{{Pic URL|Text}}]]`.

**Code blocks.** No markup is in effect if you type text `{{{like this}}}`, or -- when you need several lines -- like this:

```
{{{
line 1
line 2
line 3
}}}
```

**Headings** are created like this:

```
== Section heading
=== Subsection heading ===
==== Subsubsection heading
```

Trailing equal signs are optional.

**Bullet lists** are created like this:

```
* first item
* second item
** first subitem of second item
* third item
```

**Numbered lists** are made like this:

```
# first item
# second item
## first subitem of second item
# third item
```

**Tables** can be made easily:

```
| first row first column | first row second column |
| second row first column | second row second column |
```

**Horizontal line**, like this one can be used to separate parts of text, you just need to type:

`----`