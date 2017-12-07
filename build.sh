#!/bin/bash -e

#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at https://mozilla.org/MPL/2.0/.
#

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

heading "Running tests"
jshint --config test/jshintrc background.js || exit

heading "Building WebExtension"
# Files not distributed:
 # native/control gets put into the .deb without modification
web-ext build --ignore-files build.sh native/control test
