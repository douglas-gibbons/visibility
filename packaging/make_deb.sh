#!/bin/bash -ex

cd $(dirname $0)

# Cleanup
rm -rf debian/usr/share/*

# App
mkdir -p debian/usr/share/visibility
cp -R ../src/* debian/usr/share/visibility

# Clean up .pyc files
find debian/usr/share/visibility/ -name *.pyc -exec rm {} \;

# Docs
mkdir -p debian/usr/share/doc/visibility
cp ../changelog debian/usr/share/doc/visibility/.
cp ../changelog debian/usr/share/doc/visibility/changelog.Debian
cp ../copyright debian/usr/share/doc/visibility/.
gzip --best debian/usr/share/doc/visibility/changelog
gzip --best debian/usr/share/doc/visibility/changelog.Debian

fakeroot dpkg-deb --build debian
version=$(dpkg-deb --info debian.deb  | grep Version: | cut -d ' ' -f 3)
deb_file=visibility_${version}_all.deb
mv debian.deb $deb_file
lintian $deb_file
dpkg-deb --info deb_file