#! /usr/bin/env python
#
# Ben Osment
# Sat Apr 28 11:41:18 2012

import oauth
import time
import unicodedata
import re

# create a new authenticated instance of the API
api = oauth.oauth_login()

def download_tweets(corpus_name, query, threshold):
    max_tweets_per_hr  = 325
    download_pause_sec = 3600 / max_tweets_per_hr

    # open corpus file, append new entries
    # try:
    #     # if the file exists, read number of exisiting entries
    #     # and append new entries to the end
    #     corpus = open(corpus_name, 'r+')
    #     num_entries = 0
    #     for line in corpus:
    #         num_entries += 1
    #     print "found exisiting file with", num_entries, "tweets"
    # except IOError:
    #     # otherwise, create a new file for writing the tweets
    #     print "creating new file", corpus name

    num_pos_entries = 0
    num_neg_entries = 0
    pos_corpus = open('pos_corpus', 'r+')
    for line in pos_corpus:
        num_pos_entries += 1
    neg_corpus = open('neg_corpus', 'r+')
    for line in neg_corpus:
        num_neg_entries += 1

    # if num entries > threshold,  stop
    while num_pos_entries < threshold:
        # wait between queries to stay under the threshold
        time.sleep(download_pause_sec)
        num_pos_entries += add_tweets(pos_corpus, ':)')
        time.sleep(download_pause_sec)
        num_neg_entries += add_tweets(neg_corpus, ':(')
        print "###", num_pos_entries, "###"
        print "###", num_neg_entries, "###"


def add_tweets(corpus, query):
   # we only care about english tweets
    tweets = api.search(q=query,lang='en')['results']
    num_entries = 0
    for tweet in tweets:
        # write tweet to file in CSV format
        entry = tweet['from_user'].encode('ascii', 'ignore')
        entry += "," 
        entry += tweet['text'].encode('ascii', 'ignore') 
        entry += "\n"
        corpus.write(entry)
        print "adding tweet", entry
        num_entries += 1
    return num_entries

def sanitize(infile, outfile):
    tweets = []
    in_count = 0
    with open(infile) as f:
        for line in f:
            in_count = in_count + 1
            #ignore multiline tweets
            if ',' in line:
                # remove username
                line = line[line.index(',') + 1:]
                # remove 'RT'
                line = re.sub(r'[ ,]?RT[ ,]?', r'', line)
                # remove @username
                line = re.sub(r'@\w+:?', r'', line)
                # remove #tag
                line = re.sub(r'#\w+', r'', line)
                # make it all lowercase
                line = line.lower()
                # write it out
                tweets.append(line)

    # remove dupes
    filtered_tweets = set(tweets)
    out_count = 0
    with open(outfile, 'w') as f:
        for tweet in filtered_tweets:
            out_count = out_count + 1
            f.write(tweet)
    print "In:", infile, ":", in_count, "tweets"
    print "Out:", outfile, ":", out_count, "tweets"

if __name__ == '__main__':
    threshold = 100000
    #download_tweets('pos_corpus', ":)", threshold)
    sanitize('pos_corpus_test', 'filtered_pos')
    sanitize('neg_corpus_test', 'filtered_neg')
