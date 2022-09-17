from std_database.datatable.core.datatable import DataTable

# create your models
class Docs(DataTable):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table = 'documents'
        self.columns = """
                       id INT,
                       text VARCHAR(256),
                       PRIMARY KEY (id) 
                       """

class Sentiment(DataTable):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table = 'sentiment'
        self.columns = """
                       id INT,
                       sentiment VARCHAR(256),
                       positive FLOAT,
                       neutral FLOAT,
                       negative FLOAT,
                       text_id INT,
                       PRIMARY KEY (id),
                       FOREIGN KEY (text_id) REFERENCES documents(id)
                       """  

# create your models
# class Docs(DataTable):

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.table = 'documents'

# class Sentiment(DataTable):

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.table = 'sentiment'
