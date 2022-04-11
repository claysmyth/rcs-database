import json
import os
import re
import glob
import pandas as pd
import rcs_csv_row_helper_functions as csv_helper

CACHED_SESSIONS_FILE_PATH = './cached_sessions.json'
DATABASE_BOOLEAN_PATH = './database_boolean.json'
# Should contain both filepath to project directory, csv filepath, and sessiontype keywords
PROJECT_SESSIONTYPES_PATH = './project_sessiontype_keywords.json'
UNSYNCED_BASE_PATH = '/media/dropbox_hdd/Starr Lab Dropbox/RC+S Patient Un-Synced Data/'
UNSYNCED_SUMMIT_NESTED_PATH = '/SummitData/SummitContinuousBilateralStreaming/'
PROJECTS_BASE_PATH = '/media/dropbox_hdd/Starr Lab Dropbox/Projects/'

# TODO: Create a separate parse_eventLog function??

def get_projs_and_sessionTypes(session_eventLog, project_sessionTypes):
    # Returns found sessionTypes
    global sessionTypes

    def get_sessionTypes(session_eventLog):
        # Identifies all sesstiontypes logged from the SessionType window in the SCBS Report screen
        sessionTypes_tmp = []
        for entry in session_eventLog:
            if entry['Event']['EventType'] == 'sessiontype':
                sessionTypes_single_entry = list(filter(None, entry['EventSubType'].split(", ")))
                sessionTypes_tmp.extend(sessionTypes_single_entry)

        return list(set(sessionTypes_tmp))

    # Searches user inputs if user is trying to add this session to a specific project, without related project -->
    # sessiontype keywords
    def find_project_in_eventlog(session_eventLog, project_sessionTypes):
        associated_projs_tmp = []
        for entry in session_eventLog:
            if entry['Event']['EventType'] == 'extra_comments':
                projs_tmp = list(filter(None, re.split('[^a-zA-A]', entry["EvenSubType"])))
                associated_projs_tmp.extend([proj for proj in projs_tmp if proj in project_sessionTypes.keys()])
        return associated_projs_tmp

    # find all projects that have this sessiontype as a keyword
    def get_associated_projects(sessionTypes, project_sessionTypes):
        associated_projs_tmp = []
        for key, value in project_sessionTypes.items():
            associated_projs_tmp.extend(key) if set(value) & set(sessionTypes) else None
        return associated_projs_tmp

    # sessionTypes is a list of all the sessiontype labels the experimentor associated with this recording session
    sessionTypes = get_sessionTypes(session_eventLog)
    # associated_projs is a list of all projects this Session# (i.e. recording session) should be a part of
    associated_projs = []
    associated_projs.extend(find_project_in_eventlog(session_eventLog, project_sessionTypes))
    associated_projs.extend(get_associated_projects(sessionTypes, project_sessionTypes))

    # Flag this Session# for staying cached if there are no projects associated with logged sessionTypes.
    if sessionTypes and not associated_projs:
        keep_cached = True
    else:
        keep_cached = False

    return sessionTypes, associated_projs, keep_cached


# Creates session symlink in associated project directory trees
def create_session_symlinks(rcs, session_name, session_filepath, sessionTypes, associated_projs, project_basePaths):
    # Check if session symlink already exists somewhere
    # If not, create symlink in each relevant project
    for proj in associated_projs:
        rcs_dir = os.path.join(project_basePaths[proj], rcs)
        if not os.path.isdir(rcs_dir):
            os.mkdir(rcs_dir)
        for sessiontype in sessionTypes:
            sessiontype_proj_dir = os.path.join(rcs_dir, sessiontype)
            if not os.path.isdir(sessiontype_proj_dir):
                os.mkdir(sessiontype_proj_dir)
            os.symlink(session_filepath, os.path.join(sessiontype_proj_dir, session_name))


