from matching import get_matching_dict
from util import Entity
import os
import preprocessor as p
p.set_options(p.OPT.URL, p.OPT.EMOJI)
import json
from graph_module import NeoGraph

def process_user(path_to_scraped_tweets, entity, entities, sentiment_analysis_classifier, graph):
    
    file_path = os.path.join(path_to_scraped_tweets, entity.get_profile_name()+"_tweets.json")
    try:
        with open(file_path, "r") as f:
            tweet_list = list(map(lambda x: json.loads(x), f.readlines()))
    except:
        print("This file was not found: {}, not adding anything to the database".format(file_path))
        return
    other_entities = list(filter(lambda x: x.get_profile_name() != entity.get_profile_name(), entities))
    matching_dict, cache = get_matching_dict(tweet_list, other_entities, preprocessing_function = lambda x: p.clean(x).replace("#", " "))
    if len(cache) > 0:    
        analysed_dict = sentiment_analysis_classifier.analyse_dict(cache) 
        print("Cache: {}".format(len(cache)))
        print("Analyzed: {}".format(len(analysed_dict)))
        #for x in list(cache.keys())[:10]:
        #    print("Tweet: {}\nSentiment: {}".format(cache[x], analysed_dict[x]))
        
        
        for temp_entity in Entity.get_entities(os.getenv("USER_SET_FILE")):
            graph.create_entity(temp_entity.get_profile_name(), temp_entity.get_group())
        
        for other_entity in matching_dict:
            for tweet in matching_dict[other_entity]:
                print("Adding to db: {} -> {}, id = {}".format(entity.get_profile_name(), other_entity, tweet["id"]))
                graph.add_tweet(entity.get_profile_name(), other_entity, tweet, analysed_dict[tweet["id"]]*1.0)
    else:
        print("WARNING: Found no tweets for user {}, this may be an error".format(entity.get_profile_name()))   

if __name__ == '__main__':
    from util import *
    from sentiment_analysis import Classifier
    from dotenv import load_dotenv
    load_dotenv()
    classifier = Classifier()
    graph = NeoGraph(os.getenv('URI'), os.getenv('DB_PASSWORD'), os.getenv('TIMEFRAME_FILE'))
    entities = Entity.get_entities("data/user_set_example.json")
    # temp = None
    # for entity in entities:classifier
    #     if entity.get_profile_name() == "robersperanza":
    #         temp = entity
    for entity in entities:
        print("Processing profile: {}".format(entity.get_profile_name()))
        process_user("data/tweet_archive/", entity, entities, classifier, graph)