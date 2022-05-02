from json.tool import main
import json
import os
import fnmatch
import logging

PATIENT_DATA_PATHS_FILE = './database_jsons/patient_directory_names.json'
CACHE_FILE_PATH = './database_jsons/cached_sessions.json'
DATABASE_BOOLEAN_PATH = './database_jsons/database_boolean.json'
CACHE_LOG = './database_jsons/cache_log.log'

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
    logging.basicConfig(filename=CACHE_LOG, filemode='a', level=logging.INFO, 
                            format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    
    logging.info("Beginning Caching Run")

    # Get cache
    with open(CACHE_FILE_PATH) as g:
        cache_data = json.load(g)

    patient_dict = get_session_numbers()

    # Update cache with new session lists for each patient. Merges with existing list  (no duplicates), instead of replacing. 
    for device, sessions in patient_dict.items():
        if device in cache_data.keys():
            new_sessions = [session for session in sessions if session not in cache_data[device]]
            cache_data[device].extend(new_sessions)
            if new_sessions: logging.info("Caching session(s): %s - %s", device, new_sessions)
        else:
            cache_data[device] = sessions
            if sessions: logging.info("Caching session(s): %s - %s", device, sessions)

    # Write to jsons
    with open(CACHE_FILE_PATH, 'w') as out_cache:
        json.dump(cache_data, out_cache)

    logging.info("Completed Caching Run.\n")
    

