from matching import get_matching_dict
import os
import preprocessor as p
p.set_options(p.OPT.URL, p.OPT.EMOJI)
import json

def process_user(path_to_scraped_tweets, entity, entities, sentiment_analysis_class):
    #get dict x["other"] = [tweets (must include text and id at least)]
    file_path = os.path.join(path_to_scraped_tweets, entity.get_profile_name()+"_tweets.json")
    with open(file_path, "r") as f:
        tweet_list = list(map(lambda x: json.loads(x), f.readlines()))
    other_entities = list(filter(lambda x: x.get_profile_name() != entity.get_profile_name(), entities))
    matching_dict, cache = get_matching_dict(tweet_list, other_entities, preprocessing_function = lambda x: p.clean(x).replace("#", " "))

    classifier = sentiment_analysis_class()
    analysed_dict = classifier.analyse_dict(cache) 

    for x in list(cache.keys())[:10]:
        print("Tweet: {}\nSentiment: {}".format(cache[x], analysed_dict[x]))



    #create list of tweets to analyze (return dict[id]=sentiment)
    #TODO: clean tweets
    #TODO: pass the entities that aren't equal to the guy owning the tweets

    #get the previous dictionary and insert the whole thing in the db
    

if __name__ == '__main__':
    from util import *
    from sentiment_analysis import Classifier
    entities = Entity.get_entities("data/user_set_example.json")
    temp = None
    for entity in entities:
        if entity.get_profile_name() == "matteosalvinimi":
            temp = entity

    process_user("data/tweet_archive/", temp, entities, Classifier )