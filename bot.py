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
REPLY = "It's Eriksen, not {misspelling}! --- I'm a bot and I've made {corrections} so far"
SUBREDDIT = "testingground4bots"
REPLY_ENABLED = True

def main():

    config = configparser.ConfigParser()
    config.read("default.cfg")

    reddit = praw.Reddit(
        user_agent = config.get("General", "user_agent"),
        client_id = config.get("Credentials", "client_id"),
        client_secret = config.get("Credentials", "client_secret"),
        username = config.get("Credentials", "username"),
        password = config.get("Credentials", "password")
    )


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
        replies_made = set()
        print("No file found for replies made")

    print("Populated " + str(len(replied_to)) + " replies in set")
    subreddit = reddit.subreddit(SUBREDDIT)

    for comment in subreddit.stream.comments():
        normalized_comment = comment.body.lower()
        parsed_date = datetime.utcfromtimestamp(comment.created_utc)
        print("  " + parsed_date.strftime("%H:%M:%S") + ' - ' + comment.id + ' - ' + comment.body)
        for misspelling in MISSPELLINGS:
            if misspelling in normalized_comment:
                if comment.id not in replied_to and comment.id not in replies_made:
                    if REPLY_ENABLED:
                        print("Replying to comment " + comment.id + " containing " + misspelling)
                        reply = REPLY.format(misspelling=misspelling, corrections=str(len(replied_to)))
                        
                        reply_id = comment.reply(body=reply).id
                        replies_made.add(reply_id)
                        with open("data/replies_made.txt", "a+") as f:
                            f.write(reply_id + "\n")

                        replied_to.add(comment.id)
                        with open("data/comments_replied.txt", "a+") as f:
                            f.write(comment.id + "\n")
                    else:
                        print("Found " + misspelling + " in comment " + comment.id)
                    

main()