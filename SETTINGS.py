from flask import Flask, redirect, url_for, render_template, request, session, flash, render_template_string
from jinja2 import pass_context, Template, filters
from markupsafe import Markup

from urllib import parse
from zenora import APIClient
from os import environ, path, mkdir
import sqlite3 as sql
import json
from datetime import datetime

app = Flask(__name__, "/", "./static")
app.template_folder = "pages"
app.static_folder = "static"

#@pass_context
def jineval(need_eval):
    evalued = eval(need_eval)
    return evalued

filters.FILTERS['jineval']=  jineval

if not path.exists('./data'):
    mkdir('./data/')

SITE_URL = "http://localhost:5000"

CLIENT_SECRET = environ["CLIENT_SECRET"]

app.config["SECRET_KEY"] = environ["SECRET_KEY"]

TOKEN = environ["TOKEN"]
REDIRECT_URL = str(SITE_URL) + "/oauth/callback"
OAUTH_URL = f"https://discord.com/api/oauth2/authorize?client_id=1043495092977152061&redirect_uri={parse.quote(REDIRECT_URL)}&response_type=code&scope=identify%20email%20connections%20guilds"

client = APIClient(TOKEN, client_secret=CLIENT_SECRET)

class dataManager:
    def __init__(self) -> None:
        self.db = sql.connect("./data/database.db")
        self.cur = self.db.cursor()
        self.autocommit = True

    def exec(self, code, values=()):
        try:
            x = self.cur.execute(str(code), values)
            if self.autocommit:
                self.db.commit()
            return x
        except Exception as ex:
            raise (ex)

    def convert_create_table(self, columns: list or tuple, types: list or tuple) -> str:
        n = ""
        if len(columns) == len(types):
            for i, x in enumerate(columns):
                if i == len(types) - 1:
                    n += f"{x} {types[i]}"
                else:
                    n += f"{x} {types[i]}, "
        return str(n)

    def convert_insert(self, values: list or tuple, column=False) -> str:
        n = ""
        for i, x in enumerate(values):
            v = x
            if type(x) == str and not column:
                v = f""""{str(x)}" """
            if i < len(values) - 1:
                v = f"{str(v)}, "
            n += str(v)
        return str(n)

    def convert_update(self, columns, values):
        n = ""
        if len(columns) == len(values):
            for i, x in enumerate(columns):
                v = x
                if type(values[i]) == str:
                    v = f'"{values[i]}"'
                if i == len(values) - 1:
                    n += f"{x} = {v}"
                else:
                    n += f"{x} = {v}, "
        return str(n)

    def create_table(self, table_name: str, columns: list or tuple, types: list or tuple):
        var = self.convert_create_table(columns, types)
        code = f"""
        CREATE TABLE IF NOT EXISTS {table_name} ({str(var)})
        """
        self.exec(code)

    def delete_table(self,table:str):
        code =  f"""
            DROP TABLE IF EXISTS {table}
        """
        self.exec(code)

    def insert(self, table: str, columns: list or tuple, values: list or tuple):
        code = f"""
        INSERT INTO {table} ({self.convert_insert(columns,True)})
        VALUES({self.convert_insert(values)})
        """
        self.exec(code)

    def get(self, table: str, id: int):
        code = f"""
        SELECT * FROM {table} WHERE id=?
        """
        values = (id,)
        return self.exec(code, values).fetchone()

    def gets(self, table: str, id: int, column: str):
        code = f"""
        SELECT {column} FROM {table} WHERE id=?
        """
        values = (id,)
        return self.cur.execute(code, values).fetchone()

    def getAll(self, table:str):
        code = f"""
        SELECT * FROM {table}
        """
        return self.cur.execute(code).fetchall()

    def delete(self,table:str, id:int):
        code = f"""
        DELETE FROM {table} WHERE id=?
        """
        values = (id,)
        self.exec(code, values)

    def is_registered(self, table: str, id: int, auto_insert=False, insert_value=()):
        def repeat():
            x = self.get(table, id)
            if not x and auto_insert:
                self.insert(table, insert_value[0], insert_value[1])
                x = repeat()
            return x

        x = repeat()
        return x

    def update(self, table: str, columns: list or tuple, values: list or tuple, id: int):
        code = f"""
        UPDATE {table} SET {self.convert_update(columns,values)} WHERE id=?
        """
        self.exec(code, (id,))


def ConvertOwnUserToDict(POwnUser):
    result = {}
    for attr in dir(POwnUser):
        if not callable(getattr(POwnUser, attr)) and not attr.startswith("__"):
            result[attr] = POwnUser.__getattribute__(attr)
    return result


class User:
    def __init__(self, code: str = "", id: int = 0) -> None:
        if code != "":
            self.access_token = client.oauth.get_access_token(
                code, REDIRECT_URL
            ).access_token
        else:
            self.access_token = None

        if id and id != 0:
            self.id = id
        else:
            self.id = None

        self.aboutme = ""
        self.highlight_color = "#000"
        self.links = {}
        self.admin = False

        self.start()  # Multiples Checks

    def getMeInDatabase(self):
        d = dataManager()
        # Get User in Database
        user = d.is_registered(
            "users",
            self.id,
            True,
            (DB_USERS_TABLE_COLUMNS, [self.id, str(self.__dict__)]),
        )
        return eval(user[1])

    def loadLocalDatabase(self):
        x = self.getMeInDatabase()
        self.highlight_color = x['highlight_color']
        self.aboutme = x['aboutme']
        self.links = x['links']

    def start(self):
        if self.access_token:
            bearer_client = APIClient(self.access_token, bearer=True)
            self.user = ConvertOwnUserToDict(bearer_client.users.get_current_user())

            self.authenticated = False
            self.id = self.user["id"]
            if int(self.id) in eval(environ['ADMINS_ID']):
                self.admin = True
            
            self.loadLocalDatabase()
            if not (self.access_token in ["", " ", None, "None"]):
                if self.access_token:
                    if bearer_client:
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
        else:
            if self.id:
                self.__dict__ = self.getMeInDatabase()

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

DB_POST_TABLE_COLUMNS = ["id", "data"]
DB_USERS_TABLE_COLUMNS = ["id", "data"]
DB_TAGS_TABLE_COLUMNS = ['id','name']
DB_DATETIME_STR = "%d/%m/%Y, %I:%M"

Database.create_table(
    "post",
    DB_POST_TABLE_COLUMNS,
    ["INTEGER PRIMARY KEY", "TEXT"],
)  # Create Table of posts
"""
DATABASE MANAGER
Columns:
- Id INTEGER PRIMARY KEY # Discord
- username TEXT # Discord
- Aboutme TEXT # Discord
"""
Database.create_table("users", DB_USERS_TABLE_COLUMNS, ["INTEGER PRIMARY KEY", "TEXT"])

"""
DATABASE MANAGER
Columns:
- Id INTEGER PRIMARY KEY
- Name TEXT
"""

Database.create_table('tags', DB_TAGS_TABLE_COLUMNS, ["INTEGER PRIMARY KEY", "TEXT"])

def PostFilterTags(tag:int):
    d = dataManager()
    tag = d.get('tags',tag)
    if tag:
        posts = d.getAll('post')
        cposts = []
        for post in posts:
            ptag = eval(post[1])['tags']
            if len(ptag) > 0:
                if tag[1] in ptag:
                    cposts.append(post)
        if len(cposts) > 0:
            return cposts
        else:
            return None # Sem posts
    else:
        return False # Sem tag