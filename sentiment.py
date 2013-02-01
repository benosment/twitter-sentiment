import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing
from oauth import oauth_login
import nb_classifier

# configuration
DATABASE = 'sentiment.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

api = None

# TODO -- schema for database is not complete
# method to easly connect to the database specified
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

# initialize the database
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

def insert_movie(title):
    # add a movie title if it hasn't been added before
    g.db.execute('INSERT into MOVIES (title) ' \
                 'SELECT (?) ' \
                 'WHERE NOT EXISTS (SELECT 1 FROM MOVIES WHERE title=(?))', [title, title])
    g.db.commit()

def select_movie_id(title):
    cur = g.db.execute('SELECT id from MOVIES where title=(?)', [title])
    result = cur.fetchone()
    return result[0]

def insert_tweet(tweet_dic, movie_id, sentiment):
    # no need to check for previousily added tweets?
    g.db.execute('INSERT into TWEETS(text, username, sentiment, movie_id)' \
                 'values (?, ?, ?, ?)', \
                 [tweet_dic['text'], tweet_dic['from_user'], sentiment, movie_id])
    g.db.commit()

def select_tweets(movie_id):
    cur = g.db.execute('SELECT * from TWEETS where movie_id=(?)', [movie_id])
    return cur.fetchall()

def analyze_tweet(tweet):
    if tweet['iso_language_code'] != 'en':
        return None
    text = tweet['text']
    unigram_text = text.lower().split()
    return nb_classifier.classifier.classify(nb_classifier.unigram_features(unigram_text))

@app.route('/query', methods=['POST'])
def query():
    results = None
    if request.form['title']:
        flash('Results for the query "%s"' % request.form['title'])

        # add movie to the database
        insert_movie(request.form['title'])
        # grab the id of the previousily added movie (TOD0: can this be combined?)
        movie_id = select_movie_id(request.form['title'])
        tweets = api.search(q='"%s"' % request.form['title'], lang='en')['results']
        # TODO -- use executemany?
        for tweet in tweets:
            # analyze tweet
            sentiment = analyze_tweet(tweet)
            # if positive or negative, add to the databas
            if sentiment:
                insert_tweet(tweet, movie_id, sentiment)

        # do a SELECT to find do count of positive/negatve?
        total_tweets = select_tweets(movie_id)
        # TODO -- make this into a list comphrension 
        num_pos = 0
        num_neg = 0
        results = []
        for tweet in total_tweets:
            # build a dictionary for each entry
            # need to adjust the template accordingly
            result = {}
            result['user'] = tweet[2]
            result['text'] =  tweet[1]
            result['sentiment'] = tweet[3]
            results.append(result)

            # keep a count of the number of positive/negative
            if tweet[3] == 'pos':
                num_pos += 1
            else:
                num_neg += 1
        percentage = round(float(num_pos) / (num_pos + num_neg), 2)
    else:
        error = 'You need to specify a query'
        #return redirect(url_for('index'), error=error)
        return render_template('index.html', error=error)

    return render_template('results.html', results=results, 
                           num_pos=num_pos, num_neg=num_neg, percentage=percentage)


if __name__ == '__main__':
    # create the main API handle 
    api = oauth_login()
    app.run()
