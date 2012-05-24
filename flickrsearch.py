from flickrapi import FlickrAPI
from flickrapi import FlickrError
import time
from datetime import datetime
import sys
from pymongo import Connection

print "Started"

#output = open("searchres.txt", "w")
connection = Connection()
db = connection.socialmap
flickrDB = db.flickr

flickr = FlickrAPI('ecbe2e529de5b65c68fb66470c587423')

n = 0
pagenr = 1
ids = []
maxDate = int(time.time())
tempMaxDate = maxDate

totalPics = 0
newestDate = datetime.fromtimestamp(0)

try:
    while True:
        while n < 4000:
            try:
                result = flickr.photos_search(bbox="2.570801,49.475263,6.437988,51.512161", max_upload_date=maxDate, per_page=250, extras="geo,date_upload", page=pagenr)
                pagenr = pagenr + 1
                photos = result.find('photos').findall('photo')
                
                if photos:
                    for photo in photos:
                        photoid = int(photo.attrib['id'])
                        if photoid not in ids:
                            ids.append(photoid)
                            #output.write("%s %s\n" %(photo.attrib['longitude'], photo.attrib['latitude']))
                            dateupload = int(photo.attrib['dateupload'])
                            if dateupload<tempMaxDate:
                                tempMaxDate = dateupload
                                
                            utcdate = datetime.utcfromtimestamp(dateupload)
                            if utcdate > newestDate:
                                newestDate = utcdate
                            doc = {'_id':photoid, 'longitude':float(photo.attrib['longitude']), 'latitude':float(photo.attrib['latitude']), 'dateupload':utcdate, 'title':photo.attrib['title'], 'owner':photo.attrib['owner'], 'secret':photo.attrib['secret'], 'farm':photo.attrib['farm'], 'server':photo.attrib['server']}
                            flickrDB.insert(doc)
                            totalPics = totalPics + 1
                    
                    tag = result.find('photos')
                    n = int(tag.attrib['perpage']) * int(tag.attrib['page'])
                    if n >= int(tag.attrib['total']):
                        n = 4001
                else:
                    sys.exit(0)
            except FlickrError as e:
                print "FlickrError:", e
                print "Going to sleep..."
                time.sleep(5*60)
                print "Resuming"
        #output.flush()
        pagenr = 1
        ids = ids[-1000:]
        maxDate = tempMaxDate
        n = 0
        print "Going to sleep..."
        time.sleep(10)
        print "Resuming"
except SystemExit:
    print "Search completed"
except KeyboardInterrupt:
    print "KeyboardInterrupt: search stopped"
except BaseException as e:
    print "Error:", e
finally:
    connection.close()
    
    try:
        with open('flickrLog.txt', 'a') as log:
            log.write("\"{fromDate}\"\t\"{untilDate}\"\t{total}\n".format(fromDate=datetime.utcfromtimestamp(tempMaxDate), untilDate=newestDate, total=totalPics))
    except IOError as er:
        print "Error writing to 'flickrLog.txt':", er
    
    #output.close()

print "Finished"
# print "http://farm%s.staticflickr.com/%s/%s_%s.jpg" %(photo.attrib['farm'], photo.attrib['server'], photo.attrib['id'], photo.attrib['secret'])
