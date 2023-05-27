
# Houdini Stable-Diffusion via hda
## Overview
*This hda is a concept as of **v1.3** only allows txt2img with some features not yet implemented (HiRes) and requires the webui to be reachable via the houdini app its installed on (This can be local or over the internet)*

This HDA allows Houdini to communicate with the WebUI to generate images that are then returned to the Host app and saved. *(These settings are defined inside the HDAs User Interface)*
![hdasd_screencap1](https://github.com/SideswipeeZ/houdini-stable-diffusion-hda/blob/main/hdasd_screencap1.PNG)
## Installation
*NOTE: This HDA was created using Houdini 19.5.439 Python 3.9 and may not work with python 2 builds.*

To install this, Download the .HDA file and place it inside your houdini environment folder user the otls folder. (e.g. ~Documents\houdini19.5\otls) 
*(If you do not have an otls folder, make one.)*

If you have a custom location, you can add this to the otl scanpath environment for houdini: **HOUDINI_OTLSCAN_PATH**

## How to Use
To use this you will first need to have access to the Automatic1111 Stable Diffusion WebUi or equivalent that allows api communication. This can be done by adding -api to the webui.

Example:
***COMMANDLINE_ARGS= --api***

By Default the IP will be set to localhost (**127.0.0.1**) and the port is set to **7680**, However the Port is not a Mandatory Field if you have a URL for the Web or have a custom DNS entry for the program.

The HDA is located in OBJ Level. *(Under Digital Assets with the name Stablediffusion)*
On Creation of the HDA, the viewport will load a 512x512 Default Image loaded in an Internal COPNET. This is where the results will be shown. The Settings for these are under the Geometey Settings Option in the HDA UI.

To Connect to the WebUI enter the HOST/PORT options in the HDA and Press Connect. 
This will attempt to connect to the WebUI and if sucessful will unlock more UI options.

Once you have seletected the options you'd like to change and run the process, Scroll to the RUN button to execute the job for the WebUI to generate and return the result. This result will be saved to a location also sepficifed in the HDA Field (*sd_saveDir*) labeled as Save Directory in the HDA UI.

# Future Plans
* Allow support for img2img
* Add support for ControlNet
* Add Support for HiRes Fix
* Add Batch Options
* Add Progress Feedback to Houdini Interrupt Box
* Clean-up Code from Concept Testing

# Licence
MIT
