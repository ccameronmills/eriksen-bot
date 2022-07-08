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


# open file and populate replies. create file if doesn't exist and seek end
    with open('data/comments_replied.txt', "r") as f:
        replied_to = set(line.strip() for line in f)

    print("Populated " + str(len(replied_to)) + " replies in set")
    subreddit = reddit.subreddit(SUBREDDIT)

    for comment in subreddit.stream.comments():
        normalized_comment = comment.body.lower()
        parsed_date = datetime.utcfromtimestamp(comment.created_utc)
        print("  " + parsed_date.strftime("%H:%M:%S") + ' - ' + comment.id + ' - ' + comment.body)
        for misspelling in MISSPELLINGS:
            if misspelling in normalized_comment:
                if comment.id not in replied_to:
                    if REPLY_ENABLED:
                        print("Replying to comment " + comment.id + " containing " + misspelling)
                        reply = REPLY.format(misspelling=misspelling, corrections=str(len(replied_to)))
                        comment.reply(body=reply)
                        replied_to.add(comment.id)
                        with open("comments_replied.txt", "a+") as f:
                            f.write(comment.id + '\n')
                    else:
                        print("Found " + misspelling + " in comment " + comment.id)
                    

main()