from tweepy import OAuthHandler, Stream
from tweepy.streaming import StreamListener
import json

# Go to http://dev.twitter.com and create an app. 
# The consumer key and secret will be generated for you after
consumer_key="2XhwGwTJefx4aD2xdo4UoQ"
consumer_secret="yX5WYFz9LugOWyMgtkv4iWOvhBjGGZStmA61icFyi4"

# After the step above, you will be redirected to your app's page.
# Create an access token under the the "Your access token" section
access_token="21019503-cKlNTqPehUAlyFR1FqcqjXPVK57xf3Jz4uEEk7pUz"
access_token_secret="9gmuOaf9pf1nUV3Z87XDLL9Fwh47JTQonlinGinPRE"

class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream. 
    This is a basic listener that just prints received tweets to stdout.

    """

    def __init__(self):
        self.i = 0

    def on_data(self, data):
        processed = json.loads(data)
        #if self.i == 0:
        #    print "----"
        #    print json.dumps(processed)
        #    print "----"
        #    self.i = 1
        user = processed['user']['screen_name']
        tweet = processed['text']

        if len(processed['entities']['hashtags']) > 1:
            tags = ["#" + t['text'] for t in processed['entities']['hashtags']]
            print u"%s: %s - tags: %s" % (user, tweet, ','.join(tags))

        return True

    def on_error(self, status):
        print status

if __name__ == '__main__':
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    stream = Stream(auth, l)
    stream.filter(track=['*'])