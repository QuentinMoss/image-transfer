#!/usr/bin/env python2

#   Copyright 2015 Thomas Cravey

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#       http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import pyrax
import time
import datetime
import requests

############################################################
## Set these constants manually before running the script ##
############################################################

SOURCE_USERNAME = 'example'
SOURCE_API_KEY = '0a1b2c3d4e5f67890a1b2c3d4e5f6789'
SOURCE_REGION = 'IAD'
DESTINATION_USERNAME = SOURCE_USERNAME
DESTINATION_API_KEY = SOURCE_API_KEY
DESTINATION_REGION = 'DFW'
IMAGE_ID = '0a1b2c3d4-0a1b-0a1b-0a1b-0a1b2c3d4e5f'
IMAGE_NAME = 'Image Transferred from %s' % SOURCE_REGION

############################
## Set up the environment ##
############################

# Create context object for the account where the image currently exists
# The source
from_ctx = pyrax.create_context(id_type='rackspace',
                                username=SOURCE_USERNAME,
                                api_key=SOURCE_API_KEY)
from_ctx.authenticate()

# Create context object for the account where the image will be going
# The destination
to_ctx = pyrax.create_context(id_type='rackspace',
                              username=DESTINATION_USERNAME,
                              api_key=DESTINATION_API_KEY)
to_ctx.authenticate()

# Pyrax client for Cloud Files on the source account/region
cf_from = from_ctx.get_client('object_store', SOURCE_REGION)
from_container = cf_from.create_container(IMAGE_ID)

# Pyrax client for Cloud Files on the destination account/region
cf_to = to_ctx.get_client('object_store', DESTINATION_REGION)
to_container = cf_to.create_container(IMAGE_ID)

# Pyrax client for images service on the source account/region
img_from = from_ctx.get_client('images', SOURCE_REGION)

# Pyrax client for the images service on the destination account/region
img_to = to_ctx.get_client('images', DESTINATION_REGION)

#################
## Do the work ##
#################

# Start the task to export the image to Cloud Files
export_task = img_from.export_task(IMAGE_ID, from_container)

# Wait for the image export process to complete,
# printing the status every two minutes
print 'The image is now being exported to Cloud Files'
while export_task.status != 'success':
    print datetime.datetime.now().time().isoformat(),
    print 'Current status:', export_task.status
    time.sleep(120)
    export_task.reload()
print 'The image export is now complete'

# Get a list of all files in the container where the image was exported
objects_to_upload = from_container.get_objects(full_listing=True)

# The image will be split in to 125MB chunks in the Cloud Files container.
# The first file will be a zero byte manifest file, which will be skipped here.
# The rest of the files will be directly copied from the source Cloud Files
# container to the destination cloud files container.
count = 0
for object_to_upload in objects_to_upload:
    if count==0:
        count += 1
        # skip the manifest file, it's always first
        continue
    print 'Uploading:', object_to_upload.name
    to_container.store_object(object_to_upload.name, object_to_upload.fetch())
print 'All files transferred successfully.'

# Now that all the chunks have been transferred, create the manifest file to
# tie them all together.
cf_endpoints = [x for x in to_ctx.service_catalog
                if x['name'] == 'cloudFiles'][0]
cf_endpoint = [x for x in cf_endpoints['endpoints']
               if x['region'] == DESTINATION_REGION][0]['publicURL']
auth_token = to_ctx.auth_token
http_headers = {'X-Auth-Token': to_ctx.auth_token,
                'X-Object-Manifest': IMAGE_ID + '/' + IMAGE_ID + '.vhd-',
                'Content-Length': 0}
url = cf_endpoint + '/' + IMAGE_ID + '/' + IMAGE_ID + '.vhd'
r = requests.put(url, headers=http_headers)

# Import the image from Cloud Files
import_task = img_to.import_task(IMAGE_ID + '.vhd', IMAGE_ID,
                                 img_name=IMAGE_NAME)

# Wait for the image import process to complete,
# printing the status every two minutes
while import_task.status != 'success':
    print datetime.datetime.now().time().isoformat(),
    print 'Current status:', import_task.status
    time.sleep(120)
    import_task.reload()
print 'The image import process is now complete'

print 'All tasks complete.'
