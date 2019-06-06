#!/usr/bin/python3

# Frank Grimes Twitter Bot
# Written by: Jonathan Charles
# Last Revision: 3/11/17

import tweepy, sys, os, json, random, time, re, pyjokes

# Retrieve credentials from environment variables
consumer_key = os.environ.get('consumer_key')
consumer_secret = os.environ.get('consumer_secret')
access_token = os.environ.get('access_token')
access_token_secret = os.environ.get('access_token_secret')

# Authorize our Twitter credentials
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Import english dictionary text file into a set
with open("en_dict.txt") as word_file:
    english_words = set(word.strip().lower() for word in word_file)

# Global Variables 
myUsername = 'fr4nk_6r1m35'

# Retrieves a random word from the en_dict text file
def get_rand_word():
    return random.sample(english_words,1)[0]

# Generates a random number in range 0..max
def num_gen(max):
    if max < 0:
        max = abs(max)
    elif max == 0:
        max = 100
    return random.randint(0,max-1)

# Choose a hashtag either from trending or a random dictionary word and retweet from it
def retweet():
    decide = numGen(100)
    if decide % 2 == 0:
        hashtag = get_rand_word()
    elif decide % 2 == 1:
        hashtag = trending()
    for tweet in tweepy.Cursor(api.search,q=hashtag).items(10):
        try:
            print('@' + tweet.user.screen_name + ' tweeted ' + tweet.text)
            tweet.retweet()
            print('Frank Grimes: I shared that joyous piece of wisdom with the world!')
            return
        except tweepy.TweepError as e:
            print(e.reason)
        except StopIteration:
            break

# Yields a random hashtag from trending of Sydney
def trending():
    rawtrends = api.trends_place(id=1105779)
    trends = grabtrends[0]['trends'][0:9]
    tags = [trend['name'] for trend in trends]
    return tags[num_gen(len(tags))];

# Follow back the 100 most recent followers of Frank
def follow_back():
    for follower in tweepy.Cursor(api.followers, myUsername).items(100):
        try:
            if not api.show_friendship(source_screen_name=api.me().screen_name,target_screen_name=follower.screen_name)[1].followed_by:
                api.create_friendship(screen_name=follower.screen_name)
                print('Frank Grimes: I am now following ' + follower.screen_name)
        except tweepy.RateLimitError as e:
            print(e.reason)
            return
        except tweepy.TweepError as e:
            print('Follow Back Error: ' + e.reason)
            return

# Tweet something negative or positive to a random follower
def tweet_opinion(mood):

    # Choose a random follower from a set of 100 followers
    l = [follower.screen_name for follower in tweepy.Cursor(api.followers, myUsername).items(100)]
    chosen_one = l[num_gen(len(l))]
    print('Frank Grimes: Today I just really want to tell @' + chosen_one + ' something!')

    # Construct an opinion to share
    adjectives = [
      'brilliant',
      'spectacular',
      'marvelous',
      'perfect',
      'outstanding',
      'good',
      'solid',
      'amazing',
      'awesome'
    ]
    conv = lambda s: "an " + s if s[0] in ['a','e','i','o','u'] else "a " + s
    desc = random.randint(0, len(adjectives) - 1)
    appraises = [
        'I just know that the @' + chosen_one + ' will do great things!',
        'Hey, @' + chosen_one + ' keep striving for your dreams, the sky is the limit!',
        'Hope you are having a great week @' + chosen_one,
        '@' + chosen_one + ' is simply %s person!' % conv(adjectives[desc]),
        'Hey @' + chosen_one + ' that was %s tweet!' % conv(adjectives[desc])
    ]
    insults = [
        "@" + chosen_one + " reminds me of Mr Burns!",
        "@" + chosen_one + " probably uses notepad to write C code",
        "@" + chosen_one + " has bad bangs",
        "@" + chosen_one + " probably ate sand today"
    ]
    if mood == 0:
        comment = appraises[num_gen(len(appraises))]
    elif mood == 1:
        comment = insults[num_gen(len(insults))]
    
    # Tweet opinion
    api.update_status(comment)
    print('Frank Grimes: I just tweeted this, ' + comment)
    return

# Find a tweet from another followers timeline and favourite it
def favourite():

    # Choose a random follower from a set of 100 followers
    l = [follower.screen_name for follower in tweepy.Cursor(api.followers, myUsername).items(100)]
    chosen_one = l[numGen(100) % len(l)]
    print('Author of Tweet: %s' % chosen_one)

    try:
        tweets = api.user_timeline(screen_name=chosen_one)
        for tweet in tweets:
            if not tweet.favorited:
                print('Frank Grimes: I want to favourite this tweet, ' + tweet.text)
                api.create_favorite(tweet.id)
                print('Frank Grimes: I favourited that tweet!')
                return
    except tweepy.TweepError as e:
        print('Favourite Error: ' + e.reason)
    return

# Function providing chat bot characteristics to Frank Grimes in his direct messsages
def direct_message():
    greeting = [
        "^Hi ?",
        "^Hello",
        "^Greetings"
    ]
    greetingRegex = "(" + ")|(".join(greeting) + ")"
    farewell = [
        "^Good ?bye",
        "^Bye",
        "^Cya",
    ]
    farewellRegex = "(" + ")|(".join(farewell) + ")"
    for dm in tweepy.Cursor(api.direct_messages).items(1):
        if re.search(greetingRegex, dm.text, re.IGNORECASE):
            response = "Hi there! If you reply 'Tell me a fun joke' then I will search the internet for a fun joke!"
        elif re.search(farewellRegex, dm.text, re.IGNORECASE):
            response = "Thank you come again!"
        elif re.search(r'.*Tell me a fun joke.*', dm.text, re.IGNORECASE):
            response = pyjokes.get_joke()
        else:
            response = "I usually start my conversations with something like 'Hi' and end them with something like 'Bye'..."
        print('Frank Grimes: I messaged a follower')
        api.send_direct_message(user_id=dm.sender_id, text=response)
    return
    
def init():
    '''
    Frank Grimes is a functional bot and below is his logic since
    he is a systematic being

    Monday: Follow back
    Tuesday: Retweet
    Wednesday: Appraisal
    Thursday: Insult
    Friday: Favourite Tweet and Direct Message recent follower
    Saturday: Follow back
    Sunday: Retweet
    '''
    if time.strftime("%A") == 'Monday':
        print('Frank Grimes: I want to followback my followers')
        follow_back()
    elif time.strftime("%A") == 'Tuesday':
        print('Frank Grimes: I want to retweet')
        retweet()
    elif time.strftime("%A") == 'Wednesday':
        print('Frank Grimes: I want to appraise somebody')
        tweet_opinion(0)
    elif time.strftime("%A") == 'Thursday':
        print('Frank Grimes: I want to diss somebody')
        tweet_opinion(1)
    elif time.strftime("%A") == 'Friday':
        print('Frank Grimes: I want to favourite a tweet')
        favourite()
        print('Frank Grimes: I also need to check in on my twitter direct messages')
        direct_message()
    elif time.strftime("%A") == 'Saturday':
        print('Frank Grimes: I want to followback my followers')
        follow_back()
    elif time.strftime("%A") == 'Sunday':
        print('Frank Grimes: I might just retweet again')
        retweet()
    return

if __name__ == '__main__':
    print('Frank Grimes: I am about to exert my presence in the twittersphere!')
    init()
    print('Frank Grimes: I think I am done with twitter for today!')
