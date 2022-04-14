from json.tool import main
import json
import os
import fnmatch

PATIENT_DATA_PATHS_FILE = './database_jsons/patient_directory_names.json'
CACHE_FILE_PATH = './database_jsons/cached_sessions.json'
DATABASE_BOOLEAN_PATH = './database_jsons/database_boolean.json'

def get_session_numbers():
    patient_dict = {}
    # Open patient_direct json
    with open(PATIENT_DATA_PATHS_FILE) as f:
        patient_json = json.load(f)
    
    # Search through each entry in 'Patients', cache Sessions found in corresponding 'Synced' directory (i.e. the key value for each Patient's dictionary of filepaths)
    for key, val in patient_json["Devices"].items():
        tablet_synced_dir = val
        patient_sessions = []
        for filename in os.listdir(tablet_synced_dir):
            if fnmatch.fnmatch(filename, 'Session*'):
                patient_sessions.append(filename)
        if patient_sessions: patient_dict[key] = patient_sessions
    
    return patient_dict

if __name__ == "__main__":
    # Get boolean and cache data
    # with open(DATABASE_BOOLEAN_PATH) as db_bool:
    #     bool_data = json.load(db_bool)

    # Get cache
    with open(CACHE_FILE_PATH) as g:
        cache_data = json.load(g)


    # If data_boolean reads that databasing script is up to date with cache, then clear cache
    # [bool, delta] = list(bool_data.values())
    # if bool and not delta:
    #     cache_date = {}

    patient_dict = get_session_numbers()

    # Update cache with new session lists for each patient. Merges with existing list  (no duplicates), instead of replacing. 
    for key, sessions in patient_dict.items():
        if key in cache_data.keys():
            [cache_data[key].append(session) for session in sessions if session not in cache_data[key]]
        else:
            cache_data[key] = sessions

    
    # # Flag databasing as not updated
    # bool = False
    # # Increment delta
    # delta += 1
    # bool_data = dict(zip(bool_data.keys(), [bool, delta]))

    # Write to jsons
    with open(CACHE_FILE_PATH, 'w') as out_cache:
        json.dump(cache_data, out_cache)
    
    # with open(DATABASE_BOOLEAN_PATH, 'w') as out_bool:
    #     json.dump(bool_data, out_bool)

