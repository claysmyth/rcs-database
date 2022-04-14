import logging
import json
import pprint
import os
import re
import glob
import pandas as pd
import rcs_csv_row_helper_functions as csv_helper

CACHED_SESSIONS_FILE_PATH = './database_jsons/cached_sessions.json'
DATABASE_BOOLEAN_PATH = './database_jsons/database_boolean.json'
PROJECT_SESSIONTYPES_PATH = './database_jsons/project_sessiontype_keywords.json'
UNSYNCED_BASE_PATH = '/media/dropbox_hdd/Starr Lab Dropbox/RC+S Patient Un-Synced Data/'
UNSYNCED_SUMMIT_NESTED_PATH = '/SummitData/SummitContinuousBilateralStreaming/'
PROJECTS_BASE_PATH = '/media/dropbox_hdd/Starr Lab Dropbox/Projects/'

# TODO: Testing and Error handling.


def get_projs_and_sessionTypes(session_eventLog, project_sessionTypes):
    # Returns found sessionTypes
    global sessionTypes

    def get_sessionTypes(session_eventLog):
        # Identifies all sesstiontypes logged from the SessionType window in the SCBS Report screen
        sessionTypes_tmp = []
        for entry in session_eventLog:
            if entry['Event']['EventType'] == 'sessiontype':
                sessionTypes_single_entry = list(filter(None, entry['Event']['EventSubType'].split(", ")))
                sessionTypes_tmp.extend(sessionTypes_single_entry)

        return list(set(sessionTypes_tmp))

    # Searches user inputs if user is trying to add this session to any, or multiple, project, without related
    # project to sessiontype keywords
    def find_project_in_eventlog(session_eventLog, project_sessionTypes):
        associated_projs_tmp = []
        for entry in session_eventLog:
            if entry['Event']['EventType'] == 'extra_comments':
                projs_tmp = list(filter(None, re.split('[^a-zA-A]', entry['Event']["EventSubType"])))
                associated_projs_tmp.extend([proj for proj in projs_tmp if proj in project_sessionTypes.keys()])
        return associated_projs_tmp

    # find all projects that have this sessiontype as a keyword
    def get_associated_projects(sessionTypes, project_sessionTypes):
        associated_projs_tmp = []
        for key, value in project_sessionTypes.items():
            if set(value) & set(sessionTypes): associated_projs_tmp.extend([key])
        return associated_projs_tmp

    # sessionTypes is a list of all the sessiontype labels the experimentor associated with this recording session
    sessionTypes = get_sessionTypes(session_eventLog)
    # associated_projs is a list of all projects this Session# (i.e. recording session) should be a part of
    associated_projs = []
    # Users can explicitly add this session to project with extra_comment in SCBS Report Log. 
    # NOTE: If there are also sessionTypes found, then sessionType directories will be created in the project directory tree for this Device. 
        # However, this sessionType will not be added to the sessionType keyword list for this project.
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
            symlink = os.path.join(sessiontype_proj_dir, session_name)
            if not os.path.islink(symlink): os.symlink(session_filepath, symlink)


# Adds a row for each session to the project summary csv, which is stored as pandas dataframe, with attributes that describe each corresponding session
def add_row_to_project_df(rcs, project_dfs, session, session_eventLog, session_jsons_path, associated_projs,
                           project_sesstionTypes, sessionTypes):
    session_csv_info = csv_helper.collect_csv_info(rcs, session, {}, session_eventLog, session_jsons_path)
    SESSIONS_COLUMN = "Session#"
    COLUMN_ORDER = ['RCS#', 'Side', 'Session#', 'SessionType(s)', 'TimeStarted', 'TimeEnded', 'Notes', 'Data_FilePath', 'Data_Hyperlink']
    for proj in associated_projs:
        relevent_sessionTypes = list(set(project_sesstionTypes[proj]) & set(sessionTypes))
        session_csv_info['SessionType(s)'] = ", ".join(relevent_sessionTypes)
        if proj in project_dfs.keys():
            proj_df = project_dfs[proj]
            # Protects against duplicate entries
            if session not in proj_df[SESSIONS_COLUMN].values: 
                proj_df.loc[len(proj_df)] = session_csv_info
        else:
            project_dfs[proj] = pd.DataFrame(session_csv_info, index=[0]).reindex(columns=COLUMN_ORDER)
        

