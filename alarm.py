from PIL import Image, ImageDraw, ImageFont
from spidev import SpiDev
import ILI9486 as LCD
import os
from datetime import datetime
import time
import netifaces as ni
import RPi.GPIO as GPIO
import random
import subprocess
from decimal import Decimal
import os
import signal

if os.path.exists(f"/home/{os.getlogin()}/alarm/files") == False:
    os.mkdir(f"/home/{os.getlogin()}/alarm/files")
    os.mkdir(f"/home/{os.getlogin()}/alarm/files/audio")
    subprocess.Popen(["touch", f"/home/{os.getlogin()}/alarm/files/alarms.txt"])

#alarm format: 05-07-2025 05:00 PM

button_input = 21
output_pin = 20

GPIO.setmode(GPIO.BCM)
GPIO.setup(output_pin, GPIO.OUT)
GPIO.setup(button_input, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.output(output_pin, GPIO.HIGH)

spi = SpiDev(0, 0)
spi.mode = 0b10
spi.max_speed_hz=64000000
lcd = LCD.ILI9486(dc=24, rst=25, spi=spi).begin()
lcd.idle(True)

fontsize = 72
ni.ifaddresses("wlan0")
ip = ni.ifaddresses("wlan0")[2][0]['addr']
print(ip)

currentTime = ""
activeAlarms = 0
alarmActive = False
initialVolume = Decimal("0.4")
volume = initialVolume
music_pid = 0
foundSongs = False

def updateScreen(active, nextAlarm):
    global check_speaker
    global currentTime
    image = Image.new("RGB", (480, 320), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", fontsize)
    fontSmall = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 20)
    fontMedium = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 40)
    currentTime = now
    draw.text((0, 0), now, font=font, align="left")
    draw.text((375, 300), ip, font=fontSmall, align="right")
    if nextAlarm != None:
        draw.text((0, 300), f"Next alarm is set for {nextAlarm}", font=fontSmall, align="left")
    else:
        draw.text((0, 300), "No alarms set", font=fontSmall, align="left")
    if "Media-Player" not in os.popen("lsusb").read():
        draw.text((0, 100), "Speaker not detected!!!", font=fontMedium, align="left")
        draw.text((0, 140), "Please plug it in, or unplug and plug it in again", font=fontSmall, align="left")
    if len(os.listdir(f"/home/{os.getlogin()}/alarm/files/audio")) < 1:
        draw.text((0, 180), "No audio found in files/audio", font=fontSmall, align="left")
        draw.text((0, 200), "please put some music in there", font=fontSmall, align="left")
        draw.text((0, 220), "Or alarms will not play any music.", font=fontSmall, align="left")
    if active:
        draw.text((0, 100), "WAKE UP!!!!!!", font=font, align="left")
        if foundSongs == True:
            draw.text((0, 280), f"volume:{volume}", font=fontSmall, align="left")
    lcd.display(image)
    print(f"display updated at {datetime.now().strftime('%d-%m-%Y %I:%M %p')}")

while True:
    now = datetime.now().strftime("%I:%M %p")
    file = open(f"/home/{os.getlogin()}/alarm/files/alarms.txt", "r")
    times = []
    for line in file:
        line = line[:-1]
        try:
            times.append(datetime.strptime(line, "%m-%d-%Y %I:%M:%S %p"))
        except ValueError:
            print(f"Error parsing date \"{line}\", skipping it")
    file.close()
    if now != currentTime:
        if len(times) > 0:
            if times[0].second == 0:
                nextAlarm = times[0].strftime("%I:%M %p")
            else:
                nextAlarm = times[0].strftime("%I:%M:%S %p")
        else:
            nextAlarm = None
        updateScreen(alarmActive, nextAlarm)
    if len(times) > 0:
        for i in times:
            if i <= datetime.now():
                if activeAlarms >= 1 and foundSongs == True:
                    volume += Decimal("0.1")
                    subprocess.Popen(["playerctl", "--all-players", "volume", f"{volume}"])
                    print(f"Volume increased by 0.1, to {volume}")
                if alarmActive == False:
                    songs = []
                    for i in os.listdir(f"/home/{os.getlogin()}/alarm/files/audio"):
                        songs.append(i)
                    if foundSongs == False:
                        if len(songs) > 0:
                            foundSongs = True
                    if foundSongs == True:
                        subprocess.Popen(["cvlc", "--aout=alsa", "--alsa-audio-device", "hw:1,0", f"/home/{os.getlogin()}/alarm/files/audio/{random.choice(songs)}"])
                        time.sleep(0.5)
                        process = subprocess.Popen(["playerctl", "--all-players", "volume", f"{volume}"])
                        music_pid = process.pid
                file = open(f"/home/{os.getlogin()}/alarm/files/alarms.txt", "w")
                times.pop(0)
                activeAlarms += 1
                if alarmActive == False:
                    alarmActive = True
                if len(times) > 0:
                    if times[0].second == 0:
                        nextAlarm = times[0].strftime("%I:%M %p")
                    else:
                        nextAlarm = times[0].strftime("%I:%M:%S %p")
                else:
                    nextAlarm = None
                updateScreen(alarmActive, nextAlarm)
                for i in times:
                    file.write(i.strftime("%m-%d-%Y %I:%M:%S %p") + "\n")
                file.close()

    if GPIO.input(button_input) == GPIO.HIGH:
        print("BUTTON!!!")
        if alarmActive:
            volume = initialVolume
            activeAlarms = 0
            alarmActive = False
            if foundSongs == True:
                subprocess.Popen(["playerctl", "--all-players", "volume", f"{initialVolume}"])
                subprocess.Popen(["playerctl", "--all-players", "stop"])
                if music_pid != 0:
                    os.kill(music_pid, signal.SIGTERM)
                    subprocess.Popen(["killall", "vlc"])
                    print(f"Killed vlc process with PID {music_pid}")
                    music_pid = 0
            if len(times) > 0:
                if times[0].second == 0:
                    nextAlarm = times[0].strftime("%I:%M %p")
                else:
                    nextAlarm = times[0].strftime("%I:%M:%S %p")
            else:
                nextAlarm = None
            updateScreen(alarmActive, nextAlarm)
    time.sleep(1)
