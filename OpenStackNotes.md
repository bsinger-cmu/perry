# Open  Stack Notes

## Introduction

To access the web GUI go to: 

`https://10.20.20.1`

If over ssh `ssh username@address -L localhost:8000:10.20.20.1:443`. Then go to `https://localhost:8000`

Explore and get a feel for the platform, the GUI is useful but is a simplified version of the API.

Now open the command line and run:

`microstack.openstack image list`

This gives you a list of the images running (also shown in GUI).