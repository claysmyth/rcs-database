from json.tool import main
import json
import os
import re
import fnmatch
import glob
import rcs_csv_row_helper_functions as csv_helper

CACHED_SESSIONS_FILE_PATH = './cached_sessions.json'
DATABASE_BOOLEAN_PATH = './database_boolean.json'
PROJECT_SESSIONTYPES_PATH = './project_sessiontype_keywords.json'
UNSYNCED_BASE_PATH = '/media/dropbox_hdd/Starr Lab Dropbox/RC+S Patient Un-Synced Data/'
UNSYNCED_SUMMIT_NESTED_PATH = '/SummitData/SummitContinuousBilateralStreaming/'

def get_projs_and_sessiontypes(session_filepath, project_sessiontypes):

    # Returns found sessiontypes
    def get_sessiontypes(session_eventLog):
        # Recursively search dictionary for sessiontype Events
        # Save all those in a list
        # Convert list to set
        sessiontypes = []
        for entry in session_eventLog:
            if entry['Event']['EventType'] == 'sessiontype':
                sessiontypes_tmp = list(filter(None, entry['EventSubType'].split(", ")))
                sessiontypes.extend(sessiontypes_tmp)
        
        return list(set(sessiontypes))

    # Searches if user is trying to add this sessiontype to a specific project
    def find_project_in_eventlog(session_eventLog, project_sessiontypes):
        associated_projs = []
        for entry in session_eventLog:
            if entry['Event']['EventType'] == 'extra_comments':
                projs_tmp = list(filter(None, re.split('[^a-zA-A]', entry["EvenSubType"])))
                associated_projs.extend([proj for proj in projs_tmp if proj in project_sessiontypes.keys()])
        return associated_projs

    # find all projects that have this sessiontype as a keyword
    def get_associated_projects(sessiontypes, project_sessiontypes):
        associated_projs = []
        for key, value in project_sessiontypes:
            associated_projs.extend(key) if set(value) & set(sessiontypes) else None
        return associated_projs
    
    # Probably not going to actually be called,
    # but need a method of keeping session# cached if there is no associated project and a sessiontype was found
    def keep_in_cache():
        return None
    
    devices = glob.glob(f"{session_filepath}/DeviceNPC*")

    if len(devices) > 1:
        # TODO: Handle situation
        return None, None
    else:
        device_filepath = devices[0]
    
    if os.path.isfile(os.path.join(device_filepath, 'EventLog.json')):
        with open(os.path.join(device_filepath, 'EventLog.json')) as f:
            session_eventLog = json.load(f)
        
        sessiontypes = get_sessiontypes(session_eventLog)
        associated_projs = []
        associated_projs.extend(find_project_in_eventlog(session_eventLog, project_sessiontypes))
        associated_projs.extend(get_associated_projects(sessiontypes, project_sessiontypes))

    if sessiontypes and not associated_projs:
        keep_cached = True
    else:
        keep_cached = False
        
    return sessiontypes, associated_projs, keep_cached

        

    #associated_projs should be a list of projects that this session is a part of. keep_in_cache is a boolean
    return associated_projs, keep_cached

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
        unsynced_rcs_filepath_complete = os.path.join(UNSYNCED_BASE_PATH, rcs[:-1], UNSYNCED_SUMMIT_NESTED_PATH)

        for session in session_list:
            session_filepath = unsynced_rcs_filepath_complete + '/' + session

            if os.path.isdir(session_filepath):
                sessiontypes, associated_projs, keep_cached = get_projs_and_sessiontypes(session_filepath, project_sessiontypes)
                # Probably need to fix the following line, as session will need RCS keyword, and to not have it as append
                sessions_to_keep_cached.append(session) if keep_cached else None
                create_session_symlinks(rcs, session_filepath, associated_projs, sessiontypes)
                add_row_to_project_csv(rcs, session_filepath, associated_projs, sessiontypes)

    update_cache(cache_data, sessions_to_keep_cached)










