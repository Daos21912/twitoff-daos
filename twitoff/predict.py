import numpy as np
from .models import User, Tweet
from sklearn.linear_model import LogisticRegression
import spacy


def predict_user(user1_name, user2_name, tweet_text):
    """Determine and returns which user is more likely to say a given Tweet."""
    # SELECT name FROM User WHERE name = <user1_name> LIMIT 1;
    user1 = User.query.filter(User.name == user1_name).one()
    user2 = User.query.filter(User.name == user2_name).one()

    # Vectorize tweets using saved nlp model
    nlp = load_model()
    user1_vecs = np.array([vectorize_tweet(tweet.text, nlp) for tweet in user1.tweets])
    user2_vecs = np.array([vectorize_tweet(tweet.text, nlp) for tweet in user2.tweets])

    # X = embeddings
    # y = labels
    embeddings = np.vstack([user1_vecs, user2_vecs])
    labels = np.concatenate([np.ones(len(user1.tweets)),
                             np.zeros(len(user2.tweets))])

    # Fit a LogisticRegression model on X and y
    log_reg = LogisticRegression().fit(embeddings, labels)

    # Embed the tweet_text using SpaCy vectorizer to use with predictive model
    tweet_embedding = nlp(tweet_text).vector

    # Return the predicted label
    # [0.] = user1  //  [1.] = user2
    return log_reg.predict(np.array(tweet_embedding).reshape(1, -1))


def vectorize_tweet(tweet_text, nlp):
    return nlp(tweet_text).vector


def load_model():
    import en_core_web_sm
    return en_core_web_sm.load()