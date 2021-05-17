#!/usr/bin/env python
# -*- coding: utf-8 -*-
# > - > - > - >  > - > - > - > <
#    IBB TRAY - by steffenu    ^
# > - > - > - >  > - > - > - > ^
import os
import configparser
import datetime
from random import choice
import re
import threading
import requests
import urllib.request
import PyPDF2
from PySide6.QtWidgets import QMainWindow, QSystemTrayIcon

# import config # config.py
import schedule
import time
from notifypy import Notify #pip install notify-py
from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import QThread, SIGNAL, QObject, QEvent
from bs4 import BeautifulSoup

import test_rc # to load image correctly in windows

#import locale # Let's set a non-US locale
#https://stackoverflow.com/questions/955986/what-is-the-correct-way-to-set-pythons-locale-on-windows
#locale.setlocale(locale.LC_ALL, '')
#locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

import feiertag_diese_woche
import week_detector
import colored_logging

log = colored_logging.colored_logger()

"""
DEBUG
INFO
WARNING
ERROR
CRITICAL
"""

FORMAT = "[ %(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"

#logging.basicConfig(level=logging.DEBUG , format=FORMAT)

#--------------------
# 0 .ACTUALITY CHECK
#--------------------
# Haben wir die aktuellen Daten für diese Woche bereits ?
# JA = kein Login /  NEIN = LOGIN
# Wir schauen dafür  in unsere Gespeicherten Datensätze !



#--------------------
# 0 .  LOGIN CREDENTIALS
#--------------------
# Die Login Daten aus config.py geladen ( nickname , password)
# Datenschutz ...

def read_config():
    Config = configparser.ConfigParser()
    Config.read("config.ini")

    config_list = []
    for each_section in Config.sections():
        for (each_key, each_val) in Config.items(each_section):
            config_list.append(each_val)
    return config_list


config_data = read_config()

username = config_data[0] # username
password = config_data[1] # password

#--------------------
# 0 .  LOGIN WEB REQUEST
#--------------------
#  application/x-www-form-urlencoded  LOGIN  -  POST request



payload = {'nickname': username, 'pass': password}
headers = {'content-type': 'application/x-www-form-urlencoded'}

r = requests.post("https://us.ibb.com/umschueler/pass/loginlogout.php", data=payload , headers=headers)

#--------------------
# 0 .  WEBSITE PARSEN
#--------------------

soup = BeautifulSoup(r.text, 'html.parser')
vertretungen = soup.find('div', class_='aktuell1') # class
pdf_liste = soup.find('div', id='inhalt1')  # id


log.debug(pdf_liste)
#print(pdf_liste)
#print(vertretungen)


#--------------------
# 1. PDF DOWNLOAD
#--------------------
#
# HARDCODED FOR NOW

rootpath = "https://us.ibb.com/umschueler/daten/US_IT_2020_Sommer_FIAE_B_2021_abKW"

weeknr = week_detector.weeknr()
log.debug(weeknr)
#print(weeknr)
filetype = ".pdf"
url = rootpath + weeknr + filetype
urllib.request.urlretrieve(url, "testing/filename.pdf")

#--------------------
# 2 TEXT EXTRACT
#--------------------

#https://www.geeksforgeeks.org/working-with-pdf-files-in-python/

# creating a pdf file object
pdfFileObj = open('testing/filename.pdf', 'rb')

# creating a pdf reader object
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

# printing number of pages in pdf file
#print(pdfReader.numPages)
log.debug(pdfReader.numPages)

# creating a page object
pageObj = pdfReader.getPage(0)

# extracting text from page
#print(pageObj.extractText())
log.debug(pageObj.extractText())

# closing the pdf file object
pdfFileObj.close()

#--------------------
# 3 REGEX TEXT FORMATTER
#--------------------
# DOING SOME REGEX MAGIC TO EXTRACT INFORMATION

# STEP 1 - SEARCH AND REPLACE
# Theorieunterricht
txt = pageObj.extractText()
x = re.sub("Theorieunterricht", " Theorieunterricht ", txt)
x = re.sub("Praxisunterricht", " Praxisunterricht ", x)
x = re.sub("Mittagspause", " Mittagspause ", x)
x = re.sub("Prüfung", " Prüfung ", x)
x = re.sub("Unterrichtsfrei", " Unterrichtsfrei ", x)
x = re.sub("\d\d:\d\d-\d\d:\d\d", " \g<0> ", x)
x = re.sub("\d\d\smin", "", x)
x = re.sub("US IT 2020 Sommer FIAE B", "", x)

