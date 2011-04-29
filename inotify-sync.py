#!/usr/bin/env python
#
# Usage:
#   ./inotify-sync.py source dest
#
# Blocks monitoring |source| and its subdirectories for modifications on
# files. Copies files to |dest| which is assumed to be a mirror.
#
# Example:
#   ./inotify-sync.py /local/folder /nfs/mount
#
# Dependencies:
#   Linux, Python 2.6, Pyinotify
#
# Acknowledgements:
#   Much of this code cribbed from Pyinotify example code.
#
# Copyright (c) 2011 Stephen A. Goss 
# license: WTFPL 2.0
#

import os
import sys
import shutil
import pyinotify

class OnWriteHandler(pyinotify.ProcessEvent):
    def my_init(self, path1, path2):
        self.path1 = path1
        self.path2 = path2

    def get_target_path(self, source_path):
        assert(source_path.startswith(self.path1))
        clipped = source_path[len(self.path1):]
        target = self.path2 + clipped
        return target

    def do_copy(self, source_file):
        target_file = self.get_target_path(source_file)
        # print 'copying ' + source_file + ' to ' + target_file
        shutil.copyfile(source_file, target_file)

    def process_IN_MODIFY(self, event):
        print '==> Modification detected'
        self.do_copy(event.pathname)

def auto_sync(path1, path2):
    wm = pyinotify.WatchManager()
    handler = OnWriteHandler(path1=path1, path2=path2)
    notifier = pyinotify.Notifier(wm, default_proc_fun=handler)
    wm.add_watch(path1, pyinotify.ALL_EVENTS, rec=True, auto_add=True)
    print '==> Start monitoring %s (type c^c to exit)' % path1
    notifier.loop()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print >> sys.stderr, "Command line error: missing argument(s)."
        sys.exit(1)

    # Required arguments
    path1 = os.path.realpath(sys.argv[1])
    path2 = os.path.realpath(sys.argv[2])

    # Blocks monitoring
    auto_sync(path1, path2)
