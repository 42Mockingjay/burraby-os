from PiicoDev_SSD1306 import * #OLED Module (128x64 pixels)
from PiicoDev_CAP1203 import PiicoDev_CAP1203 #Capacative Touch Sensor
from PiicoDev_Buzzer import PiicoDev_Buzzer #PiicoDev Buzzer
from PiicoDev_TMP117 import PiicoDev_TMP117 #Precision Temperature Sensor
from PiicoDev_RGB import PiicoDev_RGB #PiicoDev RGB
from PiicoDev_Unified import sleep_ms # cross-platform-compatible sleep
import urllib.request
import json
import os
import pygame
import tinytuya
import requests

"""
RGB Bulb Device
"""
try:
    d = tinytuya.BulbDevice('bfe069512b7cd73a54r7ac', '192.168.1.218', 'ede6d8f5672611e0')
    d.set_version(3.3)  # IMPORTANT to set this regardless of version
    data = d.status()
except:
    print("Lights are turned off")

touchSensor = PiicoDev_CAP1203(sensitivity=5, touchmode='single')
display = create_PiicoDev_SSD1306()
leds = PiicoDev_RGB() # initialise the LED module with conservative default brightness
tempSensor = PiicoDev_TMP117() # initialise the sensor
buzz = PiicoDev_Buzzer(volume=2) # volume may be 0, 1 or 2 (loudest)
pygame.mixer.init()

# Define some colours
red = [255,0,0]
green = [0,255,0]
blue = [0,0,255]
yellow = [255,255,0]
magenta = [255,0,255]
cyan = [0,255,255]
white = [255,255,255]
black = [0,0,0]

# Define some note-frequency pairs
notes = {'C4':262,
         'Db':277,
         'D' :294,
         'Eb':311,
         'E' :330,
         'F' :349,
         'Gb':370,
         'G' :392,
         'Ab':415,
         'A' :440,
         'Bb':466,
         'B' :494,
         'C5':523,
         'rest':0, # zero Hertz is the same as no tone at all
         }

page = "home"

home_page = 0
home_content = ["Music", "Neopixels", "Other lights", "Weather", "System", "Buzzer"]

music_page = 0
music_content = ["Caves&Cliffs OST", "Nether OST", "Volume Alpha", "Life in Stereo", "The Planets Suite - Jupiter"]

neopixels_page = 0
neopixels_content = ["Off", "Non-Music Effects", "Music Effects"]
effects_page = 0
def getList(dict):
    list = []
    for value in dict.values():
        list.append(value)
    return list
effects_content = getList(requests.get('http://192.168.1.90:80/api/resources/effects').json()["non_music"])
music_effects_page = 0
music_effects_content = getList(requests.get('http://192.168.1.90:80/api/resources/effects').json()["music"])

other_lights_page = 0
other_lights_content = ["Off", "On", "Scenes"]
scenes_page = 0
scenes_content = ["White"]

weather_page = 0
weather_content = ["Atmospheric", "Wind", "Forecast"]

system_page = 0
system_content = ["Reboot", "Shutdown", "IP Address"]

buzzer_page = 0
buzzer_content = ["Tune 1", "Rue's whistle"]

display.fill(0) #Fill the screen with black
display.text("Welcome!", 32,29, 1)
display.show()

def music_player(dir, name):
    global page
    page = None

    music_list = os.listdir(dir)
    print(music_list)
    track_num = 0
    pygame.mixer.music.set_volume(1)
    os.system(f"amixer cset numid=3 0%")
    volume = 0
    leds.clear()

    def display_song():
        display.fill(0) #Fill the screen with black
        display.text("Playing:",0,0,1)
        display.text(name,0,15,1)
        try:
            track_name = music_list[track_num][:-4]
            if len(track_name) > 15:
                display.text(f"{track_name[:15]}-",0,30,1)
                display.text(f"{track_name[15:]}",0,45,1)
            else:
                display.text(track_name,0,30,1)

        except:
            print("Error displaying song name")
        display.show()

    while True:
        display_song()
        pygame.mixer.music.load(f"{dir}/{music_list[track_num]}")
        pygame.mixer.music.play()
        print("playing...")
        while pygame.mixer.music.get_busy():
            status = touchSensor.read()
            #If home button pressed
            if status[1] == 1:
                pygame.mixer.music.stop()
                leds.clear()
                page = "home"
                break
            #If next button pressed
            if status[2] == 1:
                break
            #If select/volume button pressed
            if status[3] == 1:
                volume += 10
                if volume == 60:
                    volume = 0
                if volume == 10:
                    leds.clear()
                    leds.setBrightness(50)
                    leds.setPixel(2, blue)
                    leds.show()
                elif volume == 20:
                    leds.clear()
                    leds.setBrightness(50)
                    leds.setPixel(1, green)
                    leds.setPixel(2, white)
                    leds.show()
                elif volume == 30:
                    leds.clear()
                    leds.setBrightness(50)
                    leds.setPixel(0, red)
                    leds.setPixel(1, white)
                    leds.setPixel(2, white)
                    leds.show()
                elif volume == 50:
                    leds.clear()
                    leds.setBrightness(50)
                    leds.fill(magenta)
                    leds.show()
                elif volume == 0:
                    leds.clear()

                os.system(f"amixer cset numid=3 {volume}%")
                display.fill(0) #Fill the screen with black
                display.text("Volume:",0,0,1)
                display.text(f"{volume}%",0,15,1)
                display.show()

                display_song()

                leds.setBrightness(15)
                leds.show()

        track_num+=1
        if page == "home":
            pygame.mixer.music.stop()
            leds.clear()
            break
        if track_num == len(music_list):
            pygame.mixer.music.stop()
            page = "music"
            leds.clear()
            break

        print("Onto next song.")
