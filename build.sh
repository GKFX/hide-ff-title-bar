#!/bin/bash -e

heading() {
  echo
  echo ====== "$1" ======
}

heading "Removing artifacts directory"
rm -rf web-ext-artifacts/

heading "Building Debian package"
TMPFILE=$(mktemp -d -p /dev/shm)
mkdir -p ${TMPFILE}/usr/lib/mozilla/native-messaging-hosts/
mkdir -p ${TMPFILE}/opt/hide-ff-title-bar/
mkdir ${TMPFILE}/DEBIAN/
cp native/hide_title_bar.json ${TMPFILE}/usr/lib/mozilla/native-messaging-hosts/
cp native/native.py           ${TMPFILE}/opt/hide-ff-title-bar/
cp native/control             ${TMPFILE}/DEBIAN/
dpkg-deb --build ${TMPFILE} native/hide-title-bar-for-firefox.deb
rm -rf ${TMPFILE}

heading "Building WebExtension"
web-ext build
