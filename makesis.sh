#!/bin/bash
VERSION='1.4.0'
# make distro
rm -rf build
mkdir -p build
cp -v utils.py build/
cp -v xtext.py build/
cp -v symwiki.py build/default.py
# create sis-file
../Ensymble/ensymble.py py2sis --uid=0xe3e34da3 --appname="Symbian Wiki" --shortcaption="SymWiki" --version=$VERSION --vendor="D.Mych" --verbose build symwiki-${VERSION}.sis
rm -rf build
# create zip-file
zip symwiki-${VERSION}.zip symwiki.py xtext.py utils.py
