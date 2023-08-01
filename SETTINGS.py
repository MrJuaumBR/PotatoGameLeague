from flask import Flask,redirect,url_for,render_template,request, session
from urllib import parse
from zenora import APIClient
from os import environ
import sqlite3 as sql

app = Flask(__name__)
app.template_folder = "pages"
app.static_folder = "static"


SITE_URL = "http://localhost:5000"

CLIENT_SECRET = environ["CLIENT_SECRET"]

app.config['SECRET_KEY'] = environ['SECRET_KEY']

TOKEN = environ['TOKEN']
REDIRECT_URL = str(SITE_URL)+"/oauth/callback"
OAUTH_URL = f"https://discord.com/api/oauth2/authorize?client_id=1043495092977152061&redirect_uri={parse.quote(REDIRECT_URL)}&response_type=code&scope=identify"

client = APIClient(TOKEN,client_secret=CLIENT_SECRET)

class dataManager():
    def __init__(self) -> None:
        self.db = sql.connect('./data/database.db')
        self.cur = self.db.cursor()
        self.autocommit = True

    def exec(self,code):
        self.cur.execute(str(code))
        if self.autocommit:
            self.db.commit()
    
    def convert_create_table(self, columns:list or tuple, types:list or tuple):
        n = ""
        if len(columns) == len(types):
            for i,x in enumerate(columns):
                if i == len(types)-1:
                    n += f"{x} {types[i]}"
                else:
                    n += f"{x} {types[i]}, "
        return str(n)

    def create_table(self,table_name:str, columns:list or tuple, types:list or tuple):
        var = self.convert_create_table(columns, types)
        code = f"""
        CREATE TABLE IF NOT EXISTS {table_name} ({str(var)})
        """
        self.exec(code)

    def insert(self, table:str, column:list or tuple, values: list or tuple):
        code = """

        """
        self.exec(code)

class User():
    def __init__(self,code:str="") -> None:
        if code != "":
            self.access_token = client.oauth.get_access_token(code, REDIRECT_URL).access_token
        else:
            self.access_token = None
        
        self.start() # Multiples Checks

    def start(self):
        if self.access_token:
            self.bearer_client = APIClient(self.access_token,bearer=True)
            self.user = self.bearer_client.users.get_current_user()

            self.authenticated = False
            if not (self.access_token in ['',' ', None, "None"]):
                if self.access_token:
                    if self.bearer_client:
                        if self.user:
                            self.authenticated = True
                        else:
                            self.authenticated = False
                    else:
                        self.authenticated = False
                else:
                    self.authenticated = False
            else:
              self.authenticated = False

    def loadAccessToken(self, code):
        self.access_token = code
        self.start()

Database = dataManager()
"""
DATABASE MANAGER
Columns:
- Id INTEGER PRIMARY KEY
- Title TEXT
- Description TEXT
- Date TEXT
- AuthorId INTEGER NOT NULL
"""
Database.create_table('post',['id','title','description','date','authorid'],['INTEGER PRIMARY KEY','TEXT',"TEXT","TEXT","INTEGER NOT NULL"]) # Create Table of posts
"""
DATABASE MANAGER
Columns:
- Id INTEGER PRIMARY KEY # Discord
- username TEXT # Discord
- Aboutme TEXT # Discord

"""
