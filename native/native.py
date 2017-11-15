#!/usr/bin/env python3

#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at https://mozilla.org/MPL/2.0/.
#
"""Hides firefox's title bar."""

from collections import namedtuple
from contextlib import suppress
from datetime import datetime
from enum import Enum
from json import loads, dumps
from os import linesep
from struct import pack, unpack
from subprocess import DEVNULL, PIPE, CalledProcessError, run
from sys import stdin, stdout, stderr, exit

from gi import require_version
from gi.module import get_introspection_module
from gi.repository import Gdk, GdkX11


PROC_NAME = 'firefox'

Window = namedtuple('Window', ('id', 'desktop', 'pid', 'machine', 'title'))


def debug(msg):
    """Writes a debug message."""

    with open('/tmp/hide-ff-title-bar.debug', 'a') as file:
        file.write('[{}] {}{}'.format(datetime.now(), msg, linesep))


def window_from_string(string):
    """Loads the window named tuple from the respective string."""

    id_, desktop, pid, machine, *title = filter(None, string.split())
    return Window(int(id_, 16), int(desktop), int(pid), machine, ' '.join(title))


def get_windows():
    """Yields windows using "wmctrl"."""

    completed_process = run(('wmctrl', '-lp'), stdout=PIPE, stderr=DEVNULL)

    try:
        completed_process.check_returncode()
    except CalledProcessError:
        raise StopIteration() from None

    try:
        text = completed_process.stdout.decode()
    except UnicodeDecodeError:
        raise StopIteration() from None

    for line in filter(None, text.split(linesep)):
        with suppress(TypeError, ValueError):
            yield window_from_string(line)


def get_pids(proc_name):
    """Gets PID of the respective process by invoking "pidof"."""

    completed_process = run(('pidof', proc_name), stdout=PIPE, stderr=DEVNULL)

    try:
        completed_process.check_returncode()
    except CalledProcessError:
        raise StopIteration() from None

    try:
        text = completed_process.stdout.decode()
    except UnicodeDecodeError:
        raise StopIteration() from None

    for pid in filter(None, text.split()):
        with suppress(ValueError):
            yield int(pid)


def windows_by_procname(proc_name):
    """Yields windows by process name."""

    pids = tuple(get_pids(proc_name))

    for window in get_windows():
        if window.pid in pids:
            yield window


def get_message():
    """Reads a JSON-ish message of a certain length."""

    raw_length = stdin.buffer.read(4)

    if not raw_length:
        exit(0)

    length, *_ = unpack('@I', raw_length)
    message = stdin.read(length)
    return loads(message)


def send_message(content):
    """Sends a JSON-ish message with content length header."""

    string = dumps(content)
    length = pack('@I', len(string))
    stdout.buffer.write(length)
    stdout.buffer.write(string.encode('utf-8'))
    stdout.buffer.flush()


class WhenToHideTitleBar(Enum):
    """When to hide title bar options."""

    ALWAYS = 'always'
    MAX_ONLY = 'maxonly'
    NEVER = 'never'
    UNKNOWN = None

    def __str__(self):
        """Returns the enumeration's string value."""
        return str(self.value)

    @classmethod
    def from_message(cls, msg):
        """Returns the respective enumeration
        value from the provided message.
        """
        try:
            value = msg["whenToHideTitleBar"]
        except KeyError:
            return cls.UNKNOWN

        for enumeration in cls:
            if str(enumeration) == value:
                return enumeration

        return cls.UNKNOWN


def decorate_window(window, decoration):
    """Decorates the respective window using Gdk."""

    gdk_display = GdkX11.X11Display.get_default()
    Gdk.Window.process_all_updates()
    gdk_window = GdkX11.X11Window.foreign_new_for_display(
        gdk_display, window.id)
    Gdk.Window.set_decorations(gdk_window, decoration)
    Gdk.Window.process_all_updates()


def hide_title_bar():
    """Main function to hide firefox's title bar."""

    received = get_message()
    debug(str(received))
    require_version('Gdk', '3.0')
    get_introspection_module('Gdk').set_allowed_backends('x11')
    decoration = None
    when_to_hide_title_bar = WhenToHideTitleBar.from_message(received)

    if when_to_hide_title_bar == WhenToHideTitleBar.ALWAYS:
        decoration = Gdk.WMDecoration.BORDER
        reply = {'okay': 'true'}
    elif when_to_hide_title_bar == WhenToHideTitleBar.MAX_ONLY:
        reply = {"knownFailure": "MAX_ONLY_UNSUPPORTED"}
    elif when_to_hide_title_bar == WhenToHideTitleBar.NEVER:
        decoration = Gdk.WMDecoration.ALL
        reply = {'okay': 'true'}
    else:
        reply = {'knownFailure': 'UNKNOWN_WHEN_TO_HIDE'}

    if decoration is not None:
        for window in windows_by_procname(PROC_NAME):
            debug('Decorating window: {}.'.format(window))
            decorate_window(window, decoration)

    send_message(reply)
    print(dumps(received, indent=2, sort_keys=True), file=stderr)


if __name__ == '__main__':
    hide_title_bar()
