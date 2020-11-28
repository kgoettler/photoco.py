# photoco.py

A quick utility for syncing image files from a memory card, and organizing them
on a local drive.

I take a lot of photos but don't sync them to my computer at regular intervals.
I wrote this utility to help me quickly sync photos from my memory cards to my
computer and enforce a simple date-based folder structure. The folder structure
looks like this:

```
2020
└── 11
    ├── 21
    │   ├── CR3
    │   └── JPG
    ├── 26
    │   ├── CR3
    │   └── JPG
    └── 27
        ├── CR3
        └── JPG 
```

## Dependencies
- Python 3
- rsync

## Usage

```bash
$ ./photoco.py -h
usage: photoco.py [-h] --source SOURCE --dest DEST [--start-index START_INDEX]
                  [--end-index END_INDEX] [--start-date START_DATE]
                  [--end-date END_DATE] [-n] [-v]

Copy image files from external memory card to local disk, enforcing a date-
based file structure.

optional arguments:
  -h, --help            show this help message and exit
  --source SOURCE       Source directory
  --dest DEST           Destination directory
  --start-index START_INDEX
                        Starting image number (e.g. 123 matches IMG_0123)
  --end-index END_INDEX
                        Ending image number (e.g. 123 matches IMG_0123)
  --start-date START_DATE
                        Start date
  --end-date END_DATE   End date
  -n, --dry-run         Applies the --dry-run flag to rsync, thereby showing
                        what would be transferred but not transferring any
                        files
  -v, --verbose         Applies the --verbose flag to rsync, thereby printing
                        detailed output to stdout
```

Only two arguments are required: source and destination directories. Image files
are scraped from the source directory, and organized into the date-based folder
structure within the destination.

```bash
$ photoco.py --source /Volumes/CANONI/DCIM/100CANON/ --dest /Users/kgoettler/Pictures/
```

You can also provide start and end dates if you want to only sync files within a
certain date range

```bash
$ photoco.py --source /Volumes/CANONI/DCIM/100CANON/ \
             --dest /Users/kgoettler/Pictures/ \
             --start-date 20201120 \
             --end-date 20201127
```

Because my camera uses the naming convention `IMG_XXXX.CR3` for naming images,
you can also provide start and end indices if you want to only sync files witin
a certain range:

```bash
$ photoco.py --source /Volumes/CANONI/DCIM/100CANON/ \
             --dest /Users/kgoettler/Pictures/ \
             --start-index 100 \
             --end-date 150
```
