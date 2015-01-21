# Image Transfer

Transfer a glance image from one Rackspace region to another, optionally transferring the image to a different account.

Requirements
------------
[pyrax](http://github.com/rackspace/pyrax) and [requests](http://docs.python-requests.org/), and anything those packages require.  Pyrax currently requires Python 2.7.

Usage
-----

Set the constants `SOURCE_USERNAME`, `SOURCE_API_KEY`, `SOURCE_REGION`, `DESTINATION_REGION`, `IMAGE_ID`, and `IMAGE_NAME` to appropriate values.  To optionally move the image to another account in the process, also set the `DESTINATION_USERNAME` and `DESTINATION_API_KEY` appropriately.

Run the script:  `python2 transfer_image.py`

Notes
-----

If you just want to move an image from one account to another in the same region, there are [faster ways](http://docs.rackspace.com/images/api/v2/ci-devguide/content/image-sharing.html) to do this.

It will take many hours for this process to finish.  If you're running this script on a remote server over SSH, be sure to start it in `tmux` or `screen`.

The performance of this script could likely be improved by splitting the transfer of the partial image files from one Cloud Files region to the other into multiple threads.