#print(x)
log.debug(x)

# Find all matches

x = re.findall("(Theorieunterricht|Praxisunterricht)(.*?)Uhr", x)
#print("HIER", x )
log.info("PARSED DATA:" + str(x))

data = {}
counter = 0
feiertag = feiertag_diese_woche.feiertag_diese_woche()
wochentag = feiertag[0] # wochentag : z.b Donnerstag
#print("WEEKDAY" ,wochentag )

log.debug("WEEKDAY " + wochentag)
for index , y in enumerate(x):
    y = list(y)
    #print(y[1])
    uhrzeit = re.search("\d\d:\d\d-\d\d:\d\d", y[1]).group()
    start = re.search("\d\d:\d\d-", uhrzeit).group()
    start = re.sub("-","" , start)

    ende = re.search("-\d\d:\d\d", uhrzeit).group()
    ende = re.sub("-","" , ende)

    log.debug(uhrzeit)
    log.debug(y[1])
    #print(uhrzeit)
    #print(y[1])

    if y[0] == "Praxisunterricht":
        fach = "Praxisunterricht"
        lehrer = "Praxisunterricht"

    if y[0] == "Theorieunterricht":
        fach = re.search(".*?/", y[1]).group()
        fach = re.sub("/","" , fach)
        #print(fach)

        #print(fach)
        lehrer = re.search("/\s\w+,\s\w+", y[1]).group()
        lehrer = re.sub("/","" , lehrer)
    else:
        fach = "Praxisunterricht"
        lehrer = "Praxisunterricht"

    #print(lehrer)

    # wenn noch kein key vorhanden ist erstelle ein dic
    # wenn key vorhanden ist dann appende

    #wenn feiertag dann nicht counter erhöhen
    if counter == 0:
        if wochentag == "Montag":
            data.update({'Montag': {index: {'Unterrichtsart':feiertag[1],'Lehrer': feiertag[1], 'Fach': feiertag[1], 'Uhrzeit': "", 'start': feiertag[1], 'ende': feiertag[1]}}})
            data.update({'Dienstag': {index: {'Unterrichtsart':y[0],'Lehrer': lehrer, 'Fach': fach, 'Uhrzeit': uhrzeit, 'start': start, 'ende': ende}}})
            counter += 1
        elif 'Montag' in data.keys():
            data['Montag'][index] = {'Unterrichtsart':y[0],'Lehrer': lehrer, 'Fach': fach, 'Uhrzeit': uhrzeit, 'start': start, 'ende': ende}

        else:
            data.update({'Montag': {index: {'Unterrichtsart':y[0],'Lehrer': lehrer, 'Fach': fach, 'Uhrzeit': uhrzeit, 'start': start, 'ende': ende}}})

    elif counter == 1:
        if wochentag == "Dienstag":
            data.update({'Dienstag': {index: {'Unterrichtsart':feiertag[1],'Lehrer': feiertag[1], 'Fach': feiertag[1], 'Uhrzeit': "", 'start': feiertag[1], 'ende': feiertag[1]}}})
            data.update({'Mittwoch': {index: {'Unterrichtsart':y[0],'Lehrer': lehrer, 'Fach': fach, 'Uhrzeit': uhrzeit, 'start': start, 'ende': ende}}})
            counter += 1

        elif 'Dienstag' in data.keys():
            data['Dienstag'][index] = {'Unterrichtsart':y[0],'Lehrer': lehrer, 'Fach': fach, 'Uhrzeit': uhrzeit, 'start': start, 'ende': ende}

        else:
            data.update({'Dienstag': {index: {'Unterrichtsart':y[0],'Lehrer': lehrer, 'Fach': fach, 'Uhrzeit': uhrzeit, 'start': start, 'ende': ende}}})

    elif counter == 2:
        if wochentag == "Mittwoch":
            data.update({'Mittwoch': {index: {'Unterrichtsart':feiertag[1],'Lehrer': feiertag[1], 'Fach': feiertag[1], 'Uhrzeit': "", 'start': feiertag[1], 'ende': feiertag[1]}}})
            data.update({'Donnerstag': {index: {'Unterrichtsart':y[0],'Lehrer': lehrer, 'Fach': fach, 'Uhrzeit': uhrzeit, 'start': start, 'ende': ende}}})
            counter += 1

        elif 'Mittwoch' in data.keys():
            data['Mittwoch'][index] = {'Unterrichtsart':y[0],'Lehrer': lehrer, 'Fach': fach, 'Uhrzeit': uhrzeit, 'start': start, 'ende': ende}

        else:
            data.update({'Mittwoch': {index: {'Unterrichtsart':y[0],'Lehrer': lehrer, 'Fach': fach, 'Uhrzeit': uhrzeit, 'start': start, 'ende': ende}}})

    elif counter == 3:
        if wochentag == "Donnerstag":
            data.update({'Donnerstag': {index: {'Unterrichtsart':feiertag[1],'Lehrer': feiertag[1], 'Fach': feiertag[1], 'Uhrzeit': "", 'start': feiertag[1], 'ende': feiertag[1]}}})
            data.update({'Freitag': {index: {'Unterrichtsart':y[0],'Lehrer': lehrer, 'Fach': fach, 'Uhrzeit': uhrzeit, 'start': start, 'ende': ende}}})
            counter += 1

        elif 'Donnerstag' in data.keys():
            data['Donnerstag'][index] = {'Unterrichtsart':y[0],'Lehrer': lehrer, 'Fach': fach, 'Uhrzeit': uhrzeit, 'start': start, 'ende': ende}

        else:
            data.update({'Donnerstag': {index: {'Unterrichtsart':y[0],'Lehrer': lehrer, 'Fach': fach, 'Uhrzeit': uhrzeit, 'start': start, 'ende': ende}}})

    elif counter == 4:
        if wochentag == "Freitag":
            data.update({'Freitag': {index: {'Unterrichtsart':feiertag[1],'Lehrer': feiertag[1], 'Fach': feiertag[1], 'Uhrzeit': "", 'start': feiertag[1], 'ende': feiertag[1]}}})

        if 'Freitag' in data.keys():
            data['Freitag'][index] = {'Unterrichtsart':y[0],'Lehrer': lehrer, 'Fach': fach, 'Uhrzeit': uhrzeit, 'start': start, 'ende': ende}

        else:
            data.update({'Freitag': {index: {'Unterrichtsart':y[0],'Lehrer': lehrer, 'Fach': fach, 'Uhrzeit': uhrzeit, 'start': start, 'ende': ende}}})


    if uhrzeit == '15:00-16:00': # neuer tag wenn dieser eintrag gefunden wird
        counter += 1

