from nltk.corpus import movie_reviews
from nltk import NaiveBayesClassifier
from nltk import FreqDist
import operator

tagged_tweets = []
word_freq = {}

def add_to_category(filename, category):
    n = 0
    with open(filename) as f:
        for line in f:
            n = n + 1
            words = line.strip().split()
            # add lists of words and category to tagged_tweets
            tagged_tweets.append([words, category])
            #print "Adding", category, ":", words
            # add all words in the tweet into the frequency distribution
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1  
    print "num category:", n

def unigram_features(doc):
    doc_words = set(doc)
    features = {}
    for word in sorted_words:
        features['contains(%s)' % word[0]] = (word[0] in doc_words)
    return features

def eval_classifier(classifier, judgements_file):
    correct = 0
    incorrect = 0
    with open(judgements_file) as f:
        for line in f:
            (label, tweet) = line.strip().split(',', 1)
            class_label = classifier.classify(unigram_features(tweet.lower().split()))
            if label == class_label:
                correct += 1
                print "Correctly labeled as:", label, ":", tweet
            else:
                incorrect += 1
                print label, "incorrectly labeled as:", class_label, ":", tweet

    print "Num correct:", correct
    print "Num incorrect:", incorrect
    print "Percentage:", float(correct) / float(correct + incorrect)


add_to_category('f_pos_small', 'pos')
add_to_category('f_neg_small', 'neg')

# select the most frequent 1000 words
sorted_words = sorted(word_freq.iteritems(), key=operator.itemgetter(1))
sorted_words.reverse()
sorted_words = sorted_words[:1000]
    
train_set = [(unigram_features(d), c) for (d,c) in tagged_tweets]
classifier = NaiveBayesClassifier.train(train_set)

eval_classifier(classifier, 'judgements.txt')
