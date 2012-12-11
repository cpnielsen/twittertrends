from tweepy import OAuthHandler, Stream
from tweepy.streaming import StreamListener
from random import random
from sets import Set
import json
import time
import operator
import smhasher 

CONSUMER_KEY="2XhwGwTJefx4aD2xdo4UoQ"
CONSUMER_SECRET="yX5WYFz9LugOWyMgtkv4iWOvhBjGGZStmA61icFyi4"

ACCESS_TOKEN="21019503-cKlNTqPehUAlyFR1FqcqjXPVK57xf3Jz4uEEk7pUz"
ACCESS_TOKEN_SECRET="9gmuOaf9pf1nUV3Z87XDLL9Fwh47JTQonlinGinPRE"

FILENAME_COUNT = "simplecount"
LENGTH_COUNT = "tweetlength"

INT_64_MAX = 2^64 - 1

class Tweet:
    def __init__(self, message, topics, time, user):
        self.message = message
        self.topics = topics
        self.time = time
        self.user = user

class SimpleTweetWriter:
    def on_tweet(self, tweet):
        print u'%s: %s - %s' % (tweet.user, tweet.message, ', '.join(tweet.topics))

class TweetLengthCounter:
    def __init__(self, minutes, twittertrends):
        self.client = twittertrends
        self.runningtime = minutes
        self.targettime = time.time() + (minutes * 60)
        self.buckets = { k: 0 for k in xrange(500) }
        self.counter = 0

    def on_tweet(self, tweet):
        if time.time() > self.targettime:
            self.writefile()
        bucket = len(tweet.message)
        self.buckets[bucket] += 1
        self.counter += 1

    def writefile(self):
        self.f = open(LENGTH_COUNT + str(self.runningtime) + ".txt", 'w')
        self.f.write('--- Total number of tweets in %d minutes: %d --- \n' % (self.runningtime, self.counter))
        for k, v in self.buckets.iteritems():
            self.f.write('%d: %d times' % (k, v))
        self.f.close()
        self.client.remove_subscriber(self)
        print 'Length counter: %d minutes collected' % self.runningtime

class SimpleTopicCounter:
    def __init__(self, minutes, twittertrends):
        self.client = twittertrends
        self.runningtime = minutes
        self.topics = {}
        self.targettime = time.time() + (minutes * 60)
        #self.targettime = time.time() + 10
        self.counter = 0

    def on_tweet(self, tweet):
        if time.time() > self.targettime:
            self.writefile()
        for tag in tweet.topics:
            if tag in self.topics:
                self.topics[tag] = self.topics[tag] + 1
            else:
                self.topics[tag] = 1

        self.counter = self.counter + 1
        #print u'%s: %s - %s' % (tweet.user, tweet.message, ', '.join(tweet.topics))

    def writefile(self):
        self.f = open(FILENAME_COUNT + str(self.runningtime) + ".txt", 'w')
        self.f.write('--- Total number of tweets in %d minutes: %d --- \n' % (self.runningtime, self.counter))
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
    def __init__(self, client, buckets, minutes):
        self.topics = {}
        self.kmvsets = {}
        self.totals = {}
        self.client = client
        self.buckets = buckets
        self.minutes = minutes
        self.targettime = time.time() + (minutes * 60)

    def on_tweet(self, tweet):
        if time.time() > self.targettime:
            self.writeresult()
            self.client.stop()
        for tag in tweet.topics:
            if tag in self.topics:
                self.topics[tag] += 1
                self.kmvadd(tag, tweet.message)
            else:
                if len(self.topics) <= self.buckets:
                    self.topics[tag] = 1
                    self.kmvadd(tag, tweet.message)
                else:
                    # Decrement all values by 1 and delete (ignore) those that would drop to 0
                    #self.topics = { k: (v-1) for k, v in self.topics.iteritems() if v >= 1 }
                    newtopics = {}
                    for k, v in self.topics.iteritems():
                        if v <= 1:
                            self.kmvdelete(k)
                        else:
                            newtopics[k] = v - 1
                    self.topics = newtopics

    def hashval(self, message):
        h = smhasher.murmur3_x64_64(message)
        final = h / INT_64_MAX
        return final

    def kmvadd(self, tag, message):
        if tag not in self.kmvsets:
            self.kmvsets[tag] = Set()
            self.totals[tag] = 0
        self.kmvsets[tag].add(self.hashval(message.encode('utf-8')))
        self.totals[tag] += 1

    def kmvdelete(self, tag):
        if tag in self.kmvsets:
            del self.kmvsets[tag]
            del self.totals[tag]

    def kmvdistinct(self, tag, k=[10, 20, 30, 40, 50]):
        sorted_set = sorted(self.kmvsets[tag])
        result = []
        for no in k:
            if len(sorted_set) >= no:
                distinct = 1 / (sum(sorted_set[:no]) / k)
                result.append(distinct)

        print "%s (%d)" % (','.join(result), len(sorted_set))


    def writeresult(self, amount=10):
        with open("trending" + str(self.runningtime) + ".txt", 'w') as f:
            sorted_topics = sorted(self.topics.iteritems(), key=operator.itemgetter(1))
            sorted_topics.reverse()

            for x in xrange(amount):
                tag = sorted_topics[x][0]
                f.write(u'%d: %s (distinct: %s, total: %d)' % (sorted_topics[x][1], tag, self.kmvdistinct(tag), self.totals[tag]))


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
                    tags = ["#" + t['text'].lower() for t in processed['entities']['hashtags']]
                    user = processed['user']['screen_name']
                    text = processed['text']
                    time = processed['created_at']

                    tweet = Tweet(text, tags, time, user)

                    for subscriber in self.subscribers:
                        subscriber.on_tweet(tweet)

        if len(self.subscribers) == 0:
            self.stop()

    def on_error(self, error):
        print u"Error occurred: %s" % error

    def add_subscriber(self, subscriber):
        self.subscribers.append(subscriber)

    def remove_subscriber(self, subscriber):
        self.subscribers.remove(subscriber)

    def start(self, topics=['*']):
        self.stream.sample()

    def stop(self):
        self.stream.disconnect()



if __name__ == '__main__':
    trends = TwitterTrends()
    trendtopics = TrendingTopics(trends, 150, 5)
    trends.add_subscriber(trendtopics)
    #counter = TweetLengthCounter(60, trends)
    #trends.add_subscriber(counter)
    #hashf = smhasher.murmur3_x64_64
    trends.start()

    while True:
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            trends.stop()
