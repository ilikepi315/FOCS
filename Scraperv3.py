import tweepy
import time
import math
#import easygui
import pandas as pd
import os
import re
import json
import datetime

today = datetime.date.today().strftime("%Y_%m_%d")
cwd = os.getcwd()

clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')

def timecalc(prvtime, no_completed):
    now = datetime.datetime.now()
    diff = now - prvtime
    sec_per = datetime.timedelta.total_seconds(diff)/no_completed
    
    return sec_per, now

def removephrase(text, rem):
    joined = ""
    if (type(rem) is str):
        spl = text.split(rem)
        joined = "".join(spl)
    elif (type(rem) is list):
        joined = text
        for phrase in rem:
            spl = joined.split(phrase)
            joined = "".join(spl)
    return joined

def deEmojify(text):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)

keys_file = open('keys.json')
keys = json.load(keys_file)
keys_file.close()

consumer_key = keys['consumer_key']
consumer_secret = keys['consumer_secret']

access_token = keys['access_token']
access_secret = keys['access_secret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

to_search = input("Which user do you want to get open friends from?\n@")

column_names = ["screen_name", "link", "name", "description", "openings_info"]
data = pd.DataFrame(columns = column_names)

friends_id_list = api.friends_ids(screen_name=to_search)
friends = len(friends_id_list)

i = 1
prv = datetime.datetime.now()
timeout_buffer = False
buffer_time = 0

for friend_id in friends_id_list:

    friend = api.get_user(friend_id)
    
    desc_clean = friend.description.lower()
    desc_clean = removephrase(desc_clean, ["opening","but open","not open","reopen","re-open","dms open","dm open","open to","open by","open up","open side","open-minded","openminded","open minded"])

    if ("opening" in friend.description.lower() or "reopen" in friend.description.lower() or "re-open" in friend.description.lower() or "open by" in friend.description.lower() or "open via" in friend.description.lower()):
        print("Opening Info Found")
        tw_link = "https://twitter.com/" + friend.screen_name
        new_row = {"screen_name":friend.screen_name, "link":tw_link, "name":friend.name, "description":deEmojify(friend.description.replace(",","")), "openings_info":"True"}
        data = data.append(new_row, ignore_index=True)

    if ("open" in desc_clean or "open" in friend.name.lower()):
        print("Opening Found")
        tw_link = "https://twitter.com/" + friend.screen_name
        new_row = {"screen_name":friend.screen_name, "link":tw_link, "name":friend.name, "description":deEmojify(friend.description.replace(",","")), "openings_info":"False"}
        data = data.append(new_row, ignore_index=True)
    
    print(i, friend.screen_name)

    if (i % 10 == 0):
        sec_per_buf, prv = timecalc(prv, 10)
        sec_per = sec_per_buf - buffer_time
        total_time = sec_per_buf*(friends-i)
        hrs_left= math.floor(total_time/3600)
        mins_left= math.floor(total_time/60)
        secs_left= math.floor(total_time % 60)

        status = api.rate_limit_status()
        time_until_reset = datetime.datetime.fromtimestamp(int(status['resources']['users']["/users/:id"]["reset"]))-datetime.datetime.now()
        sec_until_reset = datetime.timedelta.total_seconds(time_until_reset)

        rem_calls = int(status['resources']['users']["/users/:id"]["remaining"])
        sec_until_timeout=sec_per*rem_calls
        print("{:.3f} seconds until timeout ({} calls @ {}s per call). {:.3f} seconds until reset".format(sec_until_timeout, rem_calls, sec_per, sec_until_reset))

        if (sec_until_timeout<sec_until_reset):
            timeout_buffer = True
            buffer_time = (10+sec_until_reset-sec_until_timeout)/rem_calls
            print("Applying buffer of {:.3f} seconds".format(buffer_time))
        else:
            timeout_buffer = False
        
        print("Time Left - {:0>2d}:{:0>2d}:{:0>2d}".format(hrs_left,mins_left,secs_left))

    if timeout_buffer:
        time.sleep(buffer_time)

    i += 1

output_file = __file__
output_file = output_file.split("\\")
output_file.pop()
output_file = "\\".join(output_file)
output_file += "\\output\\{}_{}.csv".format(to_search,today)

data = data.sort_values(by = ["openings_info", "name"])
data.to_csv(output_file)

