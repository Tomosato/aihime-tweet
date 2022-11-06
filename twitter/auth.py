import tweepy


def creat_api(auth_info):
    return tweepy.Client(auth_info["twitter_bearer_token"])
