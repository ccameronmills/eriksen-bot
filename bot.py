from distutils.command.config import config
import praw
import configparser
from datetime import datetime

MISSPELLINGS = [
    "erikson",
    "erickson",
    "ericksson",
    "ericksen",
    "ericson",
    "ericcson",
    "ericsson",
    "erriksen",
    "ericssen",
    "erecksen",
    "ereksen"
    ]
REPLY = "It's Eriksen, not {misspelling}!\n\n---\n\nI'm a bot and I've made {corrections} so far"
SUBREDDIT = "reddevils"
REPLY_ENABLED = True

def main():

    config = configparser.ConfigParser()
    config.read("default.cfg")

    username = config.get("Credentials", "username")

    reddit = praw.Reddit(
        user_agent = config.get("General", "user_agent"),
        client_id = config.get("Credentials", "client_id"),
        client_secret = config.get("Credentials", "client_secret"),
        username = username,
        password = config.get("Credentials", "password")
    )

    bot_user = reddit.redditor(username)
    print("Welcome " + bot_user.name + " (" + bot_user.id + ")")

    try:
        f = open("data/comments_replied.txt", "r")
        replied_to = set(line.strip() for line in f)
        f.close()
    except FileNotFoundError:
        replied_to = set()
        print("No file found for replied to")

    try:
        f = open("data/replies_made.txt", "r")
        replies_made = set(line.strip() for line in f)
        f.close()
    except FileNotFoundError:
        print("No file found for replies made")
        replies_made = set()
        for bot_reply in bot_user.comments.new(limit=None):
            replies_made.add(bot_reply.id)
        populated_replies = len(replies_made)
        if populated_replies > 0: print("Populated " + str(populated_replies) + " replies made from Reddit")
        
    print("Populated " + str(len(replied_to)) + " replies in set")
    subreddit = reddit.subreddit(SUBREDDIT)

    for comment in subreddit.stream.comments():
        normalized_comment = comment.body.lower()
        parsed_date = datetime.utcfromtimestamp(comment.created_utc)
        #print("  " + parsed_date.strftime("%H:%M:%S") + ' - ' + comment.id + ' - ' + comment.body)
        comment_tokens = comment.body.split()
        for token in comment_tokens:
            if token.lower() in MISSPELLINGS:
                if comment.id not in replied_to and comment.id not in replies_made:
                    if REPLY_ENABLED:
                        print("Replying to comment " + comment.id + " containing " + token)
                        reply = REPLY.format(misspelling=token, corrections=str(len(replied_to)))
                        
                        reply_id = comment.reply(body=reply).id
                        replies_made.add(reply_id)
                        with open("data/replies_made.txt", "a+") as f:
                            f.write(reply_id + "\n")

                        replied_to.add(comment.id)
                        with open("data/comments_replied.txt", "a+") as f:
                            f.write(comment.id + "\n")
                    else:
                        print("Found " + token + " in comment " + comment.id)
                    

main()