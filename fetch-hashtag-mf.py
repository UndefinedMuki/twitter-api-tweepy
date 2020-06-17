# https://www.pluralsight.com/guides/building-a-twitter-bot-with-python
import tweepy
import json
import schedule
import time
import datetime
import os
import csv

def isEnglish(text):
    try:
        text.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def get_woeid(api, locations):

    twitter_world = api.trends_available()
    
    places = {loc['name'].lower() : loc['woeid'] for loc in twitter_world};
    
    woeids = []
    
    for location in locations:
        if location in places:
            woeids.append(places[location])
        else:
            print("err: ", location, " woeid does not exist in trending topics")
            
    return woeids

'''
Getting Tweets for the given hashtag with max of 1000 popular tweets with english dialect

    result_type:
        mixed: include both popular and real time results in the response
        recent: return only the most recent results in the response
        popular: return only the most popular results in the response
'''
def get_tweets(api, query):
    tweets = []
    for status in tweepy.Cursor(api.search,
                                q=query,
                                count=1000,
                                result_type='popular',
                                include_entities=True,
                                monitor_rate_limit=True,
                                wait_on_rate_limit=True,
                                lang="en").items():
        # Getting only tweets with has english dialects
        if isEnglish(status.text) == True:
            tweets.append([status.id_str, query, status.created_at.strftime('%d-%m-%Y %H:%M'), status.user.screen_name, status.text])
        
    return tweets

def get_trending_hashtags(api, location):

    woeids = get_woeid(api, location)
    
    trending = set()
    
    for woeid in woeids:
        try:
            trends = api.trends_place(woeid)
            # global
            #trends = api.trends_place("1")
        except:
            print("API limit exceeded. Waiting for next hour")
            #time.sleep(3605) # change to 5 for testing
            time.sleep(5)
            trends = api.trends_place(woeid)
        # Checking for English dialect Hashtags and storing text without # 
        topics = [trend['name'][1:] for trend in trends[0]['trends'] if (trend['name'].find('#') == 0 and isEnglish(trend['name']) == True)]
        trending.update(topics)
        
    return trending
    
def twitter_bot(api, locations):

    today = datetime.datetime.today().strftime("%d-%m-%Y-%S")
    
    if not os.path.exists("trending_tweets"):
        os.makedirs("trending_tweets")
        
    file_tweets = open("trending_tweets/" + today + "-tweets.csv", "a+")
    file_hashtags = open("trending_tweets/" + today + "-hashtags.csv", "w+")
    
    writer = csv.writer(file_tweets)
    
    hashtags = get_trending_hashtags(api, locations)
    
    file_hashtags.write("\n".join(hashtags))
    
    print("Hashtags written to file.")
    
    file_hashtags.close()
    
    for hashtag in hashtags:
        try:
            print("Getting Tweets for the hashtag: ", hashtag)
            tweets = get_tweets(api, "#" + hashtag)
        except:
            print("API limit exceeded. Wait for next hour")
            #time.sleep(0.2) # change to 0.2 sec for testing
            tweets = get_tweets(api, "#" + hashtag)
        for tweet in tweets:
            writer.writerow(tweet)
    
    file_tweets.close()
    
def display_timeline(api):

    public_tweets = api.home_timeline()
    
    for tweet in public_tweets:
        print(tweet.text)
        
def display_user(api, user):

    '''user = api.get_user(user)
    
    print(user.screen_name)
    
    print(user.followers_count)
    
    for friend in user.friends():
        print(friend.screen_name)'''
        
    print(api.search_users('cloud'))
    
    #print(api.lookup_users)
    #print(api.followers)
    #print(api.friends)
      
def display_geoid(api):

    #print(api.reverse_geocode(40.7565926, -73.9665976))
    
    print(api.geo_id("01a9a39529b27f36"))
    
def display_saved_searches(api):

    #print(api.saved_searches())
    print(api.get_saved_search('1264589040621420548'))
    
def display_favorites(api):

    print(api.favorites('studiocikota'))
    
def display_friendships(api):

    #print(api.show_friendship(source_screen_name='realhootlabs', target_screen_name='StudioCikota'))
    
    print(api.friends_ids('studiocikota')) #user follows these users
    #print(api.followers_ids('studiocikota')) #these users follow this user

def display_followers(followers):

    if not followers:
        print()
        print("No followers")
    else:
        print()
        print("Followers")
        print("---------")
        for follower in followers:
            print(follower.screen_name)
            
def display_friends(friends):
    
    if not friends:
        print("No friends :(")
    else:
        print("Friends")
        print("-------")
        for friend in friends:
            print(friend.screen_name)
            
