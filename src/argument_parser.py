import argparse

def create_argparser():
    parser = argparse.ArgumentParser(description='Plot relationships between groups of people.')
    parser.add_argument('--tweetarchive',
                    help='Path to the folder containing the tweets if already downloaded. If it\'s not specified the program will start by downloading the files and storing them in the tweet archive')
    return parser




