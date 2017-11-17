#!/usr/bin/env python3

#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at https://mozilla.org/MPL/2.0/.
#

import json
import os
import struct
import sys

stdout = os.fdopen(sys.stdout.fileno(), 'wb')

def getMessage():
  rawLength = sys.stdin.buffer.read(4)
  if len(rawLength) == 0:
    sys.exit(0)
  messageLength = struct.unpack('@I', rawLength)[0]
  message = sys.stdin.buffer.read(messageLength).decode('utf-8')
  return json.loads(message)

def sendMessage(messageContent):
  encodedContent = json.dumps(messageContent)
  encodedLength = struct.pack('@I', len(encodedContent))
  stdout.write(encodedLength)
  stdout.write(encodedContent.encode('utf-8'))
  stdout.flush()

received = getMessage()
sys.stderr.write(json.dumps(received, indent=2, sort_keys=True))


try:
  import subprocess
  ffPid = int(subprocess.run(["bash", "-c", "wmctrl -lp | grep -Fh $(pgrep firefox | head -n 1) -- -"], universal_newlines=True, stdout=subprocess.PIPE).stdout.split()[0], 0)

  import gi
  gi.require_version('Gdk', '3.0')

  import gi.module
  gi.module.get_introspection_module('Gdk').set_allowed_backends('x11')

  from gi.repository import Gdk, GdkX11

  gdk_display = GdkX11.X11Display.get_default()
  Gdk.Window.process_all_updates()
  gdk_window = GdkX11.X11Window.foreign_new_for_display(gdk_display, ffPid)

  if received["whenToHideTitleBar"] == "always":
    Gdk.Window.set_decorations(gdk_window, Gdk.WMDecoration.BORDER)
    Gdk.Window.process_all_updates()
    sendMessage({"okay": True})

  elif received["whenToHideTitleBar"] == "maxonly":
    sendMessage({"knownFailure": "MAX_ONLY_UNSUPPORTED"});

  elif received["whenToHideTitleBar"] == "never":
    Gdk.Window.set_decorations(gdk_window, Gdk.WMDecoration.ALL)
    Gdk.Window.process_all_updates()
    sendMessage({"okay": True})

  else:
    sendMessage({"knownFailure": "UNKNOWN_WHEN_TO_HIDE"})

except BaseException as e:
  sendMessage({"unknownFailure": str(e)})
  raise
