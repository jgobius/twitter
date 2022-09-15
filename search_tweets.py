from twitter_search.search import Twitter
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-a', '--argument', type=str, help='The query to search tweets. Max 500 characters.')
parser.add_argument('-t', '--twitter_file', type=str, help='location of .env file for twitter')
parser.add_argument('-d', '--database_file', type=str, help='location of .env file for the database')

if __name__ == '__main__':

    args = parser.parse_args()
    twitter = Twitter(twitter_env_file=args.twitter_file,
                      database_env_file=args.database_file, 
                      proxy=False)

    tweets = twitter.search(query=args.argument, filter_on_date=True)
    twitter.to_sql(tweets)





