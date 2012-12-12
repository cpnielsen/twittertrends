from tweepy import OAuthHandler, Stream
from tweepy.streaming import StreamListener
import json

CONSUMER_KEY="<key>"
CONSUMER_SECRET="<secret>"

ACCESS_TOKEN="<token>"
ACCESS_TOKEN_SECRET="<token secret>"

class Tweet:
	def __init__(self, message, topics, time, user):
		self.message = message
		self.topics = topics
		self.time = time
		self.user = user

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
					tags = [u"#" + t['text'].lower() for t in processed['entities']['hashtags']]
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

	def start(self):
		self.stream.sample()

	def stop(self):
		print 'Stopped'
		self.stream.disconnect()