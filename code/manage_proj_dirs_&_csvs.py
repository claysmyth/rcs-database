from json.tool import main
import json
import os
import fnmatch

CACHE_FILE_PATH = './cached_sessions.json'
DATABASE_BOOLEAN_PATH = './database_boolean.json'
PROJECT_SESSIONTYPES_PATH = './project_sessiontype_keywords.json'

def find_sessiontype():

    # Searches if user is trying to add this sessiontype to a specific project
    def find_project_in_eventlog():
        return None

    # find all projects that have this sessiontype as a keyword
    def find_associated_projects():
        return None
    
    #Probably not going to actually be called, but need a method of keeping session# cached if there is no associated project
    def keep_in_cache():
        return None
    
    return None

#Creates session# symlink in project directory tree
def create_session_symlink():
    return None

#Adds a row for each session to the project summary csv with attributes that describe each corresponding session
def add_row_to_project_csv():
    return None

#If a session with a sessiontype was found without a corresponding project keyword, then is kept in cache. Otherwise, session#'s are deleted from cache
def update_cache():
    return None

if __name__ == "__main__":
    # Get boolean and cache data
    with open(DATABASE_BOOLEAN_PATH) as db_bool:
        bool_data = json.load(db_bool)

    with open(CACHE_FILE_PATH) as g:
        cache_data = json.load(g)

    with open(PROJECT_SESSIONTYPES_PATH) as p:
        project_sessiontypes = json.load(p)