# If a session with a sessiontype was found without a corresponding project keyword, then is kept in cache.
# Otherwise, session#'s are deleted from cache
def update_cache(sessions_to_keep_cached):
    return {rcs: sessions_to_cache for rcs, sessions_to_cache in sessions_to_keep_cached.items() if sessions_to_cache}


if __name__ == "__main__":
    logging.basicConfig(filename="./database_jsons/manage_proj_dirs_and_csvs_log.log", filemode='a', level=logging.INFO, 
                            format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    
    logging.info("Beginning Manage Project Directories run")
    # Get boolean, cached sessions, and sessiontype keywords json data

    # with open(DATABASE_BOOLEAN_PATH) as db_bool:
    #     bool_data = json.load(db_bool)

    with open(CACHED_SESSIONS_FILE_PATH) as g:
        cache_data = json.load(g)

    with open(PROJECT_SESSIONTYPES_PATH) as p:
        project_data = json.load(p)

    # De-nest project_data into project_filepaths and proj_sessionTypes
    project_basePaths = dict(zip(project_data.keys(),
                                 [value["BasePath"] for value in project_data.values()]))

    project_sessionTypes = dict(zip(project_data.keys(),
                                    [value["SessionTypes"] for value in project_data.values()]))

    # Get each projects CSV filepath
    project_csv_paths = dict(zip(project_data.keys(),
                                 [value["csvPath"] for value in project_data.values()]))

    # Get each projects CSV as a pandas DataFrame
    project_dfs = {key: pd.read_csv(value["csvPath"], index_col=0) for key, value in project_data.items() if os.path.isfile(value["csvPath"])}
    

    # Loop through each session for each RCS device
    sessions_to_keep_cached = {}
    for rcs, session_list in cache_data.items():
        sessions_to_keep_cached[rcs] = []
        #unsynced_rcs_filepath_complete = os.path.join(UNSYNCED_BASE_PATH, f'{rcs[:-1]} Un-Synced Data', UNSYNCED_SUMMIT_NESTED_PATH, rcs)
        unsynced_rcs_filepath_complete =  f'{UNSYNCED_BASE_PATH}{rcs[:-1]} Un-Synced Data{UNSYNCED_SUMMIT_NESTED_PATH}{rcs}'

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
                if len(devices) > 1:
                    logging.warning('%s has multiple Device subdirectories. Will remain in cache.', session)
                    sessions_to_keep_cached[rcs].append(session)
                    continue
                else:
                    session_jsons_path = devices[0]

                if os.path.isfile(os.path.join(session_jsons_path, 'EventLog.json')):
                    with open(os.path.join(session_jsons_path, 'EventLog.json')) as f:
                        session_eventLog = json.load(f)

                sessionTypes, associated_projs, keep_cached = get_projs_and_sessionTypes(session_eventLog,
                                                                                         project_sessionTypes)
                

                # Add to sessions_to_keep_cached if this particular session was flagged for continued caching, 
                # which occurs when a sessionType was found, but no associated projects.
                if keep_cached:
                    sessions_to_keep_cached[rcs].append(session)
                    logging.info('%s has sessionType(s) with no related projects', session)

                # Creates symlinks in project directory tree for session based on identified sessionTypes.
                if sessionTypes and associated_projs:
                    create_session_symlinks(rcs, session, session_filepath, sessionTypes, associated_projs,
                                            project_basePaths)

                # TODO: Protect against duplicates
                # Note: Session will be added to project CSV even if there is no sessionTypes logged
                if associated_projs:
                    add_row_to_project_df(rcs, project_dfs, session, session_eventLog, session_jsons_path,
                                       associated_projs, project_sessionTypes, sessionTypes)
            
            else:
                # If there is not directory found for this session in RC+S Patient Unsynced Data, then session remains in cache
                sessions_to_keep_cached[rcs].append(session)
                logging.warning('%s does not have a directory in RC+S Patient Unsynced Data directory tree', session)

    for proj, df in project_dfs.items():
        path = project_csv_paths[proj]
        df.to_csv(path)

    with open(CACHED_SESSIONS_FILE_PATH, 'w') as g:
        json.dump(update_cache(sessions_to_keep_cached), g)
    
    logging.info("Completed Run.\n")