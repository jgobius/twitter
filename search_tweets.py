from cgitb import text
from twitter_search.engine import DatabaseEngine
from twitter_search.search import Authenticator, Twitter
from sentiment_analyzer.model import SentimentAnalysis

from argparse import ArgumentParser
import pandas as pd
from datetime import datetime
import os

class Logging:

    def __init__(self, 
                 table:str,
                 engine:DatabaseEngine) -> None:

        self.engine = engine.engine
        self.table = table

    def info(self, message:str) -> None:

        log_dict = {'id': self.id,
                    'log_type': 'INFO',
                    'log_message': message,
                    'created_at': datetime.now()
                    }

        self._to_sql(log_dict)


    def error(self, message:str) -> None:

        log_dict = {'id': self.id,
                    'log_type': 'ERROR',
                    'log_message': message,
                    'created_at': datetime.now()
                    }
        
        self._to_sql(log_dict)

    def _to_sql(self, log_dict:dict) -> None:
        
        df = pd.DataFrame(log_dict, index=[0])

        with self.engine.connect() as conn:
            df.to_sql(self.table, con=conn, index=False, if_exists='append')

    @property
    def id(self):

        with self.engine.connect() as conn:
            df = pd.read_sql(f'SELECT MAX(id) FROM {self.table}', con=conn)
        
        try:
            id = df.loc[0, df.columns[0]] + 1
        except TypeError:
            id = 0

        return id


parser = ArgumentParser()
parser.add_argument('-a', '--argument', type=str, help='The query to search tweets. Max 500 characters.')
parser.add_argument('-t', '--twitter_file', type=str, help='location of .env file for twitter')
parser.add_argument('-d', '--database_file', type=str, help='location of .env file for the database')
parser.add_argument('-s', '--sentiment_file', type=str, help='location of .env file Azure Cognitive Services api')


if __name__ == '__main__':

    try:

        args = parser.parse_args()

        auth = Authenticator()
        auth.load(env_file=args.database_file)
        auth.load(env_file=args.sentiment_file)

        database_engine = DatabaseEngine()

        logging = Logging(table='logs', engine=database_engine)
        
        twitter = Twitter(twitter_env_file=args.twitter_file,
                          engine=database_engine, 
                          proxy=False)

        sentiment_analysis = SentimentAnalysis(endpoint=os.environ.get('SENT_ENDPOINT'),
                                               key=os.environ.get('SENT_KEY'),
                                               engine=database_engine)

        tweets = twitter.search(query=args.argument, filter_on_date=True)
        logging.info(f'Number of tweets: {len(tweets.to_dataframe())}')

        if not tweets.to_dataframe().empty:
            twitter.to_sql(tweets)
            logging.info(f'Tweets saved to database')

            sentiment_analysis.analyze(df=tweets.to_dataframe(), text_column='text')
            logging.info('Sentiment analyzed')

    except Exception as e:

        logging.error(str(e))