def print_human_format(user):

    print()
    print("ID: \t\t\t\t%s"                % user.id_str)
    print("Name: \t\t\t\t%s"              % user.name)
    print("SN: \t\t\t\t%s"                % user.screen_name)
    print("Location: \t\t\t%s"            % user.location)
    print("Url: \t\t\t\t%s"               % user.url)
    print("Desc: \t\t\t\t%s"              % user.description)
    print("Protected: \t\t\t%s"           % user.protected)
    print("Verified: \t\t\t%s"            % user.verified)
    print("Followers: \t\t\t%d"           % user.followers_count)
    print("Friends: \t\t\t%d"             % user.friends_count)
    print("Listed: \t\t\t%s"              % user.listed_count)
    print("Favorites: \t\t\t%s"           % user.favourites_count)
    print("# of Statuses: \t\t\t%s"       % user.statuses_count)
    print("Created On: \t\t\t%s"          % user.created_at)
    print("Banner Url: \t\t\t%s"          % user.profile_image_url_https)
    print("Default Profile: \t\t%s"       % user.default_profile)
    print("Default Profile Image: \t\t%s" % user.default_profile_image)
    print()
    
def display_format():

    print()
    print("Select format:")
    print()
    print("1: raw JSON")
    print("2: Human Readable")
    print()
    
    while True:
        result = input("Format: ")
        
        if result == "1":
            return 1
        elif result == "2":
            return 2
        else:
            print("Invalid choice")


def display_users(api):

    users = []
    
    while True:
        user_sn = input("Enter users (or press Enter when done): ")
        
        if user_sn:
            users.append(user_sn)
        else:
            break
    
    if len(users) != 0:
        user_list = api.lookup_users(screen_names=users)
        
        for rec in user_list:
            print_human_format(rec)
    
def display_user(api, option):

    # https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/user-object
    
    if option == "1":
        me = api.me()
        friends = api.friends()
        followers = api.followers()
        
        format = display_format()
        
        if format == 1:
            # print me User object in JSON format
            print(json.dumps(me._json, indent=4))
            display_friends(friends)
            display_followers(followers)
        else:
            # print me User object in human format
            print_human_format(me)
            display_friends(friends)
            display_followers(followers)
    else:
        print()
        user_sn = input("Enter id, user id, or screenname: ")
        
        user = api.get_user(user_sn)
        friends = api.friends(user_sn)
        followers = api.followers(user_sn)
        
        format = display_format()
    
        if format == 1:
            # print me User object in JSON format
            print(json.dumps(user._json, indent=4))
            display_friends(friends)
            display_followers(followers)
        else:
            # print me User object in human format
            print_human_format(user)
            display_friends(friends)
            display_followers(followers)
    
def display_menu(api):

    while True:
        print()
        print("*** Twitter Search ***")
        print()
        print("Select an option (or press Enter to quit): ")
        print()
        print("1: Display information about me")
        print("2: Display information about a Twitter user")
        print("3: Display a list of users")
        print()
        
        option = input("Option: ")
        
        if (option == "1" or option == "2"):
            display_user(api, option)
        elif (option == "3"):
            display_users(api)
        else:
            return False
        
def initiate_api():

    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            
        auth = tweepy.OAuthHandler(config["CONSUMER_KEY"], config["CONSUMER_SECRET"])
        
        auth.set_access_token(config["ACCESS_KEY"], config["ACCESS_SECRET"])
        
        api = tweepy.API(auth)
        
        return api
        
    except:
    
        print("Problems with config.json")
        
        return None

def main():
    
    '''
    Use location = [] list for getting trending tags from different countries.
    I have limited number of requests hence I am using only 1 location
    '''
    #locations = ['new york', 'los angeles', 'philadelphia', 'barcelona', 'canada', 'united kingdom', 'india']
    locations = ['united states']
    
    api = initiate_api()
    
    display_menu(api)
    
    # twitter apis
    
    #twitter_bot(api, locations)
    #display_timeline(api)
    #display_user(api, 'studiocikota')
    #display_geoid(api)
    #display_saved_searches(api)
    #display_favorites(api)
    #display_friendships(api)
    
    
    # schedule
    # now = datetime.datetime.today().strftime("%H:%M")
    # schedule.every().day.at("02:20").do(twitter_bot, api, locations)
    # #schedule.every(10).seconds.do(twitter_bot, api, locations)
    # while True:
        # schedule.run_pending()
        # time.sleep(1)
    
    
    # junk / test scenarios
    #print(isEnglish("teÜt"))
    
    #print(api.trends_available())
    
    #with open('mf.json', 'w') as f:
     #   print(api.trends_available(), 'mf.json', file=f)
    
if __name__ == "__main__":
    main()