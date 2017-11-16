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
from sys import stdin, stdout, exit

from gi import require_version
require_version('Gdk', '3.0')
from gi.module import get_introspection_module
get_introspection_module('Gdk').set_allowed_backends('x11')
from gi.repository import Gdk, GdkX11


PROC_NAME = 'firefox'
LOGFILE = '/tmp/hide-ff-title-bar.log'
LOGGING = False      # Enable for debugging only!

Window = namedtuple('Window', ('id', 'desktop', 'pid', 'machine', 'title'))


class EmptyMessage(Exception):
    """Indicates that a message of size zero was received on stdin."""

    pass


def log(msg):
    """Writes log messages to LOGFILE iff LOGGING is True."""

    if LOGGING:
        with suppress(OSError):
            with open(LOGFILE, 'a') as file:
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
        raise EmptyMessage()

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


def decorate_window(window, decoration):
    """Decorates the respective window using Gdk."""

    gdk_display = GdkX11.X11Display.get_default()
    Gdk.Window.process_all_updates()
    gdk_window = GdkX11.X11Window.foreign_new_for_display(
        gdk_display, window.id)
    Gdk.Window.set_decorations(gdk_window, decoration)
    Gdk.Window.process_all_updates()


def hide_title_bar(proc_name, when_to_hide_title_bar):
    """Conditionally hide title bar of the respective process."""

    result = None
    decoration = None

    if when_to_hide_title_bar == WhenToHideTitleBar.ALWAYS:
        decoration = Gdk.WMDecoration.BORDER
        result = True
    elif when_to_hide_title_bar == WhenToHideTitleBar.MAX_ONLY:
        result = False
    elif when_to_hide_title_bar == WhenToHideTitleBar.NEVER:
        decoration = Gdk.WMDecoration.ALL
        result = True

    if decoration is not None:
        for window in windows_by_procname(proc_name):
            log('Decorating window: {}'.format(window))
            decorate_window(window, decoration)

    return result


def main():
    """Main function to communicate via native API."""

    log('Starting...')

    try:
        message = get_message()
    except EmptyMessage:
        log('Exiting on empty message...')
        exit(0)

    log('Received message: {}'.format(dumps(message)))
    when_to_hide_title_bar = WhenToHideTitleBar.from_message(message)
    result = hide_title_bar(PROC_NAME, when_to_hide_title_bar)

    if result is None:
        reply = {'knownFailure': 'UNKNOWN_WHEN_TO_HIDE'}
    elif result:
        reply = {'okay': True}
    else:
        reply = {"knownFailure": "MAX_ONLY_UNSUPPORTED"}

    log('Sending reply: {}'.format(dumps(reply)))
    send_message(reply)
    log('Finished...')


class WhenToHideTitleBar(Enum):
    """When to hide title bar options."""

    ALWAYS = 'always'
    MAX_ONLY = 'maxonly'
    NEVER = 'never'
    UNKNOWN = None

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
            if enumeration.value == value:
                return enumeration

        return cls.UNKNOWN


if __name__ == '__main__':
    main()
