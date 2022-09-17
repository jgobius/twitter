from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from twitter_search.engine import DatabaseEngine
import pandas as pd

class SentimentAnalysis:

    def __init__(self, 
                 endpoint:str, 
                 key:str,
                 engine:DatabaseEngine) -> None:
        """class for carrying out the sentiment analysis with cognitiveservices from azure
        """        
        self.endpoint = endpoint
        self.key = key
        self.client = self._authenticate_client(self.endpoint, self.key)
        self.engine = engine.engine

    def _authenticate_client(self, endpoint:str, key:str, language:str="nl") -> TextAnalyticsClient:
        """method that picks TextAnalyticsClient with API endpoint.

        Args:
            endpoint (str): api endpoint
            key (str): key
            language (str): language code, standard is dutch

        Returns:
            TextAnalyticsClient: class
        """                    
        ta_credential = AzureKeyCredential(key)
        text_analytics_client = TextAnalyticsClient(
                endpoint=endpoint, 
                credential=ta_credential,
                default_language=language)
        return text_analytics_client


    def analyze(self, df:pd.DataFrame, text_column:str) -> pd.DataFrame:

        if len(df) <= 10:
            df_sent = self.analysis(df=df, text_column=text_column)
        else:

            for i in range(0, len(df), 10):

                df_analysis = self.analysis(df=df[i:i+10], text_column=text_column)

                if i == 0:
                    df_sent = df_analysis
                else:
                    df_sent = df_sent.append(df_analysis)

        primary_key = self.id
        ids = [i for i in range(primary_key, primary_key+len(df_sent))]
        df_sent['id'] = ids

        with self.engine.connect() as conn:
            df_sent.to_sql('sentiment', con=conn, index=False, if_exists='append')

    def analysis(self, df:pd.DataFrame, text_column:str) -> pd.DataFrame:
        """method that carries out sentiment analysis and put output in a pandas df

        Returns:
            pd.DataFrame: dataframe with sentiment analysis to store in prinsjesdag database
        """            

        documents = df[text_column].tolist()
        ids = df['id'].tolist()

        result = self.client.analyze_sentiment(documents)
        doc_result = [doc for doc in result]

        logs = []

        for i, doc in enumerate(doc_result):
            
            if not doc.is_error:

                tweet_id = ids[i]
                positive = doc.confidence_scores.positive
                neutral = doc.confidence_scores.neutral
                negative = doc.confidence_scores.negative
                sentiment = doc.sentiment

                logs.append({'sentiment': sentiment,
                            'positive': positive,
                            'neutral': neutral,
                            'negative': negative,
                            'tweet_id': tweet_id})

        df_sent = pd.DataFrame(logs)
        print(df_sent)
        return df_sent

        
    @property
    def id(self):

        with self.engine.connect() as conn:
            df = pd.read_sql(f'SELECT MAX(id) FROM sentiment', con=conn)
        
        try:
            id = df.loc[0, df.columns[0]] + 1
        except TypeError:
            id = 0

        return id