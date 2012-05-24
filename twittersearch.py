import tweepy
from tweepy import Cursor
from tweepy import TweepError
import time
from datetime import datetime
from pymongo import Connection
import sys

print "Started"

connection = Connection()
db = connection.socialmap
twitterDB = db.twitter

#out = open("searchres.txt", "a")
totalTweets = 0
savedTweets = 0
newestDate = datetime.fromtimestamp(0)
oldestDate = datetime.utcnow()

try:
    with open('.twittersearch', 'r') as conf:
        lines = conf.readlines()
        maxid = int(lines[0])
except:
    maxid = float('inf')
loop = 0

try:
    while True:
        while loop<5000:
            try:
                if maxid != float('inf'):
                    result = tweepy.api.search(geocode='50.565794,4.438477,160km', rpp=100, result_type='recent', max_id=maxid)
                else:
                    result = tweepy.api.search(geocode='50.565794,4.438477,160km', rpp=100, result_type='recent')
                if len(result):
                    for status in result:
                        if status.id < maxid:
                            maxid = status.id
                        if status.created_at < oldestDate:
                            oldestDate = status.created_at
                        if status.created_at > newestDate:
                            newestDate = status.created_at
                        totalTweets = totalTweets + 1
                        loop = loop + 1
                        #text = status.text.encode('utf-8')
                        #text = re.sub(r'\n|\r', '', text)
                        #print text + " | " +str(status.created_at) + "\n"
                        if status.geo:
                            longitude = status.geo['coordinates'][1]
                            latitude = status.geo['coordinates'][0]
                            if latitude<=51.512161 and latitude>=49.475263 and longitude>=2.570801 and longitude<=6.437988:
                                twitterDB.insert({'_id':status.id, 'longitude':longitude, 'latitude':latitude, 'text':status.text, 'created_at': status.created_at, 'from_user_id':status.from_user_id, 'from_user':status.from_user, 'to_user_id':status.to_user_id, 'to_user':status.to_user})
                                savedTweets = savedTweets + 1
                                #out.write(str(longitude) + " " + str(latitude) + "\n")
                else:
                    sys.exit(0)
            except TweepError as t:
                print "TweepError:", t
                print "Going to sleep..."
                time.sleep(5*60)
                print "Resuming"
        #out.flush()
        print "Going to sleep..."
        time.sleep(15)
        print "Resuming"
        loop = 0
except SystemExit:
    print "Search completed"
except KeyboardInterrupt:
    print "KeyboardInterrupt"
except BaseException as e:
    print "Error:", e
finally:
    connection.close()
    try:
        with open('.twittersearch', 'w') as conf:
            conf.write(str(maxid))
    except IOError as er:
        print "Error writing to '.twittersearch':", er
    
    try:
        with open('twitterLog.txt', 'a') as log:
            log.write("\"{fromDate}\"\t\"{untilDate}\"\t{total}\t{saved}\n".format(fromDate=oldestDate, untilDate=newestDate, total=totalTweets, saved=savedTweets))
    except IOError as er:
        print "Error writing to 'twitterLog.txt':", er
    
    #out.close()
print "\nFINISHED with " + str(totalTweets) + " tweets\n"
