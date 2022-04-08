from json.tool import main
import json
import os
import fnmatch
import rcs_csv_row_helper_functions as csv_helper

CACHED_SESSIONS_FILE_PATH = './cached_sessions.json'
DATABASE_BOOLEAN_PATH = './database_boolean.json'
PROJECT_SESSIONTYPES_PATH = './project_sessiontype_keywords.json'
UNSYNCED_BASE_PATH = '/media/dropbox_hdd/Starr Lab Dropbox/RC+S Patient Un-Synced Data/'
UNSYNCED_SUMMIT_NESTED_PATH = '/SummitData/SummitContinuousBilateralStreaming/'

def find_sessiontype():

    # Searches if user is trying to add this sessiontype to a specific project
    def find_project_in_eventlog():
        return None

    # find all projects that have this sessiontype as a keyword
    def find_associated_projects():
        return None
    
    # Probably not going to actually be called,
    # but need a method of keeping session# cached if there is no associated project and a sessiontype was found
    def keep_in_cache():
        return None

    #associated_projs should be a list of projects that this session is a part of. keep_in_cache is a boolean
    return associated_projs, keep_in_cache

# Creates session symlink in associated project directory trees
def create_session_symlinks(rcs, session_filepath, associated_projs):
    # Check if session symlink already exists somewhere
    # If not, create symlink in each relevant project
    for proj in associated_projs:

    return None

#Adds a row for each session to the project summary csv with attributes that describe each corresponding session
def add_row_to_project_csv():
    return None

#If a session with a sessiontype was found without a corresponding project keyword, then is kept in cache. Otherwise, session#'s are deleted from cache
def update_cache():
    return None

if __name__ == "__main__":
    # Get boolean, cached sessions, and sessiontype keywords json data
    with open(DATABASE_BOOLEAN_PATH) as db_bool:
        bool_data = json.load(db_bool)

    with open(CACHED_SESSIONS_FILE_PATH) as g:
        cache_data = json.load(g)

    with open(PROJECT_SESSIONTYPES_PATH) as p:
        project_sessiontypes = json.load(p)

    sessions_to_keep_cached = []
    for rcs, session_list in cache_data:
        unsynced_rcs_filepath_complete = UNSYNCED_BASE_PATH + rcs[:-1] + UNSYNCED_SUMMIT_NESTED_PATH + rcs

        for session in session_list:
            session_filepath = unsynced_rcs_filepath_complete + '/' + session

            if os.path.isdir(session_filepath):
                associated_projs, keep_cached = find_sessiontype(session_filepath, project_sessiontypes)
                sessions_to_keep_cached.append(session) if keep_cached
                create_session_symlinks(rcs, session_filepath, associated_projs)
                add_row_to_project_csv(rcs, session_filepath, associated_projs)

    update_cache(cache_data, sessions_to_keep_cached)










