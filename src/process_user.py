from matching import get_matching_dict
from util import Entity
import os
import preprocessor as p
p.set_options(p.OPT.URL, p.OPT.EMOJI)
import json

def process_user(path_to_scraped_tweets, entity, entities, sentiment_analysis_classifier, graph):
    """
    Given the path to the tweets that were prevously scraped, the entity to process, the list of all the entities (needed to understand to whom the tweets are referred to), the sentiment analisys classifier and the graph, this function inserts the tweets that the entity has made referring to other entities into the neo4j db
    """    
    file_path = os.path.join(path_to_scraped_tweets, entity.get_profile_name()+"_tweets.json")
    print("Currently processing {}'s tweets".format(entity.get_profile_name()))
    try:
        with open(file_path, "r") as f:
            tweet_list = list(map(lambda x: json.loads(x), f.readlines()))
    except:
        print("This file was not found: {}, not adding anything to the database".format(file_path))
        return
    other_entities = list(filter(lambda x: x.get_profile_name() != entity.get_profile_name(), entities)) #remove the entity that we have to analyse from all the entities
    matching_dict, cache = get_matching_dict(tweet_list, other_entities, preprocessing_function = lambda x: p.clean(x).replace("#", " "))
    if len(cache) > 0:
        # to get the classification of the tweet we use a dict (so if a tweet contains references to two or more entities it gets analyzed once)    
        analysed_dict = sentiment_analysis_classifier.analyse_dict(cache)        
        
        for temp_entity in Entity.get_entities(os.getenv("USER_SET_FILE")):
            graph.create_entity(temp_entity.get_profile_name(), temp_entity.get_group())
        
        for other_entity in matching_dict:
            for tweet in matching_dict[other_entity]:
                graph.add_tweet(entity.get_profile_name(), other_entity, tweet, analysed_dict[tweet["id"]]*1.0)
    else:
        print("WARNING: Found no tweets for user {}, this may be an error".format(entity.get_profile_name()))   

