import foursquare, math, time, sys
from pymongo import Connection

connection = Connection()
db = connection.socialmap
fsDB = db.foursquare

sleep = 15

try:
    with open('.fsSearch', 'r') as conf:
        lines = conf.readlines()
        number = int(lines[0])
except:
    number= 0

fullbbox = {'swLng':2.570801 , 'swLat':49.475263 , 'neLng':6.437988 , 'neLat':51.512161} # Belgium
#fullbbox = {'swLng':4.239349 , 'swLat':50.764259 , 'neLng':4.490662 , 'neLat':50.920351} # Brussels

client = foursquare.Foursquare(client_id='4DNLTACJRBS01OXLDUA12A3I5WY0LNOKXWVJD4OHLTBIIWWS', client_secret='UUMPY5DZCPVTHQZ1XY4G2QEX3TLLB4IQFO3JFFOFILMWQN01')


def getBbox(bbox, number):
    step = 0.0025
    number = int(number)
    lineLength = bbox['neLng'] - bbox['swLng']
    stepsPerLine = int(math.ceil(lineLength/step))
    line = number / stepsPerLine
    stepsThisLine = number % stepsPerLine
    swLat = bbox['swLat'] + line * step
    neLat = swLat + step
    swLng = bbox['swLng'] + stepsThisLine * step
    neLng = swLng + step
    if swLat < bbox['neLat']:
        return {'swLng':swLng , 'swLat':swLat , 'neLng':neLng , 'neLat':neLat}
    else:
        return None
    
#with open("fsCoords.txt", "w") as coords:
try:
    bbox = getBbox(fullbbox, number)
    while bbox:
        try:
            res = client.venues.search(params={'intent':'browse', 'sw':'{},{}'.format(bbox['swLat'], bbox['swLng']), 'ne' : '{},{}'.format(bbox['neLat'], bbox['neLng']), 'limit' : 50})
            sleep = 15
            venues = res['venues']
            #print len(venues)
            for venue in venues:
                try:
                    name = venue['name']
                    latitude = venue['location']['lat']
                    longitude = venue['location']['lng']
                    checkinsCount = venue['stats']['checkinsCount']
                    usersCount = venue['stats']['usersCount']
                    _id = venue['id']
                    categories = []
                    for category in venue['categories']:
                        categories.append(category['pluralName'])
                    #coords.write("{} {}\n".format(venue['location']['lat'], venue['location']['lng']))
                    if latitude<=fullbbox['neLat'] and latitude>=fullbbox['swLat'] and longitude>=fullbbox['swLng'] and longitude<=fullbbox['neLng']:
                        fsDB.insert({'name':name, '_id':_id, 'latitude':latitude, 'longitude':longitude, 'checkinsCount':checkinsCount, 'usersCount':usersCount, 'categories':categories})
                except:
                    pass
            number = number + 1
            bbox = getBbox(fullbbox, number)
        except foursquare.FoursquareException as ex:
            print >> sys.stderr, ex.__class__.__name__, ": ", ex
            print >> sys.stderr, "Going to sleep for", sleep, "minutes."
            time.sleep(60*sleep)
            sleep = 5
            print >> sys.stderr, "Resuming:", number
        except KeyboardInterrupt as interrupt:
            raise interrupt
        except BaseException as e:
            print >> sys.stderr, "Error:", e
            print >> sys.stderr, "Going to sleep for 30 minutes."
            time.sleep(60*30)
            print >> sys.stderr, "Resuming:", number
except KeyboardInterrupt:
    print >> sys.stderr, "KeyboardInterrupt"
finally:
    try:
        with open('.fsSearch', 'w') as conf:
            conf.write(str(number))
    except IOError as er:
        print "Error writing to '.fsSearch':", er

