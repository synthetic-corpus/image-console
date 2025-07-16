##############################################
# This is really just about using arg parser #
##############################################

import argparse
import os
from run_extract import ArchiveExtract
from s3_access import S3Access

bucket = os.environ.get('S3_BUCKET_NAME')

def main():
    parser = argparse.ArgumentParser(
        description="List to help run move-to-uploads easily"
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='flag for testing of the script \
            will not save to s3 when testing'
    )
    parser.add_argument(
        '--local',
        action='store_true',
        help='use only if running locally, and not intending \
            to interact with s3'
    )
    parser.add_argument(
        '--sample',
        default=5,
        type=int,
        help='Defualt 5. The number of samples \
            from source archive to process. If 0 \
            or --all flag is used will be ignored'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='overrides sample size. \
            All archives will be processed if used!'
    )
    args = parser.parse_args()
    if args.all or args.sample < 1:
        args.sample = None
    print(args)

    archiveExtract = ArchiveExtract(
        local=False,
        test=args.test)

    s3access = S3Access(bucket)
    items = s3access.get_sources(size=args.sample)


    print('Items found. List first 10')
    for i, object in enumerate(items):
        if i >= 9:
            break
        else:
            print(object)

    print('Checking for ruling out depth')
    found = False
    for i in items:
        if i.find('/') > -1:
            print(i)
            found = True
    if found:
        print('oh noes... went one layer too deep')
    else:
        print("Content List stayed at expected depth")

if __name__ == '__main__':
    main()