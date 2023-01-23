import json
import pprint
import os
import glob
import pandas as pd
import manage_proj_dirs_and_csvs as mpdc
import sys

CACHED_SESSIONS_FILE_PATH = './database_jsons/cached_sessions.json'
DATABASE_BOOLEAN_PATH = './database_jsons/database_boolean.json'
PROJECT_SESSIONTYPES_PATH = './database_jsons/project_sessiontype_keywords.json'
UNSYNCED_BASE_PATH = '/media/dropbox_hdd/Starr Lab Dropbox/RC+S Patient Un-Synced Data/'
UNSYNCED_SUMMIT_NESTED_PATH = '/SummitData/SummitContinuousBilateralStreaming/'
PROJECTS_BASE_PATH = '/media/dropbox_hdd/Starr Lab Dropbox/Projects/'

"""This function takes a json of rcs devices + sessions and sessiontypes. It adds these sessions to the corresponding project-sessiontype directories and summary CSV."""

if  __name__ == "__main__":
    """ Terminal call of script expects sys.argv[1] as json filepath with form:
            {
                RCS#<L or R>: {
                    "Session#": ["sessiontype0", "sessiontype1", ...]
                    ...
                }
                ...
            }
        It will add that session to the projects (both in directory tree and summary csv) with corresponding sessiontypes. 
    """

    with open(sys.argv[1]) as g:
        device_session_dict = json.load(g)

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
    project_dfs = {key: pd.read_csv(value["csvPath"], index_col=0).reset_index(drop=True) for key, value in project_data.items() if os.path.isfile(value["csvPath"])}

    for rcs, session_sessiontypes_dict in device_session_dict.items():
        # Get complete file path to data in unsynced directory
        unsynced_rcs_filepath_complete =  f'{UNSYNCED_BASE_PATH}{rcs[:-1]} Un-Synced Data{UNSYNCED_SUMMIT_NESTED_PATH}{rcs}'

        # each 'session' is a Session# directory name (i.e. an individual SCBS recording session)
        for session, sessionTypes in session_sessiontypes_dict.items():
            session_filepath = os.path.join(unsynced_rcs_filepath_complete, session)

            if os.path.isdir(session_filepath):
                # Retrieves any sessionTypes, associated projects logged. Will be kept in cache if there was
                # sessionTypes identified but no associated project.
                devices = glob.glob(f"{session_filepath}/DeviceNPC*")

                # Checks if there are multiple devices in Session# directory (there should not be).
                # If not, creates path to jsons through only device.
                if len(devices) > 1:
                    print('%s has multiple Device subdirectories... skipping.', session)
                    continue
                else:
                    session_jsons_path = devices[0]

                if os.path.isfile(os.path.join(session_jsons_path, 'EventLog.json')):
                    try:
                        with open(os.path.join(session_jsons_path, 'EventLog.json')) as f:
                            session_eventLog = json.load(f)
                    except:
                        print('%s - %s has malformed EventLog.json... skipping.', rcs, session)
                        continue

                associated_projs = mpdc.get_associated_projects(sessionTypes=sessionTypes, project_sessionTypes=project_sessionTypes)

                mpdc.create_session_symlinks(rcs, session, session_filepath, sessionTypes, associated_projs, project_sessionTypes,
                                                project_basePaths)

                mpdc.add_row_to_project_df(rcs, project_dfs, session, session_eventLog, session_jsons_path,
                                        associated_projs, project_sessionTypes, sessionTypes)

            else:
                print(f"Directory does not exist: {session_filepath}")

    # Update Summary CSVs for each project
    for proj, df in project_dfs.items():
        path = project_csv_paths[proj]
        df.to_csv(path)