# Adds a row for each session to the project summary csv, which is stored as pandas dataframe, with attributes that describe each corresponding session
# TODO: Figure out ordering of columns printed.
def add_row_to_project_df(rcs, project_dfs, session, session_eventLog, session_jsons_path, associated_projs,
                           project_sesstionTypes, sessionTypes):
    session_csv_info = csv_helper.collect_csv_info(rcs, session, {}, session_eventLog, session_jsons_path)
    for proj in associated_projs:
        relevent_sessionTypes = list(set(project_sesstionTypes[proj]) & set(sessionTypes))
        session_csv_info['SessionType(s)'] = ", ".join(relevent_sessionTypes)
        project_dfs[proj].loc[len(project_dfs[proj])] = session_csv_info
        




# If a session with a sessiontype was found without a corresponding project keyword, then is kept in cache.
# Otherwise, session#'s are deleted from cache
def update_cache(cache_data, sessions_to_keep_cached):
    for rcs, session_list in cache_data.items():
        cache_data[rcs] = list(set(session_list) - set(sessions_to_keep_cached))
    return cache_data


if __name__ == "__main__":
    # Get boolean, cached sessions, and sessiontype keywords json data
    with open(DATABASE_BOOLEAN_PATH) as db_bool:
        bool_data = json.load(db_bool)

    with open(CACHED_SESSIONS_FILE_PATH) as g:
        cache_data = json.load(g)

    with open(PROJECT_SESSIONTYPES_PATH) as p:
        project_data = json.load(p)

    # De-nest project_data into project_filepaths and proj_sessionTypes
    project_basePaths = dict(zip(project_data.keys(),
                                 [value["BasePath"] for value in project_data.values]))

    project_sessionTypes = dict(zip(project_data.keys(),
                                    [value["SessionTypes"] for value in project_data.values]))

    # Get each projects CSV filepath
    project_csv_paths = dict(zip(project_data.keys(),
                                 [value["csvPath"] for value in project_data.values]))

    # Get each projects CSV as a pandas DataFrame
    project_dfs = dict(zip(project_data.keys(),
                                 [pd.read_csv(value["csvPath"]) for value in project_data.values]))
    

    # Loop through each session for each RCS device
    sessions_to_keep_cached = []
    for rcs, session_list in cache_data:
        unsynced_rcs_filepath_complete = os.path.join(UNSYNCED_BASE_PATH, rcs[:-1], UNSYNCED_SUMMIT_NESTED_PATH)

        # each 'session' is a Session# directory name (i.e. an individual SCBS recording session)
        for session in session_list:
            session_filepath = os.path.join(unsynced_rcs_filepath_complete, session)

            # Checks if Session directory exists in relevant Unsynced directory
            if os.path.isdir(session_filepath):
                # Retrieves any sessionTypes, associated projects logged. Will be kept in cache if there was
                # sessionTypes identified but no associated project.
                devices = glob.glob(f"{session_filepath}/DeviceNPC*")

                # Checks if there are multiple devices in Session# directory (there should not be).
                # If not, goes with the creates path to jsons through only device.
                # TODO: Create error log?
                if len(devices) > 1:
                    # TODO: Handle situation, probably keep cached
                    continue
                else:
                    session_jsons_path = devices[0]

                if os.path.isfile(os.path.join(session_jsons_path, 'EventLog.json')):
                    with open(os.path.join(session_jsons_path, 'EventLog.json')) as f:
                        session_eventLog = json.load(f)

                sessionTypes, associated_projs, keep_cached = get_projs_and_sessionTypes(session_eventLog,
                                                                                         project_sessionTypes)

                # TODO: Fix keep_cached data structure to reflect rcs device
                sessions_to_keep_cached.append(session) if keep_cached else None

                # Creates symlinks in project directory tree for session based on identified sessionTypes
                if sessionTypes & associated_projs:
                    create_session_symlinks(rcs, session, session_filepath, sessionTypes, associated_projs,
                                            project_basePaths)

                # Session will be added to project CSV even if there is no session types logged
                if associated_projs:
                    add_row_to_project_df(rcs, project_dfs, session, session_eventLog, session_jsons_path,
                                       associated_projs, project_sessionTypes, sessionTypes)

    for proj, path in project_csv_paths.items():
        project_dfs[proj].to_csv(path)

    with open(CACHED_SESSIONS_FILE_PATH) as g:
        json.dump(update_cache(cache_data, sessions_to_keep_cached),g)
