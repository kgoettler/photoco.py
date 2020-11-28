#!/usr/bin/env python3

from datetime import datetime
from os.path import getmtime, exists, splitext, join
import argparse
import os
import re
import subprocess
import tempfile

class Photocopy:

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Copy image files from external memory card to local disk, enforcing a date-based file structure.',
        )
        self.parser.add_argument(
            '--source',
            dest='source',
            type=str,
            required=True,
            help='Source directory',
        )
        self.parser.add_argument(
            '--dest',
            dest='dest',
            type=str,
            required=True,
            help='Destination directory',
        )
        self.parser.add_argument(
            '--start-index',
            type=int,
            help='Starting image number (e.g. 123 matches IMG_0123)',
            required=False,
            default=None,
        )
        self.parser.add_argument(
            '--end-index',
            type=int,
            help='Ending image number (e.g. 123 matches IMG_0123)',
            required=False,
            default=None,
        )
        self.parser.add_argument(
            '--start-date',
            type=strtodate,
            help='Start date',
            required=False,
            default=None,
        )
        self.parser.add_argument(
            '--end-date',
            type=strtodate,
            help='End date',
            required=False,
            default=None,
        )
        self.parser.add_argument(
            '-n',
            '--dry-run',
            dest='dryrun',
            action='store_true',
            required=False,
            default=False,
            help='Applies the --dry-run flag to rsync, thereby showing what would be transferred but not transferring any files',
        )
        self.parser.add_argument(
            '-v', 
            '--verbose',
            action='store_true',
            default=False,
            help='Applies the --verbose flag to rsync, thereby printing detailed output to stdout'
        )
        self.parser.parse_args(namespace=self)
        return

    def __repr__(self):
        msg = 'Photocopy\n' + \
                'Source:      {}\n'.format(self.source) + \
                'Destination: {}\n'.format(self.dest)
        return msg

    def get_filelist(self):
        '''
        Build a dict of files to sync. 
        
        Each key is a destination directory, each value is a list of files to
        copy into that directory.
        '''
        files = {}
        for srcfile in os.listdir(self.source):
            # Parse filename
            m = re.match('IMG_(\d+)\.(\w+)', srcfile)
            if m is None:
                continue
            srcnum, ext = m.groups()
            srcnum = int(srcnum)
            srcpath = join(self.source, srcfile)
            srctime = datetime.fromtimestamp(getmtime(srcpath))
            # Skip if not in range of photos
            # or if not in date range
            if (self.start_index is not None) and (srcnum < self.start_index):
                continue
            if (self.end_index is not None) and (srcnum > self.end_index):
                continue
            if (self.start_date is not None) and (self.start_date > srctime):
                continue
            if (self.end_date is not None) and (self.end_date < srctime):
                continue
            outdir = join(
                self.dest,
                srctime.strftime('%Y'),
                srctime.strftime('%m'),
                srctime.strftime('%d'),
                ext,
            )
            if outdir not in files:
                files[outdir] = [srcfile]
            else:
                files[outdir].append(srcfile)
        return files
    
    def copy(self):
        '''
        Perform copy
        '''
        rsync_flags = '-ar'
        if self.dryrun:
            rsync_flags += 'n'
        if self.verbose:
            rsync_flags += 'v'
        for dest, files in self.get_filelist().items():
            if not exists(dest) and not self.dryrun:
                os.makedirs(dest)
            print('Found {} files to sync to {}'.format(len(files), dest))
            files_from = tempfile.NamedTemporaryFile(mode='w+', delete=False)
            files_from.write('\n'.join(files))
            files_from.close()
            args = [
                'rsync',
                rsync_flags,
                '--files-from={}'.format(files_from.name),
                self.source,
                dest,
            ]
            # Call
            subprocess.call(args)
            os.remove(files_from.name)
        return

def strtodate(x):
    return datetime.strptime(x, '%Y%m%d')

if __name__ == '__main__':
    p = Photocopy()
    p.copy()
