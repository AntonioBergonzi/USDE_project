import twint
import os
#takes as input the list of account names, scrapes all the tweets and retweets of those account
def scrape_tweets(accounts, path_archive = "../data/tweet_archive", save_all_fields=False):
    assert type(accounts) == list
    #create a directory before start scraping
    path = os.getcwd()
    path = os.path.join(path, path_archive)
    try:
        os.mkdir(path)
    except Exception:
        print("Directory {} already exists, moving on with scraping".format(path))
    for account in accounts:
        scrape_account_tweets(account, path_archive, save_all_fields=save_all_fields)


def scrape_account_tweets(account, path_archive, save_all_fields = False):
    path_archive = "/home/antonio/Desktop/USDE/USDE_project/data/tweet_archive" #TODO: change to absolute path 
    path = os.path.join(path_archive, account + "_tweets.json")
    if os.path.exists(path):
        print(f"File {path} already exists, deleting it otherwise twint will append the contents creating doubles")
        os.remove(path)
    print(f"Currently scraping {account}, output in {path}")
    o = twint.Config()
    o.Username = account
    if not save_all_fields:
        o.Custom["tweet"] = ["id", "date", "tweet", "link", "quote_url", "retweet"]
    o.Output = path
    o.Hide_output = True
    o.Store_json = True
    print("Printing user object: {}".format(o))
    twint.run.Search(o)
    return path

