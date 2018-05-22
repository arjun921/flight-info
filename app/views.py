from flask import render_template
import os
from app import app
from selenium import webdriver
import datetime
from bs4 import BeautifulSoup
import urllib.request
import json


def getPage(flightID,):
    global browser
    date=datetime.datetime.now().date().strftime("%Y%m%d")
    link = 'https://uk.flightaware.com/live/flight/{}/history/{}/'.format(flightID,date)
    print(link)
    browser.get(link)

@app.before_first_request
def initialize():
    global browser
    browser = webdriver.PhantomJS()


# Webservices
@app.route('/flightdata/<flightID>')
def webhook(flightID):
    global browser
    getPage(flightID)
    flightSummary = browser.find_element_by_id('flightPageTourStep1')
    flightSummarySoup = BeautifulSoup(flightSummary.get_attribute('innerHTML'), 'html.parser')
    sourceDest = flightSummarySoup.find('div',{"class": "flightPageSummaryAirports"})
    sourceIATA = sourceDest.find('div',{'class':'flightPageSummaryOrigin'}).find('span',{'class':'displayFlexElementContainer'}).text
    sourceFName = sourceDest.find('div',{'class':'flightPageSummaryOrigin'}).find('span',{'class':'flightPageSummaryCity'}).text
    destIATA = sourceDest.find('div',{'class':'flightPageSummaryDestination'}).find('span',{'class':'displayFlexElementContainer'}).text
    destFName = sourceDest.find('div',{'class':'flightPageSummaryDestination'}).find('span',{'class':'flightPageSummaryCity'}).text
    dateOfDeparture = flightSummarySoup.find('span',{'class':'flightPageSummaryDepartureDay'}).text.split(' ')[-1]
    dayOfDeparture =  flightSummarySoup.find('span',{'class':'flightPageSummaryDepartureDay'}).text.split(' ')[0]
    timeOfDeparture =  flightSummarySoup.find('span',{'class':'flightPageSummaryDeparture'}).text.split('\n\n\n')[0]
    dateOfArrival = flightSummarySoup.find('span',{'class':'flightPageSummaryArrivalDay'}).text.split(' ')[-1]
    dayOfArrival =  flightSummarySoup.find('span',{'class':'flightPageSummaryArrivalDay'}).text.split(' ')[0]
    timeOfArrival =  flightSummarySoup.find('span',{'class':'flightPageSummaryArrival'}).text.split('\n\n\n')[0]
    departureDelay = flightSummarySoup.find('span',{'class':'flightPageDepartureDelayStatus'}).text.strip("()")
    arrivalDelay = flightSummarySoup.find('span',{'class':'flightPageArrivalDelayStatus'}).text.strip("()")
    totalFlightTime = flightSummarySoup.find('span',{'class':'flightPageProgressTotal'}).text.strip().replace('\n total flight time','')
    AboutFlight  = browser.find_element_by_class_name('flightPageSummaryContainer')
    AboutFlightSoup = BeautifulSoup(AboutFlight.get_attribute('innerHTML'), 'html.parser')
    currentStatus = AboutFlightSoup.find('div',{'class':'flightPageSummaryStatus'})
    summary = {}
    summary['totalTime'] = totalFlightTime
    summary['status'] = currentStatus.contents[0]
    if len(currentStatus.contents)>1:
        summary['sub-status'] = currentStatus.contents[1].text
    source = {}
    source['name'] = sourceFName.strip()
    source['airportCode'] = sourceIATA.strip()
    summary['source'] = source
    destination = {}
    destination['name'] = destFName.strip()
    destination['airportCode'] = destIATA.strip()
    summary['destination'] = destination
    departure = {}
    departure['day'] = dayOfDeparture.strip()
    departure['date'] = dateOfDeparture.strip()
    departure['time'] = timeOfDeparture.strip()
    departure['status'] = departureDelay.title()
    summary['departure'] = departure
    arrival = {}
    arrival['day'] = dayOfArrival.strip()
    arrival['date'] = dateOfArrival.strip()
    arrival['time'] = timeOfArrival.strip()
    arrival['status'] = arrivalDelay.title()
    summary['arrival'] = arrival
    return json.dumps(summary)
