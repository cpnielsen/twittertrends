from base import TwitterTrends
import time

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
		self.f.write('Total number of tweets in %d minutes: %d\n'
					  % (self.runningtime, self.counter))
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

if __name__ == '__main__':
	trends = TwitterTrends()

	# Sample complete data for topics for X minutes
	topicshour = SimpleTopicCounter(60, trends)
	topicsday = SimpleTopicCounter(1440, trends)
	trends.add_subscriber(topicshour)
	trends.add_subscriber(topicsday)

	# Start the stream
	trends.start()