from tweepy import OAuthHandler, Stream
from tweepy.streaming import StreamListener
import json
import time
import operator
from random import random

CONSUMER_KEY="2XhwGwTJefx4aD2xdo4UoQ"
CONSUMER_SECRET="yX5WYFz9LugOWyMgtkv4iWOvhBjGGZStmA61icFyi4"

ACCESS_TOKEN="21019503-cKlNTqPehUAlyFR1FqcqjXPVK57xf3Jz4uEEk7pUz"
ACCESS_TOKEN_SECRET="9gmuOaf9pf1nUV3Z87XDLL9Fwh47JTQonlinGinPRE"

FILENAME_COUNT = "simplecount"

class Tweet:
    def __init__(self, message, topics, time, user):
        self.message = message
        self.topics = topics
        self.time = time
        self.user = user

class SimpleTweetWriter:
    def on_tweet(self, tweet):
        print u'%s: %s - %s' % (tweet.user, tweet.message, ', '.join(tweet.topics))

class SimpleTopicCounter:
    def __init__(self, minutes, twittertrends):
        self.client = twittertrends
        self.runningtime = minutes
        self.topics = {}
        self.targettime = time.time() + (minutes * 60)

    def on_tweet(self, tweet):
        if time.time() > self.targettime:
            self.writefile()
        for tag in tweet.topics:
            if tag in self.topics:
                self.topics[tag] = self.topics[tag] + 1
            else:
                self.topics[tag] = 1
        #print u'%s: %s - %s' % (tweet.user, tweet.message, ', '.join(tweet.topics))

    def writefile(self):
        self.f = open(FILENAME_COUNT + str(self.runningtime) + ".txt", 'w')
        sorted_topics = sorted(self.topics.iteritems(), key=operator.itemgetter(1))
        sorted_topics.reverse()

        for x in xrange(len(self.topics)):
            try:
                self.f.write(u'%d: %s' % (sorted_topics[x][1], sorted_topics[x][0]) + '\n')
            except UnicodeEncodeError:
                pass

        self.f.close()
        self.client.remove_subscriber(self)
        print 'Topic counter: %d minutes collected' % self.runningtime

class TrendingTopics:
    def __init__(self, buckets):
        self.topics = {}
        self.buckets = buckets
        self.count = 0

    def on_tweet(self, tweet):
        for tag in tweet.topics:
            if tag in self.topics:
                self.topics[tag] = self.topics[tag] + 1
            else:
                if len(self.topics) <= self.buckets:
                    self.topics[tag] = 1
                else:
                    found = None
                    for topic, value in self.topics.iteritems():
                        if value == 0:
                            found = topic
                            break
                    if found != None:
                        del self.topics[found]
                        self.topics[tag] = 1
                    else:
                        for topic, value in self.topics.iteritems():
                            self.topics[topic] = value - 1

            self.count = self.count + 1
            #if tag in self.topics:
            #    print u"Tag '%s' has %d value" % (tag, self.topics[tag])
        
        if self.count > 1000:
            self.count = 0
            self.gettopics()

    def gettopics(self, amount=10):
        sorted_topics = sorted(self.topics.iteritems(), key=operator.itemgetter(1))
        sorted_topics.reverse()

        for x in xrange(amount):
            print u'%d: %s' % (sorted_topics[x][1], sorted_topics[x][0])


class TwitterTrends(StreamListener):
    def __init__(self):
        #initiate the reuqired authentication
        auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

        self.stream = Stream(auth, self)

        self.subscribers = []

    def on_data(self, data):
        for entry in data.split("\r\n"):
            processed = json.loads(entry)

            # Only include tweets that has a "topic", in this case one or more hashtags
            if "entities" in processed:
                if len(processed['entities']['hashtags']) > 0:
                    tags = ["#" + t['text'] for t in processed['entities']['hashtags']]
                    user = processed['user']['screen_name']
                    text = processed['text']
                    time = processed['created_at']

                    tweet = Tweet(text, tags, time, user)

                    for subscriber in self.subscribers:
                        subscriber.on_tweet(tweet)


    def on_error(self, error):
        print u"Error occurred: %s" % error

    def add_subscriber(self, subscriber):
        self.subscribers.append(subscriber)

    def remove_subscriber(self, subscriber):
        self.subscribers.remove(subscriber)

    def start(self, topics=['*']):
        self.stream.sample(async=True)

    def stop(self):
        self.stream.disconnect()



if __name__ == '__main__':
    # l = StdOutListener()
    # auth = OAuthHandler(consumer_key, consumer_secret)
    # auth.set_access_token(access_token, access_token_secret)
    # stream = Stream(auth, l)
    # stream.filter(track=['*'])
    trends = TwitterTrends()
    trendtopics = TrendingTopics(250)
    topiccounter = SimpleTopicCounter(120, trends)
    trends.add_subscriber(trendtopics)
    trends.add_subscriber(topiccounter)
    #trends.add_subscriber(SimpleTweetWriter())
    trends.start()

    while True:
        try:
            time.sleep(10)
        except (KeyboardInterrupt, SystemExit):
            trends.stop()
            print "Done"
