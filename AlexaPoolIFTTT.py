# Amazon Alexa to iAquaLink Pool Control
# Evan Greavu - Updated August 13th 2017
# Version 1.11
# Version info: Automatic timer functionality improved

### AQUALINK LOGIN
### IMPORTANT!
### Set the login information to your iAqualink Zodiac pool systems account here.
AQUA_USERNAME = 'IAQUALINK_USERNAME'
AQUA_PASSWORD = 'IAQUALINK_PASSWORD'

### REQUEST KEY
### IMPORTANT!
### Set this key to anything you want, then set your IFTTT requests to send this key in the json body.
### More information is on the AlexaPoolIFTTT Github README.
MY_KEY = '555'

# TIMING
# Automatically turns the lights on and off per schedule.

AUTO_LIGHTING_HOURS_START = 19 # Time when the lights will turn on in 24hr time. 20 is 8 PM.
                               # -1 to disable timer functionality completely.

AUTO_LIGHTING_HOURS_END = 3 # Time when the lights turn off in 24hr time. 3 is 3 AM.

#######################################################################################################

# System
import os
import time
import threading

# Flask
from flask import Flask, request
app = Flask(__name__)

# Selenium Interactions
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium import common

# Selenium Timing
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# BROWSER INTERACTION

AQUA_URL = 'https://iaqualink.zodiacpoolsystems.com/start/mobile/?actionID=AlzZVnPMfHDU5&lang=en'
AQUA_TOGGLE_ON = 'https://iaqualink.zodiacpoolsystems.com/files/images/aux_0_1.png'
AQUA_TOGGLE_OFF = 'https://iaqualink.zodiacpoolsystems.com/files/images/aux_0_0.png'
AQUA_TOGGLE_ALTERNATE = 'https://iaqualink.zodiacpoolsystems.com/files/images/aux_0_3.png'


def newBrowser():
    path = os.path.abspath(os.path.dirname(__file__)) + '/phantomjs.exe'
    new_browser = None

    try:
        new_browser = webdriver.PhantomJS(path)
        return new_browser

    except:
        print ('CRITICAL ERROR: phantomjs.exe not found in directory of this script.\n'
               'Please download and place a copy of phantomjs.exe in the same directory as this script.')

    finally:
        return new_browser


def openAqua(browser):
    browser.get(AQUA_URL)
    if 'iAquaLink Email Address:' in browser.page_source:
        assert 'Sign In' in browser.page_source
        print ('Logging in to iAqualink...')
        userID = browser.find_element_by_id('userID')
        userPassword = browser.find_element_by_id('userPassword')
        userID.clear()
        userID.send_keys(AQUA_USERNAME)
        userPassword.clear()
        userPassword.send_keys(AQUA_PASSWORD)
        userPassword.send_keys(Keys.RETURN)

        try:
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "spa_pump_state")))
            return browser

        except common.exceptions.TimeoutException:
            print ('CRITICAL: iAqualink login information is incorrect.')
            quit()


# When an event is triggered, check the status of BROWSER, the global browser variable for PhantomJS
# If not logged in, instantiate a new Aqua browser and update BROWSER accordingly.
global BROWSER
print ("Initializing...")
BROWSER = openAqua(newBrowser())
print ("Successfully logged into iAqualink.")

def refreshBROWSER():
    global BROWSER
    BROWSER.refresh()
    if "iAquaLink Email Address:" in BROWSER.page_source:
        print ("Logging into a new BROWSER.")
        BROWSER.quit()
        BROWSER = openAqua(newBrowser())


# AUTOMATIC TIMING

def getHour():
    return int(time.strftime("%H"))

def isNight():
    hour = int(getHour())
    if hour <= AUTO_LIGHTING_HOURS_END or hour >= AUTO_LIGHTING_HOURS_START:
        return True
    else:
        return False

def timerLoop():
    print ('Timer loop started.')
    while True:
        if isNight():
            print ('It\'s nighttime! Automatically turning on the lights...')
            lightsOn()
        else:
            print ('It\'s daytime! Automatically turning off the lights...')
            lightsOff()
        time.sleep(60)

def startTimerLoop():
    t = threading.Thread(target=timerLoop)
    t.start()


# BROWSER FUNCTIONALITY

def checkElementToggle(element):
    imgSrc = element.get_attribute("src")
    if imgSrc == AQUA_TOGGLE_ON or imgSrc == AQUA_TOGGLE_ALTERNATE:
        return True
    elif imgSrc == AQUA_TOGGLE_OFF:
        return False
    else:
        print ("Error: Unknown state derived from element " + element.get_attribute("id") + " in checkElementToggle.")

def goToHome(browser=BROWSER):
    if "Spa Mode" not in browser.page_source:
        homeButton = browser.find_element_by_link_text("Home")
        homeButton.click()
    WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, "spa_pump_state")))
    WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, "pool_pump_state")))
    WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, "spa_heater_state")))
    WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, "pool_heater_state")))

def goToDevices(browser=BROWSER):
    if "Jet Pump" not in browser.page_source:
        devicesButton = browser.find_element_by_link_text("Devices")
        devicesButton.click()
    WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, "aux_1")))
    WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, "aux_2")))
    WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, "aux_3")))


