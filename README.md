# Pixel raw image stacker for Immich
This is a script I wrote up to run as a cron job to stack JPEG and RAW images from a Pixel.

# How does this work

The script pulls down a list of all albums and then iterates through them to create a list of all assets. Once I have that list I separate the files by the MIME type as reported by Immich. Then I look at the original file name of these images and match the first segment like this "PXL_20260103_192003989" between the JPEG and RAW images I called this segment the id throughout this script. Once I have this list of matching file names I iterate through all of the existing stacks in Immich making sure the UUID issued by Immich doesn't match any of the files I've selected. I then stacked the remaining files.

One limitation I did observe in this method is that the count of all the assets I get by listing out all the albums does not match with the asset count Immich reports. I'm not entirely sure what the cause of this discrepancy is but in my testing it didn't seem to affect the stacking of my images.

# API Permissions needed
asset.read
album.read
stack.create
stack.read