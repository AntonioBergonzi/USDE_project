import json
import datetime

class Entity:
    """
    Represents a twitter account, it also saves its aliases and the group of the account
    Attributes
    --------------------------------
    profile_name: str
        The twitter handle of the entity
    aliases: list of str
        The different names that when matched refer to this account (@realdonaldtrump may have Donald and Trump as aliases)
    group: str
        The group of the account
    """
    def __init__(self, profile_name, aliases, group):
        self._profile_name = profile_name
        assert type(aliases) == list
        self._aliases = aliases
        self._group = group
    
    def get_profile_name(self):
        return self._profile_name
    
    def get_group(self):
        return self._group

    def get_aliases(self):
        return self._aliases
    def __repr__(self):
        return f"Name: {self._profile_name} Aliases: {self._aliases} Group: {self._group}"
    def get_entities(path_to_file):
        """
        Gets the entites from the file and returns a list containing those entities
        Parameters
        -----------
        filename: str
            path to the file
        """
        entities = []
        with open(path_to_file) as f:
            accounts =  json.load(f)
            for account in accounts:
                entities.append(Entity(account["username"], account["aliases"], account["group"]))
        return entities

class Timeframe:
    """
    Class that handles the different periods of time in which the tweet happen, it's used to store the different periods that are to be analyzed and provides a way of testing if a date is included in the timeframe or not.

    Attributes
    -----------
    name: str
        Name of the period of time that we want to store
    from_date: date (formatted as: "%Y-%m-%d")
        Date from which the timeframe starts
    to_date:
        Date that ends the timeframe
    
    Methods
    ---------
    includes(date)
        Returns True if the date is in the timeframe, False otherwise
    Timeframe.convert_to_datetime(date)
        Converts the date formatted as "%Y-%m-%d" and returns the corresponding datetime value
    Timeframe.get_timeframes_from_file(path_to_file)
        Given the path to the file of the timeframe file, creates a list of timeframes (from the file)
    """
    def __init__(self, name, from_date, to_date):
        self._name = name
        self._from_date = Timeframe.convert_to_datetime(from_date)
        self._to_date = Timeframe.convert_to_datetime(to_date)
    def __str__(self):
        return "Timeframe Object:\n\tName: {}\n\tFrom: {}\n\tTo:   {}\n".format(self._name, self._from_date, self._to_date)
    def includes(self, date):
        converted_date = Timeframe.convert_to_datetime(date)
        if converted_date >= self._from_date and converted_date < self._to_date:
            return True
        return False
    def convert_to_datetime(date):
        return datetime.datetime.strptime(date, "%Y-%m-%d")
    def get_timeframes_from_file(path_to_file):
        result = []
        with open(path_to_file) as f:
            timeframes =  json.load(f)
            for timeframe in timeframes:
                result.append(Timeframe(timeframe["name"], timeframe["start"], timeframe["end"]))
        return result
    def get_name(self):
        return self._name

def progress_bar(iterable, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"): #not mine
    total = len(iterable)
    # Progress Bar Printing Function
    def printProgressBar (iteration):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Initial Call
    printProgressBar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)
    # Print New Line on Complete
    print()
