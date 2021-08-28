from argument_parser import create_argparser
from tweet_scraper import scrape_tweets
from util import Entity
import sys
import os
from dotenv import load_dotenv
from process_user import process_user
from sentiment_analysis import Classifier
from graph_module import NeoGraph

def main(tweet_archive_path):
    #get the entities from the entities file
    print("os.getcwd = {}".format(os.path.dirname(os.getcwd())))
    print("full path: {}".format((os.path.join(os.path.dirname(os.getcwd()), os.getenv('USER_SET_FILE')))))
    entities = Entity.get_entities(os.getenv('USER_SET_FILE')) #requires absolute path
    
    if tweet_archive_path == None: #if no path for the tweets is given, start scraping the tweets and save them in data/archive
        print(os.getcwd())
        tweet_archive_path = os.path.join(os.getcwd(), "data", "tweet_archive")
        scrape_tweets(list(map(lambda x: x.get_profile_name(), entities)), path_archive=tweet_archive_path)
    else:
        print("It works!")
    #tweet_archive_path = "/home/antonio/Desktop/USDE/USDE_project/data/tweet_archive/"
    #set up the classifier and the graph
    
    classifier = Classifier()
    print("Authenticating with: URI: {}, PASSWORD: {}, TIMEFRAME: {}".format(os.getenv('URI'), os.getenv('DB_PASSWORD'), os.getenv('TIMEFRAME_FILE')))
    graph = NeoGraph(os.getenv('URI'), os.getenv('DB_PASSWORD'), os.getenv('TIMEFRAME_FILE'))
    entities = Entity.get_entities(os.getenv('USER_SET_FILE'))

    #for each entity, analyze the tweets, perform sentiment analysis and add them to the database
    for entity in entities:
        process_user(tweet_archive_path, entity, entities, classifier, graph)
        



if __name__ == "__main__":
    load_dotenv()
    arg_parser = create_argparser()
    parsed_args = arg_parser.parse_args(sys.argv[1:])
    main(parsed_args.tweetarchive)
