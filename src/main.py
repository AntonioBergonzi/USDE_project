from argument_parser import create_argparser
from tweet_scraper import scrape_tweets
from util import Entity, Timeframe
import sys
import os
from dotenv import load_dotenv
from process_user import process_user

def main(tweet_archive_path):
    #get the entities from the entities file
    entities = Entity.get_entities(os.path.join(os.path.dirname(os.getcwd()), os.getenv('USER_SET_FILE'))[1:]) #TODO: test on windows
    
    if tweet_archive_path == None: #if no path for the tweets is given, start scraping the tweets and save them in data/archive
        print(os.getcwd())
        tweet_archive_path = os.path.join(os.getcwd(), "data", "tweet_archive")
        scrape_tweets(list(map(lambda x: x.get_profile_name(), entities)), path_archive=tweet_archive_path)
        
    #for each entity, analyze the tweets, perform sentiment analysis and add them to the database
    for entity in entities:
        process_user(tweet_archive_path, entity, entities, sentiment_analysis_function)
        



if __name__ == "__main__":
    load_dotenv()
    arg_parser = create_argparser()
    parsed_args = arg_parser.parse_args(sys.argv[1:])
    main(parsed_args.tweetarchive)