#print("FORMATTED: ",data)
log.info(data)


#--------------------
#     DATA PICKER
#--------------------
# picks and returns the correct data based on current date and time

def data_picker(data):
    # Example current time = 8.00 Uhr
    # pick data where start = 8.00 Uhr
    # Wir triggern unser schedule  zur genauen startzeit der stunde

    today = datetime.datetime.now()
    uhrzeit_H_M = today.strftime('%H:%M')
    #print(uhrzeit_H_M)
    weekday = today.strftime('%A')
    #print(weekday) # Monday is 0 and Sunday is 6.
    if weekday in data.keys():
        weekday_data = data.get(weekday)
        for x in weekday_data.values():
            #print("xdata",x)
           # print(x['start'], uhrzeit_H_M)
            if x['start'] == uhrzeit_H_M:
                print(" ## NOTIFCATION CREATED ##")
                notifcation(x['Uhrzeit'],x['Fach'])
                naechste_stunde(data) # to set next unit when schedule runs

def naechste_stunde(data):

    # Example current time = 8.00 Uhr
    # pick data where start = 8.00 Uhr
    # Wir triggern unser schedule ja zur genauen startzeit der stunde

    today = datetime.datetime.now()
    uhrzeit_H_M = today.strftime('%H:%M')
    date_time_today = datetime.datetime.strptime(uhrzeit_H_M, '%H:%M')

    #print(uhrzeit_H_M)
    weekday = today.strftime('%A')
    #print(weekday) # Monday is 0 and Sunday is 6.
    if weekday in data.keys():
        weekday_data = data.get(weekday)
        for index,x in enumerate(weekday_data.values()):
            #log.info("weekday values: " + str(weekday_data.values()))
            log.debug("today " + str(date_time_today.time()))
            #print("today",date_time_today.time())
            data_time_start = datetime.datetime.strptime(x['start'], '%H:%M').time()
            data_time_ende = datetime.datetime.strptime(x['ende'], '%H:%M').time()

            mittag_start = datetime.datetime.strptime("12:05", '%H:%M').time()
            mittag_ende = datetime.datetime.strptime("12:35", '%H:%M').time()
            #log.debug(data_time_start +" "+ data_time_ende)
            #print(data_time_start,data_time_ende)
            #print("xdata",x)
            # print(x['start'], uhrzeit_H_M)

            #log.debug(str(date_time_today.time() > data_time_start) +" " + str(date_time_today.time() < data_time_ende))
            #print(date_time_today.time() > data_time_start , date_time_today.time() < data_time_ende)

            # dazwischen oder genau die zeit

            if (date_time_today.time() > data_time_start and date_time_today.time() < data_time_ende or date_time_today.time() == data_time_start ):
                #print("aktuelle stunde : " , x , "index : " + str(index))
                log.info("weekday values: " + str(weekday_data.values()))
                log.info("aktuelle stunde : " + str(x) + " index : " + str(index))
                arraydata = weekday_data.values()
                # https://stackoverflow.com/questions/33674033/python-how-to-convert-a-dictionary-into-a-subscriptable-array
                try:
                    next =list(arraydata)[index+1]

                except:
                    next = {'Unterrichtsart': 'Feierabend', 'Lehrer': 'Feierabend', 'Fach': 'Feierabend', 'Uhrzeit': 'Frei', 'start': '15:00', 'ende': 'Frei'}


                try:
                    #print("RUN ACTION")
                    global option1
                    global option2
                    option1.setText((next['Fach']))
                    option2.setText((next['Uhrzeit']))
                except Exception as e:
                    log.warning("FAIL")
                    #print("fail")
                    pass
                print("nacheste stunde: " , next)
                log.info("nacheste stunde: " + str(next))
                return next



