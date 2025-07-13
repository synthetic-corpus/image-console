##############################################
# This is really just about using arg parser #
##############################################

import argparse

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
    args = parser.parse_args()
    print(args)

if __name__ == '__main__':
    main()