from argparse import ArgumentParser
from pathlib import Path

MIN_FOLDER_SIZE = 5

argp = ArgumentParser('Read in command line arguments')
argp.add_argument('dirpath', metavar='DIRPATH', type=str, \
    help='Organize files in DIRPATH')
argp.add_argument('--min_size', '-min', default=MIN_FOLDER_SIZE, type=int, \
    help='Minimum number of matching files to place into a new subdirectory')
argp.add_argument('--suffix', '-s', default='*', \
    help='Restrict file matching to those ending with SUFFIX ' \
        + '[Default is to match all files]')
argp.add_argument('--filter', '-f', default='*', \
    help='Filter to files whose stem matches basic wildcard expression')
argp.add_argument('--separator', '-sep', default='-', type=str, \
    help='Use SEPERATOR to develop match templates')
argp.add_argument('--cmp_mult_sep', '-cms', action='store_false', \
    help='Treat multiple separators as one', default=True)
argp.add_argument('--trunc_directory', '-td', action='store_true', \
    help='Use only second to last filename chunk for directory name if unique')
argp.add_argument('--trunc_filename', '-tf', action='store_true',\
    help='Chop off directory name from filename if unique')
argp.add_argument('--dry_run', '-n', action='store_true', \
    help='Perform dry run without touching files')
argp.add_argument('--verbose', '-v', action='store_true', \
    help='Provide verbose output of actions')
args = argp.parse_args()

p = Path(args.dirpath)
if not p.exists():
    print('Path %s does not exist' % str(args.dirpath))
    exit(1)

path_list = sorted(p.glob(args.filter + '.' + args.suffix))
file_list = []
name_list = []
for f in path_list:
    if f.is_file():
        file_list = file_list + [f]
        name_list = name_list + [f.stem]

print(len(path_list), len(file_list), len(name_list))

sl_map = {}
ss_map = {}
ns_map = {}
nl_map = {}
for f in file_list:
    if args.cmp_mult_sep:
        name = f.name.replace(args.separator + args.separator, args.separator)
        stem = f.stem.replace(args.separator + args.separator, args.separator)
    else:
        name = f.name
        stem = f.stem
    nl_map[f] = name
    ns_map[f] = nl_map[f].split(args.separator)[-1]
    sl_map[f] = args.separator.join(stem.split(args.separator)[0:-1])
    ss_map[f] = sl_map[f].split(args.separator)[-1]

common_long_prefix_list = sorted(set(sl_map.values()))
common_short_prefix_list = sorted(set(ss_map.values()))
print(common_long_prefix_list, common_short_prefix_list)

if args.trunc_directory and (len(common_long_prefix_list) == len(common_short_prefix_list)):
    s_map = ss_map
    common_prefix_list = common_short_prefix_list
    print('Truncated directory names requested and no loss of detail is observed')
else:
    s_map = sl_map
    common_prefix_list = common_long_prefix_list
    if args.trunc_directory:
        print('Using truncated directory names would result in lost detail in subdirs')

fs_map = {}
fl_map = {}
for f in file_list:
    fs_map[f] = f.parent / s_map[f] / ns_map[f]
    fl_map[f] = f.parent / s_map[f] / nl_map[f]

if args.trunc_filename and (len(file_list) == len(sorted(set(fs_map.values())))):
    f_map = fs_map
    print('Truncated file names requested and no loss of detail is observed')
else:
    f_map = fl_map
    if args.trunc_filename:
        print('Using truncated filename would result in duplicate filenames')

def create_subdir(p: Path, subdir: str):
    ps = p / subdir
    try:
        ps.mkdir(exist_ok=True)
    except:
        print('Error creating subdirectory %s' % str(ps))
        raise

for s in common_prefix_list:
    if not args.dry_run:
        create_subdir(p, s)
    else:
        print('DRY-RUN: Create subdirectory %s' % str(p / s))

for f in file_list:
    if s_map[f] not in common_prefix_list:
        print('Unexpected mapping error for %s to %s' \
            % (f, s_map[f]))
        print('Mapped subdirectory is not among the legal set of choices: %s'\
            % str(common_prefix_list))
        raise ValueError
for f in file_list:
    if args.dry_run:
        if args.verbose:
            print('move %s to %s' % (str(f), str(f_map[f])))
    else:
        if f_map[f].exists() or f == f_map[f]:
            print('Target %s for %s already exists' % (str(f_map[f]), str(f)))
        else:
            f.rename(f_map[f])
print('Complete')
#print(str(path_list))
#print(str(name_list))