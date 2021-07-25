import tweepy

consumer_key = "rsSNHVcrgw1QmWsZTvVm3m2Cj"
consumer_secret = "BUwwQz7xzrmLkuhibHDxNRVTvTB8rqwjficBrG5ee9A4goYsEf"

access_token = "977303742671306752-dqIP1EL8u6Mf5nJsUtmOQ7wZFkuFQbl"
access_secret = "1iJKiJVHDHZmWofSIdLOpfw3AQLAbKJ1DPOP6eLHJPigL"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
print(api.rate_limit_status()['resources'])
friends = api.friends_ids(screen_name="TybaDeer")

j=1

for i in friends[1:10]:
    cur = api.get_user(i)
    print(j, cur.screen_name)
    print(api.rate_limit_status()['resources']['users']["/users/:id"])
    print(api.rate_limit_status()['resources']['friends']['/friends/ids'])
    j += 1

