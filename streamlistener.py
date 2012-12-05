# -*- coding: utf-8 -*-
from tweepy import OAuthHandler, Stream
from tweepy.streaming import StreamListener
import json

class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream. 
    This is a basic listener that just prints received tweets to stdout.

    """

    def __init__(self, repository):
        self.i = 0
        self.repository = repository

    def on_data(self, data):
        processed = json.loads(data)
        #if self.i == 0:
        #    print "----"
        #    print json.dumps(processed)
        #    print "----"
        #    self.i = 1
        user = processed['user']['screen_name']
        tweet = processed['text']
        time = processed['created_at']
        if len(processed['entities']['hashtags']) > 1:
            tags = ["#" + t['text'] for t in processed['entities']['hashtags']]
            print u"%s: %s - tags: %s" % (user, tweet, ','.join(tags))
            self.repository.newtweet(tweet, ','.join(tags), time, user)

        return True

    def on_error(self, status):
        print status