import os
import sys
import twitter

from twitter.oauth import write_token_file, read_token_file
from twitter.oauth_dance import oauth_dance

APP_NAME ='Movie Sentiment Recommender'
CONSUMER_KEY = '2UX5EoC7ypG0yvkwlOw'
CONSUMER_SECRET = 'yMH5RBJGMlqQLtPZ2XweXtt2kEBjfpxToMOyKg94'

# Most of this is based off of Recipes for Mining Twitter by Russel
def oauth_login(app_name=APP_NAME,
                consumer_key=CONSUMER_KEY, 
                consumer_secret=CONSUMER_SECRET, 
                token_file='auth/twitter.oauth'):

    # try to read the token file
    try:
        (access_token, access_token_secret) = read_token_file(token_file)
    except IOError, e: # if it fails, create the token and write it to disk
        (access_token, access_token_secret) = oauth_dance(app_name, consumer_key,
                                                          consumer_secret)
        if not os.path.isdir('auth'):
            os.mkdir('auth')
        write_token_file(token_file, access_token, access_token_secret)
        print >> sys.stderr, "OAuth Success. Token file stored to", token_file

    # return an authenticated API for search API calls
    return twitter.Twitter(domain='search.twitter.com',
                           auth=twitter.oauth.OAuth(access_token, access_token_secret,
                           consumer_key, consumer_secret))