#--------------------
#     NOTIFICATION
#--------------------

# def notifcation(title,message):
#     notification = Notify()
#     notification.title = title
#     notification.message = message
#     notification.icon = "images/icon.png"
#
#     notification.send()

def random_sound():
    dir = os.listdir("sounds")
    random_sound = choice(dir)
    return random_sound


def notifcation(title = "test",message="test"):
    notification = Notify()
    notification.title = title
    notification.message = message
    sound = random_sound()
    setting = read_config()
    if setting[2] == "True": # True False - SOUND ON OFF

        if setting[3] == "default": # default random
            notification.audio = "sounds/" + "default.wav"

        if setting[3] == "random": # default random
            notification.audio = "sounds/" + sound

    if setting[4] == "True": # True False - Norifcarion ON OFF
        notification.icon = "images/icon.png"
        notification.send()

#notifcation("test","test")
#--------------------
# 5 SCHEDULES
#--------------------
# Datums Uhrzeit basierende Trigger

class Worker(QThread):

    def run(self):
        run_continuously()

def run_continuously(interval=5):
    """Continuously run, while executing pending jobs at each
    elapsed time interval.
    @return cease_continuous_run: threading. Event which can
    be set to cease continuous run. Please note that it is
    *intended behavior that run_continuously() does not run
    missed jobs*. For example, if you've registered a job that
    should run every minute and you set a continuous run
    interval of one hour then your job won't be run 60 times
    at each interval but only once.
    """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


# run ONCE at startuup
data_picker(data)


#schedule.every(5).seconds.do(naechste_stunde , data=data)
schedule.every().day.at("08:00").do(data_picker , data=data)
schedule.every().day.at("08:45").do(data_picker , data=data)
schedule.every().day.at("09:40").do(data_picker , data=data)
schedule.every().day.at("10:25").do(data_picker , data=data)
schedule.every().day.at("11:20").do(data_picker , data=data)

schedule.every().day.at("12:05").do(notifcation , title="bis 12:35" , message="Mittagspause") # mittagspause

schedule.every().day.at("12:35").do(data_picker , data=data) # mittagspause ende
schedule.every().day.at("13:30").do(data_picker , data=data)
schedule.every().day.at("14:15").do(data_picker , data=data)
schedule.every().day.at("15:00").do(data_picker , data=data) # FEIERABEND

#--------------------
# 6 SAVE JSON INFO in SQLITE
#--------------------
# Zwwischenspeicherung der Daten , unnötige requests vermeiden.

#----------------------------------------
#                  APP
#----------------------------------------

# Step 2: Create a QThread object
thread = QThread()
# Step 3: Create a worker object
worker = Worker()
# Step 4: Move worker to the thread
worker.moveToThread(thread)

# Step 5: Connect signals and slots
thread.started.connect(worker.run)
worker.finished.connect(thread.quit)
worker.finished.connect(worker.deleteLater)
thread.finished.connect(thread.deleteLater)

# Step 6: Start the thread
thread.start()




app = QtWidgets.QApplication([])

app.setQuitOnLastWindowClosed(False)

# Adding an icon
icon = QtGui.QIcon(':/images/icon.png')

