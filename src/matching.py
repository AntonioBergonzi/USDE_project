def get_matching_dict(tweet_list, entities, preprocessing_function=None):
    """
    Produces the dictionary that saves the mentions of the other entities and returns it along with the dictionary dict[tweet_id]=text_of_tweet
    Returns tuple: (matching_dictionary[other_entity] = [list_of_tweets (the json object)], cache_dict[tweet_id]=text)
    Parameters
    -------------
    tweet_list: list of json objects
        list of the json object that contain the tweets
    entities: list of entity objects
        list of entities to have in the dictionaries (of course the owner of the tweets should not be included)
    preprocessing_function: lambda function 
        Function to apply to the tweets that are put in the cache dict (and that will be fed to the dictionary)
    Returns
    ----------
    Tuple with matching_dictionary and cache dict
    """
    matching_dictionary = {}
    for entity in list(map(lambda x: x.get_profile_name(), entities)):
        matching_dictionary[entity] = []
    cache_dict = {}
    if preprocessing_function == None:
        preprocessing_function = lambda x: x

    for tweet in tweet_list:
        for entity in entities:
            if to_append(entity, tweet):
                matching_dictionary[entity.get_profile_name()].append(tweet)
                if tweet["id"] not in cache_dict: 
                    cache_dict[tweet["id"]] = preprocessing_function(tweet["tweet"])
    return matching_dictionary, cache_dict

def to_append(entity, tweet):
    if entity.get_profile_name() in tweet["tweet"] or (type(tweet["quote_url"])==str and entity.get_profile_name() in tweet["quote_url"]):
        return True
    for alias in entity.get_aliases():
        if alias in tweet["tweet"]:
            return True
    return False
















