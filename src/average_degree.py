import json
import sys
import itertools
from datetime import datetime, timedelta
import heapq
import math

months = {
  'Jan': 1,
  'Feb': 2,
  'Mar': 3,
  'Apr': 4,
  'May': 5,
  'Jun': 6,
  'Jul': 7,
  'Aug': 8,
  'Sep': 9,
  'Oct': 10,
  'Nov': 11,
  'Dec': 12
}

class Tweet:
  def __init__(self, text):
    tweet_dict = json.loads(text)

    date = str(tweet_dict['created_at']).split(' ')
    # eg. Tue Mar 29 06:04:50 +0000 2016
    # *** Important: Under assumption that it is always +0000 timezone ***
    time = date[3].split(':')
    self.timestamp = datetime(int(date[5]), months[date[1]], int(date[2]), int(time[0]), int(time[1]), int(time[2]))
    self.hashtags = []
    for data in tweet_dict['entities']['hashtags']:
      self.hashtags.append(data['text'].lstrip('#'))

  def get_timestamp(self):
    return self.timestamp

  def get_hashtags(self):
    return self.hashtags

  def get_hashtag_combinations(self):
    return itertools.combinations(self.hashtags, 2)

class Graph:
  def __init__(self):
    self.graph = {}

  def add_double_edge(self, edge):
    self.graph.setdefault(edge[0], set())
    self.graph[edge[0]].add(edge[1])

    self.graph.setdefault(edge[1], set())
    self.graph[edge[1]].add(edge[0])

  def link_hashtags(self, tweet):
    for edge in tweet.get_hashtag_combinations():
      self.add_double_edge(edge)

  def remove_edge(self, edge):
    if edge[0] in self.graph[edge[1]]:
      self.graph[edge[1]].remove(edge[0])
    if edge[1] in self.graph[edge[0]]:
      self.graph[edge[0]].remove(edge[1])

  def unlink_hashtags(self, tweet):
    for edge in tweet.get_hashtag_combinations():
      self.remove_edge(edge)

  def average_degree(self):
    degree_sum = 0
    number_of_nodes = 0
    for node, edge_set in self.graph.iteritems():
      degree_sum += len(edge_set)
      if len(edge_set) > 0:
        number_of_nodes += 1
    if number_of_nodes == 0:
      return '%.2f' % 0.0
    else:
      # return float(degree_sum) / number_of_nodes # ok this doesn't work because of rounding issues
      # format into 3 places, then chop off that extra digit
      values = str('%.3f' % (float(degree_sum) / number_of_nodes)).split('.')
      return values[0] + '.' + values[1][:2]

    
if __name__ == "__main__":
  with open(sys.argv[1]) as input_file, open(sys.argv[2], 'w') as output_file:
    window = []
    graph = Graph()
    tweet = Tweet(input_file.readline().strip())
    latest_time = tweet.get_timestamp()
    earliest_time = latest_time - timedelta(0, 60)
    graph.link_hashtags(tweet)
    output_file.write('{}\n'.format(graph.average_degree()))

    for line_number, content in enumerate(input_file):
      try:
        tweet = Tweet(content)
      except Exception as e:
        # print e # throw out all 'limit' json objects (not tweets)
        continue

      if tweet.get_timestamp() > latest_time:
        latest_time = tweet.get_timestamp()
        earliest_time = latest_time - timedelta(0, 60)
      
      if tweet.get_timestamp() <= earliest_time:
        output_file.write('{}\n'.format(graph.average_degree()))
        continue

      heapq.heappush(window, (tweet.get_timestamp(), tweet))

      graph.link_hashtags(tweet)
      while len(window) > 0 and window[0][0] < earliest_time:
        (time, old_tweet) = heapq.heappop(window)
        graph.unlink_hashtags(old_tweet)
      output_file.write('{}\n'.format(graph.average_degree()))


