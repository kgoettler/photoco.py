#!/usr/bin/env python3

from datetime import datetime
from os.path import getmtime, exists, splitext, join
from pprint import pprint
import argparse
import math
import os
import re

class Photocopy:

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Copy image files from external memory card to local disk, enforcing a date-based file structure',
        )
        self.parser.add_argument(
            'start',
            type=int,
            help='Starting image number (e.g. 123 matches IMG_0123)',
        )
        self.parser.add_argument(
            'end',
            type=int,
            help='Ending image number (e.g. 123 matches IMG_0123)',
        )
        self.parser.add_argument(
            '--source',
            dest='source',
            type=str,
            required=False,
            default='/Volumes/Untitled/DCIM/100CANON/',
            help='Source directory',
        )
        self.parser.add_argument(
            '--dest',
            dest='dest',
            type=str,
            required=False,
            default='/Users/kgoettler/Pictures/Canon/',
            help='Destination directory',
        )
        self.parser.parse_args(namespace=self)
        print(self)
        return

    def __repr__(self):
        msg = 'Photocopy\n' + \
                'Source:      {}\n'.format(self.source) + \
                'Destination: {}\n'.format(self.dest)
        return msg

    def get_filelist(self):
        files = {}
        for srcfile in os.listdir(self.source):
            # Parse filename
            m = re.match('IMG_(\d+)\.(\w+)', srcfile)
            if m is None:
                continue
            srcnum, ext = m.groups()
            srcnum = int(srcnum)
            # Skip if not in range of photos
            if ((self.start is None or srcnum < self.start) or (self.end is None or srcnum > self.end)):
                continue
            srcpath = join(self.source, srcfile)
            mtime = datetime.fromtimestamp(getmtime(srcpath))
            outdir = join(
                self.dest,
                mtime.strftime('%Y'),
                mtime.strftime('%m'),
                mtime.strftime('%d'),
            )
            if outdir not in files:
                files[outdir] = [srcfile]
            else:
                files[outdir].append(srcfile)
        return files
    
    def copy(self):
        for dest, files in self.get_filelist().items():
            print('Copying {} files to {}:'.format(len(files), dest))
            for file in files:
                print('\t{}'.format(file))
        return

if __name__ == '__main__':
    p = Photocopy()
    p.copy()
