#!/usr/bin/env python
# -*- coding: utf-8 -*-
# > - > - > - >  > - > - > - > <
#    IBB TRAY - by steffenu    ^
# > - > - > - >  > - > - > - > ^

import calendar
import datetime

import requests
import json

import locale # Let's set a non-US locale

locale.setlocale(locale.LC_ALL, '')


def weeknr_of_date(date):
    feiertag = datetime.datetime.strptime(date,"%Y-%m-%d")
    feiertag_weeknr = feiertag.isocalendar()[1]
    feiertag_wochentag = feiertag.date().weekday()
    feiertag_wochentag= calendar.day_name[feiertag_wochentag]  #'Wednesday'

    #print(feiertag_weeknr , feiertag_wochentag)

    return(feiertag_weeknr , feiertag_wochentag)




# 1. make api request
# 2.
def feiertag_diese_woche():

    weeknr= datetime.datetime.now().isocalendar()[1] # diese woche
    print("Aktuelle Woche feiertag_diese_woche())",weeknr)

        # Making the post request and parse json
    headers = {'X-DFA-Token': 'dfa'}
    r = requests.post("https://deutsche-feiertage-api.de/api/v1/2021?bundeslaender=mv", headers=headers)
    #print(r.encoding)
    response = r.text
    json_data = json.loads(response)
    json_data = json_data['holidays']

    print(json_data)

    for x in json_data:
        if x['holiday']['regions']['mv'] == True:
            name , date = x['holiday']['name'] , x['holiday']['date']
            #print(name,date)
            w1,w2 = weeknr_of_date(date) # wochenummer des feiertagsdatums
            if w1 == weeknr: # wenn feiertag diese woche
                print(w2, name)
                return (w2, name)




feiertag_diese_woche()





"""
%a	Weekday, short version	Wed	
%A	Weekday, full version	Wednesday	
%w	Weekday as a number 0-6, 0 is Sunday	3	
%d	Day of month 01-31	31	
%b	Month name, short version	Dec	
%B	Month name, full version	December	
%m	Month as a number 01-12	12	
%y	Year, short version, without century	18	
%Y	Year, full version	2018	
%H	Hour 00-23	17	
%I	Hour 00-12	05	
%p	AM/PM	PM	
%M	Minute 00-59	41	
%S	Second 00-59	08	
%f	Microsecond 000000-999999	548513	
%z	UTC offset	+0100	
%Z	Timezone	CST	
%j	Day number of year 001-366	365	
%U	Week number of year, Sunday as the first day of week, 00-53	52	
%W	Week number of year, Monday as the first day of week, 00-53	52	
%c	Local version of date and time	Mon Dec 31 17:41:00 2018	
%x	Local version of date	12/31/18	
%X	Local version of time	17:41:00	
%%	A % character	%	
%G	ISO 8601 year	2018	
%u	ISO 8601 weekday (1-7)	1	
%V	ISO 8601 weeknumber (01-53)	01
"""