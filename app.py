import os
import pandas as pd
from flask import Flask, render_template, request, jsonify
from sklearn.model_selection import train_test_split
import tweepy
from dotenv import load_dotenv
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
import argparse

load_dotenv()

debug = os.getenv('DEBUG_MODE')

# create an argument parser
parser = argparse.ArgumentParser()
parser.add_argument("-w", "--window", action="store_true", help="show the application in a Window GUI.")
parser.add_argument("-p", "--port", type=int, default=5000, help="specify the port number, default is 5000.")

# parse the command-line arguments
args = parser.parse_args()

# set up Tweepy API client
consumer_key = os.getenv('CONSUMER_KEY')
consumer_secret = os.getenv('CONSUMER_SECRET')
access_token = os.getenv('ACCESS_TOKEN')
access_secret = os.getenv('ACCESS_TOKEN_SECRET')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)

# load the CSV file into a DataFrame
df = pd.read_csv('models/hate_speech_model.csv')

# split the data into feature and target variables
x = df['text']
y = df['is_toxic']

toxicity = 0

# convert the text data into numerical vectors using a CountVectorizer
vectorizer = CountVectorizer()
x = vectorizer.fit_transform(x)

# split the data into training and testing sets
x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=0.2, random_state=42)

# train a logistic regression model on the training data
model = LogisticRegression()
model.fit(x_train, y_train)

app = Flask(__name__)

# function to format number
def format_number(num):
    if num < 1000:
        return str(num)
    elif num >= 1000 and num < 1000000:
        return '{:.1f}K'.format(num / 1000)
    elif num >= 1000000 and num < 1000000000:
        return '{:.1f}M'.format(num / 1000000)
    else:
        return '{:.1f}B'.format(num / 1000000000)

# function to check if a tweet contains hate speech
def is_toxic(text):
    vec = vectorizer.transform([text])
    percentage = round((model.predict_proba(vec)[0][1] * 100), 2)

    if percentage >= 65.00:
        return True
    else:
        return False

# flask app setup
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['GET', 'POST'])
def results():
    if request.method == 'GET':
        return render_template('index.html')

    username = request.form['username']
    posts = int(request.form['posts'])

    # get tweets from Twitter API
    tweets = []
    try:
        for tweet in tweepy.Cursor(api.user_timeline, screen_name=username, tweet_mode='extended').items(posts):
            tweets.append(tweet)
    except tweepy.TweepyException as e:
        return render_template('error.html', error=str(e))

    # perform hate speech detection on the tweets
    labels = [is_toxic(tweet.full_text) for tweet in tweets]

    # compute hate speech detection metrics
    num_hateful = sum(labels)
    num_total = len(tweets)
    hate_speech_ratio = num_hateful / num_total * 100

    # compute the average toxicity percentage
    toxicity = sum([model.predict_proba(vectorizer.transform([tweet.full_text]))[
                   0][1] for tweet in tweets]) / num_total

    # get user's followers and following
    user = api.get_user(screen_name=username)

    name = user.name

    followers_count = user.followers_count
    following_count = user.friends_count

    # convert the counts to K, M, or B format
    followers_count = format_number(followers_count)
    following_count = format_number(following_count)

    # variable tweet_url to store tweet URLs
    for tweet in tweets:
        tweet_url = 'https://twitter.com/{}/status/{}'.format(
            username, tweet.id_str)
        tweet.tweet_url = tweet_url

    # render the results template
    return render_template('results.html',
        username=username,
        posts=posts,
        num_total=num_total,
        num_hateful=num_hateful,
        hate_speech_ratio=hate_speech_ratio,
        tweets=tweets,
        format_number=format_number,
        is_toxic=is_toxic,
        toxicity=toxicity,
        followers_count=followers_count,
        following_count=following_count,
        name=name,
        tweet_url=tweet_url,
    )

@app.route('/api/keys', methods=['GET', 'POST'])
def api_keys():
    if request.method == 'GET':
        api_keys = {
            'CONSUMER_KEY': os.getenv('CONSUMER_KEY'),
            'CONSUMER_SECRET': os.getenv('CONSUMER_SECRET'),
            'ACCESS_TOKEN': os.getenv('ACCESS_TOKEN'),
            'ACCESS_TOKEN_SECRET': os.getenv('ACCESS_TOKEN_SECRET')
        }
        return jsonify(api_keys)
    elif request.method == 'POST':
        api_keys = request.json
        with open('.env', 'w') as f:
            f.write(f"CONSUMER_KEY={api_keys['CONSUMER_KEY']}\n")
            f.write(f"CONSUMER_SECRET={api_keys['CONSUMER_SECRET']}\n")
            f.write(f"ACCESS_TOKEN={api_keys['ACCESS_TOKEN']}\n")
            f.write(f"ACCESS_TOKEN_SECRET={api_keys['ACCESS_TOKEN_SECRET']}\n")
        return jsonify({'message': 'API keys saved successfully'})

if __name__ == '__main__':
    if args.window:
        import webview
        app.config["TEMPLATES_AUTO_RELOAD"] = True
        webview.create_window(
            "Twitter Toxicity Detection",
            app,
            width=850,
            height=700,
            min_size=(600, 700),
        )
        webview.start()
    else:
        app.run(debug=debug, port=args.port)
