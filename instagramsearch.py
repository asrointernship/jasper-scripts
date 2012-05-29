#!/usr/bin/python

from instagram.client import InstagramAPI
from pymongo import Connection
from simplejson import JSONDecodeError
import datetime, math, sys
import time

date = datetime.datetime.now()
params = {
    'day':date.day,
    'month':date.month,
    'year':date.year,
    'hour':date.hour,
    'minute':date.minute,
    'second':date.second,
    'daysago':None
}

resolveParams = {
    'd':'day',
    'day':'day',
    'm':'month',
    'month':'month',
    'y':'year',
    'year':'year',
    'H':'hour',
    'hour':'hour',
    'M':'minute',
    'minute':'minute',
    'S':'second',
    'second':'second',
    'daysago':'daysago',
    'D':'daysago'
}
ok = True
continu = False
try:
    if len(sys.argv) == 2 and sys.argv[1] == '--continue':
        try:
            with open('.instagramsearch', 'r') as conf:
                lines = conf.readlines()
                savedMintime = int(lines[0])
                savedMaxtime = int(lines[1])
                savedNumber = int(lines[2])
                savedEnd = int(lines[3])
                continu = True
        except:
            ok = False
    else:
        for i in range(1,len(sys.argv)):
            if sys.argv[i].startswith('-'):
                name = sys.argv[i].lstrip('-')
                value = int(sys.argv[i + 1])
                params[resolveParams[name]] = value
        now = datetime.datetime(year=params['year'], month=params['month'], day=params['day'], hour=params['hour'], minute=params['minute'], second=params['second'])
except IndexError as ex:
    ok = False
except KeyError as ex:
    ok = False
except ValueError as ex:
    ok = False

if not params['daysago'] and not continu:
    ok = False

if ok:
    try:
        connection = Connection()
        db = connection.socialmap
        instagramDB = db.instagram
        
        api = InstagramAPI(client_id='fb2728054e0f462cb97e99eb056e4ddc')
        
        delta = 60*30
        if continu:
            end = savedEnd
            maxtime = savedMaxtime
            mintime = savedMintime
            number = savedNumber
        else:
            end = now - datetime.timedelta(days=params['daysago'])
            end = int(time.mktime(end.timetuple()))
            now = int(time.mktime(now.timetuple()))
            maxtime = now
            mintime = maxtime - delta
            number = 0
        
        #fullbbox = {'swLng':2.570801 , 'swLat':49.475263 , 'neLng':6.437988 , 'neLat':51.512161} # Belgium
        fullbbox = {'swLng':4.239349 , 'swLat':50.764259 , 'neLng':4.490662 , 'neLat':50.920351} # Brussels
        
        def getPoint(bbox, number):
            stepLng = 0.05
            stepLat = 0.03
            number = int(number)
            lineLength = bbox['neLng'] - bbox['swLng']
            stepsPerLine = int(math.ceil(lineLength/stepLng))
            line = number / stepsPerLine
            stepsThisLine = number % stepsPerLine
            lat = bbox['swLat'] + line * stepLat
            lng = bbox['swLng'] + stepsThisLine * stepLng
            if lat < bbox['neLat']:
                return {'lat':lat , 'lng':lng}
            else:
                return None
        
        
        while mintime>end:
            point = getPoint(fullbbox, number)
            print datetime.datetime.fromtimestamp(maxtime)
            while point:
                try:
                    media = api.media_search(min_timestamp=mintime, max_timestamp=maxtime, lat=point['lat'], lng=point['lng'], distance=5000)
                    for m in media:
                        latitude = None
                        longitude = None
                        locID = None
                        locName = None
                        instaFilter = None
                        userid = None
                        username = None
                        like_count = None
                        url = None
                        created_at = None
                        caption = None
                        _id = None
                        
                        try:
                            _id = m.id
                            if m.location and m.location.point:
                                if m.location.id:
                                    locID = m.location.id
                                if m.location.point.latitude and m.location.point.longitude:
                                    latitude = m.location.point.latitude
                                    longitude = m.location.point.longitude
                                if m.location.name:
                                    locName = m.location.name
                            if m.user:
                                if m.user.id:
                                    userid = m.user.id
                                if m.user.username:
                                    username = m.user.username
                            if m.filter:
                                instaFilter = m.filter
                            like_count = m.like_count
                            if m.get_standard_resolution_url():
                                url = m.get_standard_resolution_url()
                            if m.created_time:
                                created_at = m.created_time
                            if m.caption:
                                caption = m.caption.text
                            
                            if _id and latitude and longitude:
                                instagramDB.insert({'_id':_id, 'latitude':latitude, 'longitude':longitude, 'locationID':locID, 'locationName':locName, 'filter':instaFilter, 'userID':userid, 'username':username, 'like_count':like_count, 'url':url, 'created_at':created_at, 'caption':caption})
                            
                            #coords.write("{}\t{}\n".format(m.created_time, m.id))
                            #coords.write("{} {}\n".format(m.location.point.latitude, m.location.point.longitude))
                        except BaseException as ex:
                            print ex
                    number = number + 1
                    point = getPoint(fullbbox, number)
                except KeyboardInterrupt as ex:
                    coords.flush()
                    raise ex
                except JSONDecodeError as ex:
                    print ex
                except BaseException as ex:
                    print "Error:", ex
                    print "Going to sleep."
                    time.sleep(15*60)
                    print "Resuming."
            maxtime = mintime
            mintime = mintime - delta
            number = 0
        print "Search Finished."
    except BaseException as ex:
        print ex
    finally:
        connection.close()
        
        try:
            with open('.instagramsearch', 'w') as conf:
                conf.write(str(mintime) + "\n")
                conf.write(str(maxtime) + "\n")
                conf.write(str(number) + "\n")
                conf.write(str(end))
        except IOError as er:
            print "Error writing to '.instagramsearch':", er
else:
    print """This script searches for instagram pictures backwards in time since the start date (see below).

usage: {scriptName} -argName1 argValue1 -argName2 argValue2 ...
       {scriptName} --continue

Mandatory arguments:
    -D (or -daysago)    the amount of days in the past the script has to search since the start date
    
    OR
    
    --continue          continue the search where it stopped the previous time

Optional arguments:
    With these arguments you can define the start date.
    Every argument that is not defined by the user will be filled in with the values of the current date.
    So when no optional argument is given the script will use the current date as start date.
    Every argument value should be given in numbers.

    -d (or -day)        the day of the month of the start date
    -m (or -month)      the month of the start date
    -y (or -year)       the year of the start date
    -H (or -hour)       the hour of the start date
    -M (or -minute)     the minute of the start date
    -S (or -second)     the second of the start date
""".format(scriptName=sys.argv[0])