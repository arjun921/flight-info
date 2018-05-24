from flask import *
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


@app.route('/enroute')
def findEnrouteFlights():
    global browser
    enrouteflights = []
    origin= request.args.get('origin')
    destination= request.args.get('destination')
    link = 'https://uk.flightaware.com/live/findflight?origin={}&destination={}'.format(origin,destination)
    print(link)
    browser.get(link)
    browser.set_window_size(height=1009,width=1617)
    try:
        browser.find_element_by_id('r_En_Route')
        browser.execute_script("document.getElementById('r_En_Route').parentNode.parentNode.children[1].children[0].click()")
    except Exception as e:
        data = {"enroute":["No Enroute Flights"]}
        print(data)
        return json.dumps(data)

    resultsSoup = BeautifulSoup(browser.find_element_by_id('Results').get_attribute('innerHTML'), 'html.parser')
    for x in resultsSoup.findAll('tr',{'style':''})[1:]:
        if str(x) not in ['<tr class=""></tr>','<tr class="alternateRow"></tr>']:
            flight = {
                "flightName" : x.findAll('td')[0].findAll('span')[0].text,
                "flightID" : x.findAll('td')[1].findAll('a')[0].text,
                "aircraft" : x.findAll('td')[2].text.strip(),
                "status" : x.findAll('td')[3].text.strip(),
                "departs" : (x.findAll('td')[4].text.strip().encode('ascii', 'ignore')).decode("utf-8"),
                "arrives" : (x.findAll('td')[6].text.strip().encode('ascii', 'ignore')).decode("utf-8"),
            }
            enrouteflights.append(flight)
    data = {
        "enroute" : enrouteflights
    }
    print(data)
    return json.dumps(data)
