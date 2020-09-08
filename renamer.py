from argparse import ArgumentParser
from pathlib import Path

argp = ArgumentParser('Read in command line arguments')

# Base arguments
argp.add_argument('--dry_run', '-n', action='store_true', \
    help='Perform dry run without touching files')
argp.add_argument('--verbose', '-v', action='store_true', \
    help='Provide verbose output of actions')

# Filter options
fargp = argp.add_argument_group('Filters')
fargp.add_argument('dirpath', metavar='DIRPATH', type=str, \
    help='Organize files in DIRPATH')
fargp.add_argument('--filter_stem', '-f', default='*', \
    help='Filter to files whose stem matches basic wildcard expression FILTER')
fargp.add_argument('--filter_type', '-t', default='f', choices=['f','d'], \
    help='Filter to paths of type [f]ile or [d]irectory')
fargp.add_argument('--filter_suffix', '-s', default='*', metavar='SUFFIX', \
    help='Filter to files whose suffix matches SUFFIX')

# Rename options
rargp = argp.add_argument_group('Rename options')
# Suffixes
rargp.add_argument('--new_suffix', '-nsuf', type=str, metavar='SUFFIX', \
    help='Change suffix of file to SUFFIX')
rargp.add_argument('--remove_suffix', '-rsuf', action='store_true', \
    help='Remove final suffix (useful for double suffixes)')
# Remove characters
rargp.add_argument('--remove_start', '-rms', type=int, metavar='N', \
    help='Remove starting N characters')
rargp.add_argument('--remove_final', '-rmf', type=int, metavar='N', \
    help='Remove final N characters of stem of file')
rargp.add_argument('--remove_string', '-rmstr', type=str, metavar='STRING', \
    help='Remove all instances of STRING from stem of file')
# Keep characters
rargp.add_argument('--keep_start', '-ks', type=int, metavar='N', \
    help='Keep starting N characters')
rargp.add_argument('--keep_final', '-kf', type=int, metavar='N', \
    help='Keep final N characters of stem of file')
# Replace characters
rargp.add_argument('--replace_start', '-repls', type=str, metavar='STRING', \
    help='Replace starting characters with STRING of equal length of stem of file')
rargp.add_argument('--replace_final', '-replf', type=str, metavar='STRING', \
    help='Replace final characters with STRING of equal length of stem of file')
# Append and preprend
rargp.add_argument('--prepend_prefix', '-pp', metavar='PREFIX', \
    help='Prepend PREFIX to stem of file')
rargp.add_argument('--append_suffix', '-ap', metavar='SUFFIX', \
    help='Append SUFFIX to stem of file')


args = argp.parse_args()

p = Path(args.dirpath)
if not p.exists():
    print('Path %s does not exist' % str(args.dirpath))
    exit(1)

if args.filter_type == 'd':
    filter_string = args.filter_stem
else:
    filter_string = (args.filter_stem + args.filter_suffix).replace('**','*')
path_list = sorted(p.glob(filter_string))
if args.verbose:
    print('Matching files on: %s' % str(p / filter_string) )
    if not len(path_list):
        print('No matches found')

def new_suffix(f, suf):
    # return f.with_suffix(suf)
    return '.'.join(f.split('.')[0:-1]) + '.' + suf

def remove_start(f, n):
    return f[n:]

def remove_final(f, n):
    pass

f_map = {}
for f in path_list:
    #print(f)
    if args.filter_type == 'd' and not f.is_dir():
        continue
    elif args.filter_type == 'f' and not f.is_file():
        continue

    #print(f)
    # Update suffixes
    if args.new_suffix:
        nf = f.with_suffix(args.new_suffix)
    elif args.remove_suffix:
        nf = f.with_suffix('')
    else:
        nf = f

    stem = nf.stem
    suf = nf.suffix

    if args.remove_start:
        stem = stem[args.remove_start:]
    if args.remove_final:
        stem = stem[:- args.remove_final]
    if args.keep_start:
        stem = stem[0:args.keep_start]
    if args.keep_final:
        stem = stem[- args.keep_final:]
    if args.remove_string:
        stem = stem.replace(args.remove_string, '')
    if args.replace_start:
        stem = args.replace_start + stem[len(args.replace_start):]
    if args.replace_final:
        stem = stem[:- len(args.replace_final)] + args.replace_final
    if args.prepend_prefix:
        stem = args.prepend_prefix + stem
    if args.append_suffix:
        stem = stem + args.append_suffix
    
    f_map[f] = f.parent / (stem + suf)

if len(set(f_map.keys())) != len(set(f_map.values())):
    print('Rename operation results in a loss of detail and will be aborted')
    exit(1)
else:
    print('Rename operation results in no loss of detail.')

if args.dry_run:
    print('DRY-RUN ONLY')

for f in f_map:
    if args.verbose:
        print('%s --> %s' % (str(f), str(f_map[f])))
    if not args.dry_run and not f_map[f].exists():
        f.rename(f_map[f])