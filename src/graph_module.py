import os
from util import Timeframe
from neo4j import GraphDatabase

class NeoGraph:

    def __init__(self, uri, password, timeframe_file_path):
        self.driver = GraphDatabase.driver(uri, auth=("neo4j", password)) #used for creating parallel relationships
        self.timeframes = Timeframe.get_timeframes_from_file(timeframe_file_path)

    def create_entity(self, username, group): 
        if not self.account_exists(username):
            with self.driver.session() as session:
                session.write_transaction(add_entity, username, group)
        else:
            print("WARNING: entity {} is already in the graph".format(username))

    def account_exists(self, username):
        """
        Returns True if a node with the username in input already exists in the db, False otherwise.
        """
        with self.driver.session() as session:
            result=session.read_transaction(check_account_existance, username)
        if len(result) > 0:
            return True
        return False
    
    def tweet_exists(self, from_profile, to_profile ,tweet_id):
        with self.driver.session() as session:
            result = session.read_transaction(check_tweet_existance, from_profile, to_profile, tweet["id"])
        if len(result) > 0:
            return True
        return False

    def add_tweeted_about(self, from_profile, to_profile, tweet_text, tweet_date, tweet_link, tweet_id, sentiment):
        with self.driver.session() as session:
            session.write_transaction(tweeted_about, from_profile, to_profile, tweet_text, tweet_date, tweet_link, tweet_id, sentiment)
        
    def check_existance_timeframe_opinion(self, from_profile, to_profile, timeframe_name):
        with self.driver.session() as session:
            result = session.read_transaction(check_existance_relationship, from_profile, to_profile, timeframe_name)
        if len(result) > 0:
            return True
        return False
    
    def create_timeframe_opinion(self, from_profile, to_profile, timeframe_name, sentiment):
        with self.driver.session() as session:
            result = session.write_transaction(create_timeframe_opinion, from_profile, to_profile, timeframe_name, sentiment)
        
    def update_timeframe_opinion(self, from_profile, to_profile, timeframe_name, sentiment):
        with self.driver.session() as session:
            result = session.write_transaction(update_timeframe_opinion, from_profile, to_profile, timeframe_name, sentiment)


#queries 
def check_tweet_existance(tx, from_account, to_account, id):
    res = []
    results = tx.run("MATCH (n: Account)-[r:TWEETED_ABOUT]->(k:Account) WHERE r.tweetid=$id AND n.username=$from_account AND k.username=$to_account RETURN r.tweetid as id", id = id, from_account = from_account, to_account = to_account)
    for r in results:
        res.append(r["id"])
    return res

def check_account_existance(tx, name):
    res = []
    results = tx.run("MATCH (n: Account) WHERE n.username=$username RETURN n.username as username", username=name)
    for r in results:
        res.append(r["username"])
    return res

def tweeted_about(tx, from_profile, to_profile, text, date, link, tweet_id, sentiment):
    tx.run("MATCH (a: Account), (b: Account) WHERE a.username=$from_username and b.username=$to_username CREATE (a)-[:TWEETED_ABOUT{text: $text, date: date($date), tweetid: $tweet_id, sentiment: $sentiment, link: $link}]->(b)", 
           from_username=from_profile, to_username=to_profile, text=text, date=date, tweet_id=tweet_id, sentiment=sentiment, link=link
    )

def check_existance_relationship(tx, from_username, to_username, timeframe_name): #TODO: da cambiare nella repo vera (redundant)
    res = []
    results = tx.run("MATCH (n: Account)-[r:TIMEFRAME_OPINION]->(k: Account) WHERE n.username=$from_username AND k.username=$to_username AND r.timeframe_name=$timeframe_name RETURN r.average_sentiment as average_sentiment", from_username=from_username, to_username=to_username, timeframe_name=timeframe_name)
    for r in results:
        res.append(r["average_sentiment"])
    return res

def create_timeframe_opinion(tx, from_profile, to_profile, timeframe_name, sentiment):
    tx.run(
        "MATCH (a: Account), (b: Account) WHERE a.username=$from_profile AND b.username=$to_profile CREATE (a)-[:TIMEFRAME_OPINION{average_sentiment: $sentiment, number_tweets: 1, timeframe_name: $timeframe_name}]->(b)",
        from_profile=from_profile, to_profile=to_profile, timeframe_name=timeframe_name, sentiment=sentiment
    )

def update_timeframe_opinion(tx, from_profile, to_profile, timeframe_name, sentiment):
    tx.run(
        "MATCH (n: Account)-[r:TIMEFRAME_OPINION]->(k: Account) \
        WHERE n.username=$from_profile AND k.username=$to_profile AND r.timeframe_name = $timeframe_name \
        SET r.average_sentiment = ((r.average_sentiment*r.number_tweets)+$sentiment)/(r.number_tweets+1)\
        SET r.number_tweets = r.number_tweets + 1"
    , from_profile=from_profile, to_profile=to_profile, sentiment=sentiment, timeframe_name=timeframe_name)

