sleep_ms(1000) #Sleep for one second

def draw_page(name, the_list, list_number):
    display.fill(0) #Fill the screen with black
    display.text(f"{name}", 0,0, 1)
    display.text("__________________",0,4,1)
    display.text("P"+str(list_number+1),110,0,1)
    display.text(the_list[list_number],0,20,1)
    display.show()

while True:
    # Example: Display touch-pad statuses
    status = touchSensor.read()
    #print("Touch Pad Status: " + str(status[1]) + "  " + str(status[2]) + "  " + str(status[3]))

    #If home button pressed
    if status[1] == 1:
        print("Home button pressed")
        if page == "home":
            home_page = 0
        page = "home"

    #If next button pressed
    if status[2] == 1:
        print("Next button pressed")
        if page == "home":
            home_page+=1
            if home_page>(len(home_content)-1):
                home_page = 0
        if page == "music":
            music_page+=1
            if music_page>(len(music_content)-1):
                music_page = 0
        if page == "neopixels":
            neopixels_page+=1
            if neopixels_page>(len(neopixels_content)-1):
                neopixels_page = 0
        if page == "effects":
            effects_page+=1
            if effects_page>(len(effects_content)-1):
                effects_page = 0
        if page == "music_effects":
            music_effects_page+=1
            if music_effects_page>(len(music_effects_content)-1):
                music_effects_page = 0
        if page == "other_lights":
            other_lights_page+=1
            if other_lights_page>(len(other_lights_content)-1):
                other_lights_page = 0
        if page == "scenes":
            scenes_page+=1
            if scenes_page>(len(scenes_content)-1):
                scenes_page = 0
        if page == "weather":
            weather_page+=1
            if weather_page>(len(weather_content)-1):
                weather_page = 0
        if page == "system":
            system_page+=1
            if system_page>(len(system_content)-1):
                system_page = 0
        if page == "buzzer":
            buzzer_page+=1
            if buzzer_page>(len(buzzer_content)-1):
                buzzer_page = 1

    #If select button pressed
    if status[3] == 1:
        print("Select button pressed")

        if page=="home":
            if home_page == 0:
                page="music"
            elif home_page == 1:
                page="neopixels"
            elif home_page == 2:
                page="other_lights"
            elif home_page == 3:
                page="weather"
            elif home_page == 4:
                page="system"
            elif home_page == 5:
                page="buzzer"

        elif page=="neopixels":
            if neopixels_page == 0: #Turn off
                page = None
                response = requests.post('https://httpbin.org/post', data = {'key':'value'})
                display.fill(0) #Fill the screen with black
                display.text("Power toggle:",0,0,1)
                display.text("Off",0,15,1)
                display.show()
                sleep_ms(1000)
                page = "neopixels"
            if neopixels_page == 1: #Non-Music Effect
                page = "effects"
            if neopixels_page == 2: #Music Effect
                page = "music_effects"
        elif page=="effects":
            def getList(dict):
                list = []
                for key in dict.keys():
                    list.append(key)
                return list
            effect = getList(requests.get('http://192.168.1.90:80/api/resources/effects').json()["non_music"])[effects_page]

            query = {
                "device": "device_0",
                "effect": effect
            }
            r = requests.post('http://192.168.1.90:80/api/effect/active', json=query)

            display.fill(0) #Fill the screen with black
            display.text("Effect",0,0,1)
            display.text(effects_content[effects_page],0,15,1)
            display.show()
            sleep_ms(1000)
            page = "neopixels"
        elif page=="music_effects":
            def getList(dict):
                list = []
                for key in dict.keys():
                    list.append(key)
                return list
            effect = getList(requests.get('http://192.168.1.90:80/api/resources/effects').json()["music"])[music_effects_page]

            query = {
                "device": "device_0",
                "effect": effect
            }
            r = requests.post('http://192.168.1.90:80/api/effect/active', json=query)

            display.fill(0) #Fill the screen with black
            display.text("Music Effect",0,0,1)
            display.text(effects_content[effects_page],0,15,1)
            display.show()
            sleep_ms(1000)
            page = "neopixels"

        elif page=="other_lights":
            if other_lights_page == 0: #Turn off
                page = None
                try:
                    d.turn_off()
                    display.fill(0) #Fill the screen with black
                    display.text("Power toggle:",0,0,1)
                    display.text("Off",0,15,1)
                    display.show()
                    sleep_ms(1000)
                except:
                    display.text("Error",0,0,1)
                    display.text("Lights are offline",0,15,1)
                    display.show()
                    sleep_ms(1000)
                page = "other_lights"
            if other_lights_page == 1: #Turn on
                page = None
                try:
                    d.turn_on()
                    display.fill(0) #Fill the screen with black
                    display.text("Power toggle:",0,0,1)
                    display.text("On",0,15,1)
                    display.show()
                    sleep_ms(1000)
                except:
                    display.text("Error",0,0,1)
                    display.text("Lights are offline",0,15,1)
                    display.show()
                    sleep_ms(1000)
                page = "other_lights"
            if other_lights_page == 2: #Scenes
                page = "scenes"

        elif page=="weather":
            if weather_page == 0: #Atmospheric
                page = None
                # Aeris Weather API
                print("Sending request...")
                request = urllib.request.urlopen('https://api.aerisapi.com/observations/-37.80162551497153,145.09654329658505?format=json&filter=pws&limit=1&fields=id,ob.tempC,ob.humidity,ob.windSpeedKPH,ob.windDir,ob.weather&client_id=FEgU5C97UlUl6b3PLKKo2&client_secret=XBwFU4gAyEp80vYIpuHSqkwx8ddlOoXONXAXcbxo')
                response = request.read()
                json_response = json.loads(response)
                if json_response['success']:
                    print("Done\n")
                    id = json_response["response"]["id"]
                    ob = json_response["response"]["ob"]
                    tempC = ob["tempC"]
                    humidity = ob["humidity"]
                    windSpeedKPH = ob["windSpeedKPH"]
                    windDir = ob["windDir"]
                    weather = ob["weather"]

                    inTemp = round(tempSensor.readTempC(),2) # Celsius

                    display.fill(0) #Fill the screen with black
                    display.text(f"{weather}",0,0,1)
                    display.text(f"Humidity: {humidity}%",0,15,1)
                    display.text(f"OutTemp: {tempC}C",0,30,1)
                    display.text(f"InTemp: {inTemp}C",0,45,1)
                    display.show()
                else:
                    print("An error occurred: %s" % (json['error']['description']))
                    request.close()

            if weather_page == 1: #Wind
                page = None
                # Aeris Weather API
                print("Sending request...")
                request = urllib.request.urlopen('https://api.aerisapi.com/observations/-37.80162551497153,145.09654329658505?format=json&filter=pws&limit=1&fields=id,ob.tempC,ob.humidity,ob.windSpeedKPH,ob.windDir,ob.weather&client_id=FEgU5C97UlUl6b3PLKKo2&client_secret=XBwFU4gAyEp80vYIpuHSqkwx8ddlOoXONXAXcbxo')
                response = request.read()
                json_response = json.loads(response)
                if json_response['success']:
                    print("Done\n")
                    id = json_response["response"]["id"]
                    ob = json_response["response"]["ob"]
                    tempC = ob["tempC"]
                    humidity = ob["humidity"]
                    windSpeedKPH = ob["windSpeedKPH"]
                    windDir = ob["windDir"]
                    weather = ob["weather"]

                    display.fill(0) #Fill the screen with black
                    display.text(f"{weather}",0,0,1)
                    display.text(f"Wind speed: {windSpeedKPH}km/h",0,15,1)
                    display.text(f"Wind dir: {windDir}",0,30,1)
                    display.show()
                else:
                    print("An error occurred: %s" % (json['error']['description']))
                    request.close()

            if weather_page == 2: #Forecast
                page=None
                #Aeris Weather API
                request = urllib.request.urlopen('https://api.aerisapi.com/forecasts/-37.801600083196746,145.09631799102226?format=json&filter=daynight&limit=1&fields=periods.weather,periods.maxTempC,periods.minTempC,periods.pop,periods.precipMM,periods.windSpeedMaxKPH&client_id=FEgU5C97UlUl6b3PLKKo2&client_secret=XBwFU4gAyEp80vYIpuHSqkwx8ddlOoXONXAXcbxo')
                response = request.read()
                json_response = json.loads(response)
                if json_response['success']:
                    #print(json_response["response"][0]["periods"][0])
                    ob=json_response["response"][0]["periods"][0]
                    weather=ob["weather"]
                    maxTempC=ob["maxTempC"]
                    minTempC=ob["minTempC"]
                    precip_prob=ob["pop"]
                    precipMM=ob["precipMM"]
                    windSpeedMaxKPH=ob["windSpeedMaxKPH"]

                    display.fill(0) #Fill the screen with black
                    display.text(f"Max Temp: {maxTempC}C",0,0,1)
                    display.text(f"Min Temp: {minTempC}C",0,15,1)
                    display.text(f"Rain:{precipMM}mm({precip_prob}%)",0,30,1)
                    display.show()
                else:
                    print("An error occurred: %s" % (json['error']['description']))
                    request.close()

        elif page=="system":
            if system_page == 0:
                page=None
                display.fill(1) #Fill the screen with black
                display.text(f"Rebooting...",0,7,0)
                display.show()
                sleep_ms(1000) #Sleep for 1 second
                os.system("sudo reboot")
            elif system_page == 1:
                page = None
                display.fill(1) #Fill the screen with black
                display.text(f"Shutdown",0,7,0)
                display.show()
                sleep_ms(1000) #Sleep for 1 second
                os.system("sudo shutdown")
            elif system_page == 2:
                page = None
                display.fill(1) #Fill the screen with black
                display.text(f"192.168.1.90",0,7,0)
                display.show()

        elif page=="buzzer":
            if buzzer_page == 0:
                page = None

                display.fill(0) #Fill the screen with black
                display.text("Playing:",0,0,1)
                display.text("Tune 1",0,15,1)
                display.show()

                buzz.tone(800, 500) # high tone (800Hz for 500ms)
                sleep_ms(500)

                buzz.tone(400, 500) # low tone (400Hz for 500ms)
                sleep_ms(1500)

                buzz.volume(0) # low volume

                buzz.tone(800) # high tone - continuous
                sleep_ms(500)
                buzz.noTone() # stop playing

                buzz.tone(400) # low tone - continuous
                sleep_ms(500)
                buzz.noTone()
            elif buzzer_page == 1:
                page = None

                display.fill(0) #Fill the screen with black
                display.text("Playing:",0,0,1)
                display.text("Rue's four note",0,15,1)
                display.text("whistle",0,30,1)
                display.show()

                # define a melody - two-dimensional list of notes and note-duration (ms)
                melody = [['Db',    500],
                          ['F',    500],
                          ['Eb',   500],
                          ['Gb', 500]
                          ]

                # play the melody
                for x in melody:
                    noteName = x[0] # extract the note name
                    duration = x[1] # extract the duration
                    buzz.tone(notes[noteName], duration)
                    sleep_ms(duration)

        elif page == "music":
            if music_page == 0:
                music_player("/home/pi/Desktop/CavesCliffsOST", music_content[0])
            elif music_page == 1:
                music_player("/home/pi/Desktop/NetherUpdateOST", music_content[1])
            elif music_page == 2:
                music_player("/home/pi/Desktop/VolumeAlpha", music_content[2])
            elif music_page == 3:
                music_player("/home/pi/Desktop/LifeInStereo", music_content[3])
            elif music_page == 4:
                music_player("/home/pi/Desktop/PlanetsSuiteJupiter", music_content[4])


    if page == "home":
        draw_page("Home", home_content, home_page)
    elif page == "music":
        draw_page("Music", music_content, music_page)
    elif page == "neopixels":
        draw_page("Neopixels", neopixels_content, neopixels_page)
    elif page == "effects":
        draw_page("Effects", effects_content, effects_page)
    elif page == "music_effects":
        draw_page("Music Effects", music_effects_content, music_effects_page)
    elif page == "other_lights":
        draw_page("Other lights", other_lights_content, other_lights_page)
    elif page == "scenes":
        draw_page("Scenes", scenes_content, scenes_page)
    elif page == "weather":
        draw_page("Weather", weather_content, weather_page)
    elif page == "system":
        draw_page("System", system_content, system_page)
    elif page == "buzzer":
        draw_page("Buzzer", buzzer_content, buzzer_page)
