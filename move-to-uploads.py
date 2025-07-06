############################################################
# This file will process a collection of rar, .tz .zip etc #
# And extract their files to a loca drive.                 #
# Then It will move them to the s3 bucket                  #
############################################################

import os
import uuid
import pathlib

# Check first if we're runnin is EC2,
# In which case, use ebs.

if os.path.exists('/mnt/ebs_volume'):
    local_souce = None # because we'll use s3
    work_space = os.path('/mnt/ebs_volume')
else:
    local_source = os.path.abspath('root/zips')
    work_space = os.path.abspath('root/results')

