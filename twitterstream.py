import tweepy
from textwrap import TextWrapper
import json, time
from datetime import datetime
from datetime import timedelta
from pymongo import Connection

connection = Connection()
db = connection.socialmap
twitterDB = db.twitter

count = 0

class StreamWatcherListener(tweepy.StreamListener):
    
    status_wrapper = TextWrapper(width=60, initial_indent='    ', subsequent_indent='    ')

    def on_status(self, status):
        try:
            if hasattr(status, 'coordinates') and status.coordinates:
                coo = status.coordinates
                longitude = coo['coordinates'][0]
                latitude = coo['coordinates'][1]
                if latitude<=51.512161 and latitude>=49.475263 and longitude>=2.570801 and longitude<=6.437988:
                    #out.write("%s %s\n" %(longitude, latitude))
                    global count
                    count = count + 1
                    twitterDB.insert({'_id':status.id, 'longitude':longitude, 'latitude':latitude, 'text':status.text, 'created_at': status.created_at, 'from_user_id':status.author.id, 'from_user':status.author.screen_name, 'to_user_id':status.in_reply_to_user_id, 'to_user':status.in_reply_to_screen_name})
                    #print self.status_wrapper.fill(status.text.encode('utf-8'))
                    #print '\n %s  %s  via %s\n' % (status.author.screen_name.encode('utf-8'), status.created_at, status.source)
        except Exception as e:
            print "Error: ", e

    def on_error(self, status_code):
        print 'An error has occurred! Status code = %s' % status_code
        
        return True # keep stream alive

    def on_timeout(self):
        print 'Snoozing Zzzzzz'


auth = tweepy.OAuthHandler('BaOAJk7Y6ycqEUlXSG12fw', 'As0SiyPu6YnUkCaEQTRBuWmuYsO0UIgYst3AugNTc')


key = "522278301-IoXpvLrFrxXatnTWMwEu3axbJXwhEokqtDKiy0ew"
secret = "G167dsXgtgd4WEL2I0DVHeNPhyd56S1ivwKQAvWTyqc"
auth.set_access_token(key, secret)


stream = tweepy.Stream(auth, StreamWatcherListener(), timeout=None)

start = datetime.utcnow()
delta = timedelta(microseconds=start.microsecond)
start = start - delta
loop = True

while loop:
    try:
        stream.filter(locations=[2.570801,49.475263, 6.437988, 51.512161])
    except KeyboardInterrupt:
        print "KeyboardInterrupt"
        loop = False
    except BaseException as e:
        print "Error",e
        print "Going to sleep."
        time.sleep(60*5)
        print "Resuming.\n"

#out.close()
end = datetime.utcnow()
delta = timedelta(microseconds=end.microsecond)
end = end - delta

try:
    with open('twitterLog.txt', 'a') as log:
        log.write("\"{fromDate}\"\t\"{untilDate}\"\t{total}\t{saved}\n".format(fromDate=start, untilDate=end, total="N/A", saved=count))
except IOError as er:
    print "Error writing to 'twitterLog.txt':", er

print "\nGoodbye\n%s tweets\n" %(count)
