import csv
import datetime
import sqlite3
import discord
import string
import twitter.auth
import twitter.conf

TWEET_URL = "https://twitter.com/{}/status/{}"

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def create_massages():
    """
    これを呼んで処理する想定。
    """

    past_created_at = None
    # 過去の取得情報を取得する。
    with open('past_result.csv') as c:
        reader = csv.reader(c)

        # 先頭だけ取ってくる
        for row in reader:
            past_created_at = datetime.datetime.fromisoformat(row[0])
            break
    
    conf = twitter.conf.load_conf()
    twitter_client = twitter.auth.creat_api(conf)
    tweet_fields = ["created_at", "referenced_tweets"]

    response = twitter_client.get_users_tweets(id=conf["twitter_id"], 
                                        tweet_fields=tweet_fields,
                                        start_time=past_created_at).data
    post_target = list()
    for tweet_data in reversed(response):

        if is_post_target(tweet_data, past_created_at):
            post_target.append(tweet_data)

    with open("discode_template.txt") as t:
        template_message = string.Template(t.read())

    post_massages = list()
    screen_name = conf["twitter_screen_name"]
    csv_record_target = None
    for tweet in post_target:

        if tweet.referenced_tweets != None:
            if (tweet.referenced_tweets[0].type == "retweeted"):
                twitter_url = create_retweet_url(tweet, twitter_client)
            else:
                twitter_url = TWEET_URL.format(screen_name, tweet.id)
        else:
            twitter_url = TWEET_URL.format(screen_name, tweet.id)

        post_massage = template_message.safe_substitute({"twitter_url": twitter_url})
        post_massages.append(post_massage)

        csv_record_target = [tweet.created_at, tweet.id]

    if(csv_record_target != None):
        with open("past_result.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerow(csv_record_target)

    return post_massages

def create_retweet_url(tweet, twitter_client):
    """
    そのユーザのscreen nameとリツイートのIDを取得してURLを作る
    """
    tweet_fields = ["author_id", "created_at"]
    retweet = twitter_client.get_tweet(tweet.referenced_tweets[0].id,
                                       tweet_fields=tweet_fields)

    tweeted_user = twitter_client.get_user(id=retweet.data.author_id)
    screen_name = tweeted_user.data.username

    return TWEET_URL.format(screen_name, retweet.data.id)

def is_post_target(tweet_data, past_created_at):
    """
    投稿の対象であるか確認する
    """
    is_target_from_db = is_post_target_for_db(tweet_data.id)

    if past_created_at != None:
        return post_cond_detail(tweet_data, past_created_at)
    elif tweet_data.referenced_tweets == None & \
        is_target_from_db:
        # 普通のツイートで過去にも出したことのあるツイートではない。
        return True
    elif (tweet_data.referenced_tweets[0].type != "replied_to") :
        # 過去の情報が全くない(初めて動かす)ときは、リプライ以外は対象にする。
        return True


def post_cond_detail(tweet_data, past_created_at):
    """
    過去ツイートよりも新しい?
    リプライ以外のもの。(ツイート, リツイート, 引用リツイート)
    """
    if tweet_data.referenced_tweets == None:
        return True
    elif  past_created_at > tweet_data.created_at:
        # 過去の投稿のほうが新しい
        return False
    elif (tweet_data.referenced_tweets[0].type != "replied_to") & \
        (tweet_data.created_at > past_created_at) :
        # 新しくとったやつが新しくて、リプライ以外
        return True
    
    return False


def is_post_target_for_db(tweet_id):
    """
    DBから検索してみて、今投稿しようとしているものが
    過去に投稿したものであるか確認する。
    """

    conf = twitter.conf.load_conf()
    db_name = conf['db_name']
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    sql = """
            SELECT COUNT(TWEET_ID) FROM PAST_TWEET WHERE TWEET_ID = ?
        """
    sql_result_list = cur.execute(sql, (str(tweet_id),)).fetchall()

    for sql_result in sql_result_list:
        if(sql_result[0] == 0):
            return False
        else:
            return True

@client.event
async def on_ready():
    conf = twitter.conf.load_conf()
    post_target_massages = create_massages()
    for tweet_message in post_target_massages:
        await client.get_channel(conf["discord_message_target"]).send(tweet_message)
    
    await client.close()

@client.event
async def on_disconnect():
    print("finish!")

conf = twitter.conf.load_conf()
client.run(conf["discord_bot_token"])