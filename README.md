# Alexa Pool Control

A Python script that allows an Amazon Alexa to interpret voice commands to operate an iAqualink pool control system by Zodiac Pool Systems.

# Prerequisites

Requires Flask, Selenium, and a PhantomJS executable.

`pip install flask`

`pip install selenium`

PhantomJS is a portable, invisible web browser that the script uses to communicate with iAqualink.

[Download PhantomJS here](http://phantomjs.org/download.html) and place the extracted phantomjs.exe file in the same directory as the Python script.

# IFTTT Setup

This script uses IFTTT.com to communciate with the Amazon Alexa. You will have to create an IFTTT service for every command to be said to your Alexa ("Alexa, trigger pool on" or "Alexa, trigger hot tub off", etc.)

To begin, create an IFTTT applet triggered by Amazon Alexa - Say a specific phrase, and set it up for the command you want to be executing.

Then choose the Webhooks action service. 

### Webhooks 

The URL should be set to your IP address. IFTTT.com is going to send an HTTP POST request to port 3737 on this IP address.

#### If neccessary, on your router forward the port TCP 3737 to the computer running the Python script.

![alt text](http://i.imgur.com/v0o4PFB.png "IFTTT Webhooks service details")

The method of the request is POST.

The content type is application/json.

### Request JSON Body

The body of this request must be formatted correctly as a JSON table. This is what a correctly formatted request contains:

`{ "key" : "<YOUR KEY HERE>", "device" : "<DEVICE HERE>", "mode" : "<MODE HERE>" }`

The `key` field contains the same key as the one defined in the string atop the Python script (default 555).

The `device` field contains the name of the device being targeted: TUB, POOL, LIGHTS, FEATURE, BUBBLES, or ALL.

The `mode` field contains the desired state of the device: ON or OFF.

# Warning

## This script is partially incomplete.

This script attempts to navigate the web interface for iAqualink. Depending on your pool equipment, some buttons in the webpages may be out of order causing the script to malfunction. 
If everything appears to be setup correctly and your pool is being controlled incorrectly, contact me!

