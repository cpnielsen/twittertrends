from tweepy import OAuthHandler, Stream
from tweepy.streaming import StreamListener
import json
from streamlistener import StdOutListener

class TwitterTrends:

	def __init__(self, streamListener):
		self.streamListener = streamListener
		self.trendingtopics = []

	def trendingtopics(self):
		# Read data stream from streamListener and find trending topics
		return "#itu, #sad2, #obama"

	def misragries(self):
		#Perform misra-gries algorithm
		return self.trendingtopics

	def distincttopics(self):
		#use an algorithm to find distinct/rising topics
		return "#itu, #obama, #sad2"

	def newtweet(self):
		#callback from listener, create new tweet
		return ""

class Tweet:
	def __init__(self, message, topic, time, user):
		self.message = message
		self.topic = topic
		self.time = time
		self.user = user

# Go to http://dev.twitter.com and create an app. 
# The consumer key and secret will be generated for you after
consumer_key="2XhwGwTJefx4aD2xdo4UoQ"
consumer_secret="yX5WYFz9LugOWyMgtkv4iWOvhBjGGZStmA61icFyi4"

# After the step above, you will be redirected to your app's page.
# Create an access token under the the "Your access token" section
access_token="21019503-cKlNTqPehUAlyFR1FqcqjXPVK57xf3Jz4uEEk7pUz"
access_token_secret="9gmuOaf9pf1nUV3Z87XDLL9Fwh47JTQonlinGinPRE"

if __name__ == '__main__':
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    stream = Stream(auth, l)
    stream.filter(track=['*'])

    trends = TwitterTrends(stream)
