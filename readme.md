# Flight Information API

This simple app gives flight related information for future, in-progress and past flights.

Add PhantomJS Buildpack to heroku from here:

`https://github.com/stomita/heroku-buildpack-phantomjs.git`

### Endpoint

`localhost:5000/flightdata/VTI885`  or `https://flightaware.herokuapp.com/flightdata/VTI885`

Send `GET` requests to the above URL withyour flight tracking ID get a json response as shown below:

```json
{
  "totalTime": "3h 11m",
  "status": "En route",
  "sub-status": "Landing in 2 hours 9 minutes",
  "source": {
    "name": "New Delhi, India",
    "airportCode": "DEL"
  },
  "destination": {
    "name": "Kochi / Nedumbassery, India",
    "airportCode": "COK"
  },
  "departure": {
    "day": "Tuesday",
    "date": "22-May-2018",
    "time": "14:40 IST",
    "status": "On Time"
  },
  "arrival": {
    "day": "Tuesday",
    "date": "22-May-2018",
    "time": "17:51 IST",
    "status": "21 Minutes Late"
  }
}
```