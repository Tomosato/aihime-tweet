import twitter.conf
import sqlite3

"""
初回にいっかいだけ
"""
conf = twitter.conf.load_conf()
db_name = conf['db_name']
conn = sqlite3.connect(db_name)
cur = conn.cursor()

cur.execute("""
            CREATE TABLE PAST_TWEET(TWEET_ID VARCHAR(1000) PRIMARY KEY,
                                    TWEET CLOB)
            """)

conn.commit()
conn.close()