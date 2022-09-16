import tweepy
from tweepy.auth import OAuthHandler
from dotenv import load_dotenv
import os
import pandas as pd
from sqlalchemy import create_engine


class TweetList:

    def __init__(self, search_results:list):

        self.tweets = [Tweet(result) for result in search_results]

    def to_dataframe(self) -> pd.DataFrame:

        df = pd.DataFrame([tweet.data for tweet in self.tweets])

        return df


class Twitter:

    def __init__(self,
                 twitter_env_file:str=None,
                 database_env_file:str=None,
                 proxy:bool=False):

        """
        Class to interact with Twitter api.

        Args:
            twitter_env_file (str,optional): the file with the credentials for the Twitter api. If not provided, set the following
                                             environment variables:
                                             - TWITTER_API_KEY
                                             - TWITTER_API_KEY_SECRET
                                             - TWITTER_ACCESS_TOKEN
                                             - TWITTER_ACCESS_TOKEN_SECRET

            database_env_file (str, optional): the file with the credentials for the database. Defaults to none. If not provided,
                                               please provide the following environment variables:
                                               - USER
                                               - PASSWORD
                                               - SERVER_NAME
                                               - DATABASE_NAME
                                               - DRIVER_NAME

            proxy (bool, optional): check if proxies need to be set. Defaults to False.
        """        

        auth = Authenticator()
        auth.load(database_env_file)
        twitter_auth = auth.authenticate(twitter_env_file)

        self.engine = self._create_database_connection()

        if proxy == False:
            self.api = tweepy.API(twitter_auth)
        else:
            self.api = tweepy.API(twitter_auth, proxy='http://empweb1.ey.net:8443')

        self.api.session.verify = False

    def search(self,   
               query:str, 
               lang:str='nl', 
               result_type:str='recent',
               filter_on_date=True) -> TweetList:

        """
        Method to search Twitter for tweets.

        Args:
            query (str): the search query. Max 500 characters.
            lang (str, optional): language setting. Defaults to 'nl'.
            result_type (str, optional): Specifies what type of search results you would prefer to receive. Options are "mixed", 
                                         "recent" and "popular".
        Returns:
            TweetList: a list of tweets
        """      

        if filter_on_date == True:
            max_id = self._get_most_recent_id()
        else:
            max_id = None

        search_results = self.api.search_tweets(q=query, 
                                                lang=lang,   
                                                result_type=result_type,
                                                since_id=max_id)

        tweets = TweetList([result for result in search_results])
        
        return tweets
    
    def to_sql(self, tweets:TweetList):
        """
        Method to save a TweetList to sql.

        Args:
            tweets (TweetList): _description_
        """        
        df = tweets.to_dataframe()
        
        if not df.empty:
            df = self._modify_dataframe(df)

            with self.engine.connect() as conn:
                df.to_sql('tweets', con=conn, index=False, if_exists='append')

    def _get_most_recent_id(self) -> int:

        with self.engine.connect() as conn:
            df = pd.read_sql('SELECT MAX(id) FROM tweets', con=conn)
        
        if not df.empty:
            max_id = str(df.loc[0, ''])
            return max_id

    def _modify_dataframe(self, df:pd.DataFrame) -> pd.DataFrame:

        df['verified'] = df['verified'].map({False: 0, True: 1}).fillna(2)
        df['possibly_sensitive'] = df['possibly_sensitive'].map({False: 0, True: 1}).fillna(2)
        
        df['created_at'] = pd.to_datetime(df['created_at']).dt.tz_convert(None)

        df = df.astype({'possibly_sensitive': int,
                        'verified': int})

        return df

    def _create_database_connection(self):
        engine = create_engine(f'mssql+pyodbc://{os.environ.get("USER")}:{os.environ.get("PASSWORD")}@{os.environ.get("SERVER_NAME")}/{os.environ.get("DATABASE_NAME")}?driver={os.environ.get("DRIVER_NAME")}')

        return engine


class Authenticator:

    def load(self, env_file:str=None) -> None:

        if env_file != None:
            load_dotenv(env_file)

    def authenticate(self, env_file:str=None) -> OAuthHandler:
        print(os.getenv('TWITTER_API_KEY'))
        self.load(env_file=env_file)
        auth = OAuthHandler(os.getenv('TWITTER_API_KEY'), os.getenv('TWITTER_API_KEY_SECRET'))
        auth.set_access_token(os.getenv('TWITTER_ACCESS_TOKEN'), os.getenv('TWITTER_ACCESS_TOKEN_SECRET'))

        return auth

class Tweet:

    def __init__(self, result):
        self.result = result._json
        self.user = User(self.result.get('user'))

    @property
    def data(self):

        data = {}

        keys = ['created_at', 'id', 'possibly_sensitive', 'text']

        for key in keys:
            data[key] = self.result.get(key)

        data['hashtags'] = self.hashtags
        
        data = {**data, **self.user.data}

        return data

    @property
    def hashtags(self) -> str:

        hash_tags = []

        entity = self.result.get('entities')
        indices = entity.get('hashtags')

        for indice in indices:
            hash_tags.append(indice.get('text'))

        return '||'.join(hash_tags)
    
    def __repr__(self):
        return f'Tweet({self.data})'

class User:

    def __init__(self, user_data:dict):

        self.user_data = user_data
        self.keys = ['user_id', 'user_name', 'screen_name', 'verified', 'favourites_count', 'followers_count']
    
    @property
    def data(self):

        data = {'user_id': self.user_id,
                'user_name': self.user_name,
                'screen_name': self.screen_name,
                'verified': self.verified}

        return data

    @property
    def user_id(self) -> str:

        return self.user_data.get('id')

    @property
    def user_name(self) -> str:

        return self.user_data.get('name')
    
    @property
    def screen_name(self) -> str:

        return self.user_data.get('screen_name')

    @property
    def verified(self) -> str:

        return self.user_data.get('verified')
    