# Adding item on the menu bar
tray = QtWidgets.QSystemTrayIcon()
tray.setIcon(icon)
tray.setVisible(True)

# https://gist.github.com/for-l00p/3e33305f948659313127632ad04b4311
class TrayIcon(QSystemTrayIcon):

    def __init__(self, parent=None):
        super(TrayIcon, self).__init__(parent)
        self.trayIcon = QSystemTrayIcon(QtGui.QIcon("images/icon.png"), self)
        self.trayIcon.activated.connect(self.onTrayIconActivated)
        self.trayIcon.show()


    def onTrayIconActivated(self, reason):
        print("onTrayIconActivated:", reason)
        if reason == QSystemTrayIcon.Trigger:
            print("JAWOLLO")
        elif reason == QSystemTrayIcon.DoubleClick:

            print("Tray icon double clicked")


# Creating the options
menu = QtWidgets.QMenu()

# FAlls es keine Daten gibt ... dann zeig nix an ;)
try:
    option1 = QtGui.QAction(QtGui.QIcon(':/images/icon.png'), naechste_stunde(data)['Fach'])
    option2 = QtGui.QAction(naechste_stunde(data)['Uhrzeit'],)
    #option2.triggered.connect(print("test"))

except:
    option1 = QtGui.QAction(QtGui.QIcon(':/images/icon.png'), "")
    option2 = QtGui.QAction("",)
    #option2.setText("JAWOLLO")


menu.addAction(option1)
menu.addAction(option2)
#menu.addAction("test", notifcation)

edit = menu.addMenu("Stundenplan")
tag_1 =edit.addMenu("Montag")
tag_2 =edit.addMenu("Dienstag")
tag_3 =edit.addMenu("Mittwoch")
tag_4 =edit.addMenu("Donnerstag")
tag_5 =edit.addMenu("Freitag")

# den menueeintraegen die jeweiligen unterrichteinheiten hinzufügen
for x in data:
    if x == "Montag":
        for y in data["Montag"].values():
            tag_1.addAction(y['Fach'] + " " + y['Uhrzeit'])

    if x == "Dienstag":
        for y in data["Dienstag"].values():
            tag_2.addAction(y['Fach'] + " " + y['Uhrzeit'])

    if x == "Mittwoch":
        for y in data["Mittwoch"].values():
            tag_3.addAction(y['Fach'] + " " + y['Uhrzeit'])

    if x == "Donnerstag":
        for y in data["Donnerstag"].values():
            tag_4.addAction(y['Fach'] + " " + y['Uhrzeit'])

    if x == "Freitag":
        for y in data["Freitag"].values():
            tag_5.addAction(y['Fach'] + " " + y['Uhrzeit'])

#tag_1.addAction("Stunde1")

# https://zetcode.com/gui/pyqt5/menustoolbars/

#optionen = menu.addMenu("Benachrichtigungen")
#setting_unterricht = optionen.addAction("Unterricht").setCheckable(True)
#setting_vertretung = optionen.addAction("Vertretung").setCheckable(True)
#setting_stundenplan = optionen.addAction("Stundenplan").setCheckable(True)


"""
Access functions:

bool	isChecked() const
void	setChecked(bool)

"""

# To quit the app
quit = QtGui.QAction("Exit")
quit.triggered.connect(app.quit)
menu.addAction(quit)

# Adding menu / options to the System Tray
tray.setContextMenu(menu)

app.exec_()

# TODO
# Wenn die anwendung startuet wäaerend mittagspause ist der text nicht gesetz - NON CRITICAL
# - CRITICAL- Erkennt leeren wochentag nicht wenn zb feiertag ist... freitag wird dann zu donnerstag zb weil tag fehlt
# wenn man anwendung startet waehrend stunde ... bekommt man keine nachricht... anwendung sollte im autostart sein  for that not to happen
# CRIRITCAL - external config
# CRIRITCAL-  naechste stunde waehrens pausenzeiten start nicht angeizeigt

"""
Feiertag	Datum
Neujahr	Fr, 01.01.2021
Karfreitag	Fr, 02.04.2021
Ostermontag	Mo, 05.04.2021
Tag der Arbeit	Sa, 01.05.2021
Christi Himmelfahrt	Do, 13.05.2021
Pfingstmontag	Mo, 24.05.2021
Tag der Deutschen Einheit	So, 03.10.2021
Reformationstag	So, 31.10.2021
Weihnachten	Sa, 25.12.2021
2. Weihnachtstag	So, 26.12.2021
"""
