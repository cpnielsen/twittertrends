from base import TwitterTrends
import operator
import smhasher
import math
import time

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
		for tag in tweet.topics:
			if tag in self.topics:
				self.topics[tag] += 1
				self.kmvadd(tag, tweet.message)
			else:
				if len(self.topics) <= self.buckets:
					self.topics[tag] = 1
					self.kmvadd(tag, tweet.message)
				else:
					# Decrement all values by 1
					# Delete those that would become 0
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
		self.kmvsets[tag].add(self.hashval(message.encode('utf-8')))

	def kmvdelete(self, tag):
		if tag in self.kmvsets:
			del self.kmvsets[tag]
			del self.totals[tag]

	def kmvdistinct(self, tag, k=[25, 50, 75, 100]):
		sorted_set = sorted(self.kmvsets[tag])
		result = []
		for no in k:
			if len(sorted_set) >= no:
				distinct = (no - 1) / sorted_set[(no - 1)]
				result.append(unicode(round(distinct)))

		return u"%s" % (u",".join(result))


	def writeresult(self, amount=10):
		print "Saving to file..."
		with open("trending" + str(self.minutes) + ".txt", 'w') as f:
			sorted_topics = sorted(self.topics.iteritems(), key=operator.itemgetter(1))
			sorted_topics.reverse()

			for x in xrange(amount):
				tag = sorted_topics[x][0]
				count = sorted_topics[x][1]
				distinct = self.kmvdistinct(tag)
				f.write(u'%d: %s (distinct: %s)\n' % (count, tag, distinct))

		# Wait <minutes> more until we output the next sample
		self.targettime = time.time() + (minutes * 60)

if __name__ == '__main__':
	trends = TwitterTrends()

	feedback_interval = 20
	# Find trending topics in the stream with distinct tweets per trending topic
	topicshour = TrendingTopics(trends, 165, feedback_interval)
	topicsday = TrendingTopics(trends, 155, feedback_interval)
	trends.add_subscriber(topicshour)
	trends.add_subscriber(topicsday)

	# Start the stream
	trends.start()