# DEVICE INTERACTIONS
# Returns:
#   0 == No toggle(s) needed
#   1 == Toggle(s) completed
def hotTubOn(browser=BROWSER):
    goToHome(browser)
    spaButton = browser.find_element_by_id("spa_pump_state")
    heatButton = browser.find_element_by_id("spa_heater_state")
    if checkElementToggle(spaButton) is True:
        if checkElementToggle(heatButton) is True:
            return 0
        else:
            heatButton.click()
            if isNight(): lightsOn(browser)
            print ("Hot tub was already on, but the heater is now on.")
            return 1
    else:
        spaButton.click()
        if checkElementToggle(heatButton) is False:
            heatButton.click()
        if isNight(): lightsOn(browser)
        print ("Hot tub turned on.")
        return 1

def hotTubOff(browser=BROWSER):
    bubblesOff(browser)
    goToHome(browser)
    spaButton = browser.find_element_by_id("spa_pump_state")
    heatButton = browser.find_element_by_id("spa_heater_state")
    if checkElementToggle(spaButton) is False:
        return 0
    else:
        spaButton.click()
        if checkElementToggle(heatButton) is True:
            heatButton.click()
        print ("Hot tub turned off.")
        return 1

def poolOn(browser=BROWSER):
    hotTubOff(browser)
    goToHome(browser)
    poolButton = browser.find_element_by_id("pool_pump_state")
    if checkElementToggle(poolButton) is True:
        return 0
    else:
        poolButton.click()
        print ("Pool turned on.")
        if isNight(): lightsOn()
        return 1

def poolOff(browser=BROWSER):
    goToHome(browser)
    poolButton = browser.find_element_by_id("pool_pump_state")
    if checkElementToggle(poolButton) is False:
        return 0
    else:
        poolButton.click()
        print ("Pool turned off.")
        return 1

def lightsOn(browser=BROWSER):
    goToDevices(browser)
    lightsButton = browser.find_element_by_id("aux_3")
    if checkElementToggle(lightsButton) is True:
        return 0
    else:
        lightsButton.click()
        print ("Lights turned on.")
        return 1

def lightsOff(browser=BROWSER):
    goToDevices(browser)
    lightsButton = browser.find_element_by_id("aux_3")
    if checkElementToggle(lightsButton) is False:
        return 0
    else:
        lightsButton.click()
        print ("Lights turned off.")
        return 1

def featureOn(browser=BROWSER):
    goToDevices(browser)
    featureButton = browser.find_element_by_id("aux_2")
    if checkElementToggle(featureButton) is True:
        return 0
    else:
        featureButton.click()
        print ("Water feature turned on.")
        return 1

def featureOff(browser=BROWSER):
    goToDevices(browser)
    featureButton = browser.find_element_by_id("aux_2")
    if checkElementToggle(featureButton) is False:
        return 0
    else:
        featureButton.click()
        print ("Water feature turned off.")
        return 1

def bubblesOn(browser=BROWSER):
    goToDevices(browser)
    bubblesButton = browser.find_element_by_id("aux_1")
    if checkElementToggle(bubblesButton) is True:
        return 0
    else:
        bubblesButton.click()
        print ("Bubbles turned on.")
        return 1

def bubblesOff(browser=BROWSER):
    goToDevices(browser)
    bubblesButton = browser.find_element_by_id("aux_1")
    if checkElementToggle(bubblesButton) is False:
        return 0
    else:
        bubblesButton.click()
        print ("Bubbles turned off.")
        return 1

def allOff(browser=BROWSER):
    print ("Turning all off.")
    return (hotTubOff(browser),
        poolOff(browser),
        lightsOff(browser),
        featureOff(browser),
        bubblesOff(browser))

def allOn(browser=BROWSER):
    print ("Turning all on.")
    return (hotTubOn(browser),
        featureOn(browser),
        bubblesOn(browser))


# IFTTT INTERACTION
@app.route('/', methods=['POST'])
def trigger():
    if not request.is_json:
        print ('Invalid request. Please see the wiki for information on setting up IFTTT for use with this script.')
    else:
        json = request.get_json(force=True)
        if json['key'] == MY_KEY:
            refreshBROWSER()
            if json['device'] == 'TUB':
                if json['mode'] == 'ON':
                    result = hotTubOn()
                elif json['mode'] == 'OFF':
                    result = hotTubOff()
            elif json['device'] == 'POOL':
                if json['mode'] == 'ON':
                    result = poolOn()
                elif json['mode'] == 'OFF':
                    result = poolOff()
            elif json['device'] == 'LIGHTS':
                if json['mode'] == 'ON':
                    result = lightsOn()
                elif json['mode'] == 'OFF':
                    result = lightsOff()
            elif json['device'] == 'FEATURE':
                if json['mode'] == 'ON':
                    result = featureOn()
                elif json['mode'] == 'OFF':
                    result = featureOff()
            elif json['device'] == 'BUBBLES':
                if json['mode'] == 'ON':
                    result = bubblesOn()
                elif json['mode'] == 'OFF':
                    result = bubblesOff()
            elif json['device'] == 'ALL':
                if json['mode'] == 'ON':
                    result = allOn()
                elif json['mode'] == 'OFF':
                    result = allOff()
            else:
                print('CRITICAL ERROR! Unspecified device in request JSON: ' + json['device'])
                return 'failure'

            return 'success'

        else:
            print("WARNING!: Request with invalid key attempted to trigger an event: " + json['key'])

    return 'failure'



# RUNNING
if __name__ == "__main__":

    if AUTO_LIGHTING_HOURS_START != -1:
        startTimerLoop()

    app.run(host='0.0.0.0',port='3737')

    print ("CRITICAL: Server stopped unexpectedly!")
    sys.exit(8)
