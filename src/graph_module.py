import os
from util import Timeframe
from neo4j import GraphDatabase

class NeoGraph:

    def __init__(self, uri, password, timeframe_file_path):
        print(uri)
        self.driver = GraphDatabase.driver(uri, auth=("neo4j", password)) #used for creating parallel relationships
        self.timeframes = Timeframe.get_timeframes_from_file(timeframe_file_path)

    def create_entity(self, username, group): 
        if not self.account_exists(username):
            with self.driver.session() as session:
                session.write_transaction(add_entity, username, group)
        
    def add_tweet(self, from_profile, to_profile, tweet, sentiment):
        """
        Adds a single tweet to the database.
        Also handles the :TIMEFRAME_OPINION relationships
        Parameters
        ----------
        from_profile: str
            The handle of the twitter account that posted the tweet
        to_profile: str
            The handle of the twitter account that is on the receiving end of the tweet (of course this is not present in every tweet scraped, the graph stores only the tweets that have the to_profile though, as it enstablishes a relationship)
        tweet: str
            The json representation of the tweet, must contain date and text of the tweet
        sentiment: integer
            1 if the sentiment is positive, -1 if it's not positive and 0 if it's neutral 
        """
        if not self.tweet_exists(from_profile, to_profile, tweet["id"]):
            valid_timeframes = self.get_valid_timeframes(tweet["date"])
            for timeframe_name in map(lambda x: x.get_name(), valid_timeframes):
                self.add_tweeted_about(from_profile, to_profile, tweet["tweet"], tweet["date"], tweet["link"], tweet["id"], sentiment)
                if self.check_existance_timeframe_opinion(from_profile, to_profile, timeframe_name):
                    self.update_timeframe_opinion(from_profile, to_profile, timeframe_name, sentiment)
                else:
                    self.create_timeframe_opinion(from_profile, to_profile, timeframe_name, sentiment)
        else:
            print("Tweet with id {} from {} to {} is already present in the db".format(tweet["id"], from_profile, to_profile))

    def account_exists(self, username):
        """
        Returns True if a node with the username in input already exists in the db, False otherwise.
        """
        with self.driver.session() as session:
            result=session.read_transaction(check_account_existance, username)
        if len(result) > 0:
            return True
        return False

    def get_valid_timeframes(self, date):
        result = []
        for timeframe in self.timeframes:
            if timeframe.includes(date):
                result.append(timeframe)
        return result
    def tweet_exists(self, from_profile, to_profile ,tweet_id):
        with self.driver.session() as session:
            result = session.read_transaction(check_tweet_existance, from_profile, to_profile, tweet_id)
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

def add_entity(tx, name, group):
    tx.run("CREATE (n:Account {username: $username, group: $group})", username=name, group=group)

if __name__ == "__main__":
    print(os.getcwd())
    graph = NeoGraph("neo4j://localhost:7687", "1234", "data/timeframe_example.json")
    
    from util import Entity
    import json
    for entity in Entity.get_entities("data/user_set_example.json"):
        graph.create_entity(entity.get_profile_name(), entity.get_group())
    tweet1 = '{"id": 1342019539488432127, "date": "2020-12-24", "tweet": "La mia intervista di ieri sera a #portaaporta ➡️  https://t.co/kldkEeYDDA", "link": "https://twitter.com/GiuseppeConteIT/status/1342019539488432129", "quote_url": "", "retweet": false}'
    tweet2 = '{"id": 1341813611115798533, "date": "2020-12-23", "tweet": "Il prossimo ritorno in Italia di #ChicoForti è davvero una bella notizia. Un ringraziamento al Ministro @luigidimaio e a tutto il corpo diplomatico italiano per la determinazione e l\'impegno che hanno permesso di raggiungere questo importante risultato.", "link": "https://twitter.com/GiuseppeConteIT/status/1341813611115798533", "quote_url": "", "retweet": false}'
    tweet3 = '{"id": 1341763611560165378, "date": "2020-12-23", "tweet": "Questa sera sarò ospite a #PortaaPorta. Dalle 23.20 su Rai Uno.  https://t.co/NFV8Kaly5p", "link": "https://twitter.com/GiuseppeConteIT/status/1341763611560165378", "quote_url": "", "retweet": false}'
    graph.add_tweet("GiuseppeConteIT","matteosalvinimi", json.loads(tweet1), -1.0)
    graph.add_tweet("GiuseppeConteIT","matteosalvinimi", json.loads(tweet2), 0.0)
    graph.add_tweet("GiuseppeConteIT","luigidimaio", json.loads(tweet3),1.0)











