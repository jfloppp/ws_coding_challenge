import tweepy
import os
import json
from requests_oauthlib import OAuth1Session
import csv


consumer_key = "8cSPUHtr3WnOgkF6f8HhCC6et"
consumer_secret = "dXlttGjb6pfT5keQKmCytbrFaFfwCPoIAFiwxnYyZ01rF5a49I"
access_token = "1213983116378787840-I0FIBuj83t1j5aRbvHi0JbGLJRITkn"
access_secret = "UHT3wuEDBvj2cYED8ZhmE9vS9km4FIwMhaMLXZudjIjlS"

# Authenticate to twitter
auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_token,access_secret)

api = tweepy.API(auth)

# Check whether authentication worked
try:
    api.verify_credentials()
    print('Success')
except:
    print('Failed Auth')

# Grab desired user fields
fields = "created_at,pinned_tweet_id,description"
params = {
    "user.fields": fields,
    "expansions": "pinned_tweet_id" 
}

request_token_url = "https://api.twitter.com/oauth/request_token"
oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

try:
    fetch_response = oauth.fetch_request_token(request_token_url)
except ValueError:
    print(
        "There may have been an issue with the consumer_key or consumer_secret you entered."
    )

resource_owner_key = fetch_response.get("oauth_token")
resource_owner_secret = fetch_response.get("oauth_token_secret")
print("Got OAuth token: %s" % resource_owner_key)

# Get authorization
base_authorization_url = "https://api.twitter.com/oauth/authorize"
authorization_url = oauth.authorization_url(base_authorization_url)
print("Please go here and authorize: %s" % authorization_url)
verifier = input("Paste the PIN here: ")

# Get access token
access_token_url = "https://api.twitter.com/oauth/access_token"
oauth = OAuth1Session(
    consumer_key,
    client_secret=consumer_secret,
    resource_owner_key=resource_owner_key,
    resource_owner_secret=resource_owner_secret,
    verifier=verifier,
)
oauth_tokens = oauth.fetch_access_token(access_token_url)

access_token = oauth_tokens["oauth_token"]
access_token_secret = oauth_tokens["oauth_token_secret"]

# Make request
oauth = OAuth1Session(
    consumer_key,
    client_secret=consumer_secret,
    resource_owner_key=access_token,
    resource_owner_secret=access_token_secret,
)

response = oauth.get("https://api.twitter.com/2/users/me", params=params)

if response.status_code != 200:
    raise Exception(
        "Request returned an error: {} {}".format(response.status_code, response.text)
    )

print("Response code: {}".format(response.status_code))

json_response = response.json()

# Extract info for csv
user_data = json_response["data"]
user_id = user_data["id"]
user_name = user_data["username"]
created_at = user_data["created_at"]
pinned_tweet_id = ""
if "includes" in json_response and "tweets" in json_response["includes"]:
    pinned_tweets = json_response["includes"]["tweets"]
    if len(pinned_tweets) > 0:
        pinned_tweet_id = pinned_tweets[0]["id"]

# Write data to csv
csv_file = "twitter_data.csv"
with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Username", "CreationDate", "PinnedTweetID", "UserID"])
    writer.writerow([user_name, created_at, pinned_tweet_id, user_id])
