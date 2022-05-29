#!/usr/bin/env python3

from datetime import datetime
from os.path import getmtime, exists, splitext, join
import argparse
import os
import re
import subprocess
import tempfile

import exiftool
from tqdm import tqdm

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
            '--date-start',
            type=strtodate,
            help='Start date',
            required=False,
            default=None,
        )
        self.parser.add_argument(
            '--date-end',
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


    def get_filelist_2(self):
        pattern = 'IMG_(\d+)\.(\w+)'
        files = [join(self.source, file) for file in os.listdir(self.source) if re.match(pattern, file)]
        
        ti = datetime.now()
        filemap = {}
        with exiftool.ExifToolHelper() as et:
            metadata = et.get_metadata(files)
            for meta in metadata:
                srcfile = meta['SourceFile']
                # Parse filename
                m = re.match('IMG_(\d+)\.(\w+)', srcfile)
                if m is None:
                    continue
                srcnum, ext = m.groups()
                srcnum = int(srcnum)
                srcpath = join(self.source, srcfile)
                srctime = datetime.strptime(meta['EXIF:DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')
                # Skip if not in range of photos
                # or if not in date range
                if (self.start_index is not None) and (srcnum < self.start_index):
                    continue
                if (self.end_index is not None) and (srcnum > self.end_index):
                    continue
                if (self.date_start is not None) and (self.date_start > srctime):
                    continue
                if (self.date_end is not None) and (self.date_end < srctime):
                    continue
                outdir = join(
                    self.dest,
                    ext,
                    srctime.strftime('%Y'),
                    srctime.strftime('%m'),
                    srctime.strftime('%d'),
                )
                if outdir not in filemap:
                    filemap[outdir] = [srcfile]
                else:
                    filemap[outdir].append(srcfile)
        tf = datetime.now()
        print('Runtime: {}'.format(str(tf - ti)))
        return filemap


    def get_filelist(self):
        '''
        Build a dict of files to sync. 
        
        Each key is a destination directory, each value is a list of files to
        copy into that directory.
        '''
        # Start exiftool
        et = exiftool.ExifTool()
        et.run()

        files = {}
        for srcfile in tqdm(os.listdir(self.source), desc='Scanning image files'):
            # Parse filename
            m = re.match('IMG_(\d+)\.(\w+)', srcfile)
            if m is None:
                continue
            srcnum, ext = m.groups()
            srcnum = int(srcnum)
            srcpath = join(self.source, srcfile)
            #srctime = datetime.fromtimestamp(getmtime(srcpath))
            # Read datetime using exiftool
            meta = et.execute_json(srcpath)
            srctime = meta[0].get('EXIF:DateTimeOriginal')
            srctime = datetime.strptime(srctime, '%Y:%m:%d %H:%M:%S')
            # Skip if not in range of photos
            # or if not in date range
            if (self.start_index is not None) and (srcnum < self.start_index):
                continue
            if (self.end_index is not None) and (srcnum > self.end_index):
                continue
            if (self.date_start is not None) and (self.date_start > srctime):
                continue
            if (self.date_end is not None) and (self.date_end < srctime):
                continue
            outdir = join(
                self.dest,
                ext,
                srctime.strftime('%Y'),
                srctime.strftime('%m'),
                srctime.strftime('%d'),
            )
            if outdir not in files:
                files[outdir] = [srcfile]
            else:
                files[outdir].append(srcfile)
        et.terminate()
        return files
    
    def copy(self):
        '''
        Perform copy
        '''
        ti = datetime.now()
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
        tf = datetime.now()
        print('Runtime: {}'.format(str(tf - ti)))
        return

def strtodate(x):
    return datetime.strptime(x, '%Y%m%d')

if __name__ == '__main__':
    p = Photocopy()
    p.copy()
