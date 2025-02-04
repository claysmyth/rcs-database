import json
import os
import glob
import copy
import warnings
import re

SESSIONS_TO_ADD_SESSIONTYPES_PATH = '/home/karenabalagula/add_sessiontypes_folder/'
PATIENT_DATA_PATHS_FILE = './database_jsons/patient_directory_names.json'
EVENT_TEMPLATE_PATH = './database_jsons/eventlog_template.json'

def add_sessiontype_de_novo(json_file_path, sessiontype):
    
    with open(EVENT_TEMPLATE_PATH, 'r') as file:
        data = json.load(file)
    
    # Need to get initial entry
    data = data[0]
    
    # Define a regular expression pattern to capture the session number and device string
    pattern = r"/Session(\d+)/Device([a-zA-Z0-9]+)/EventLog\.json"
    
    # Use regex to search for the pattern in the filepath
    match = re.search(pattern, json_file_path)
    
    if match:
        # Extract the session and device parts from the match
        session = f"Session{match.group(1)}"
        session_number = match.group(1)
        device = f"Device{match.group(2)}"
    
    data['Event']['EventType'] = 'sessiontype'
    data['Event']['EventSubType'] = ', '.join(sessiontype)
    data['Event']['UnixOffsetTime'] = int(session_number)
    data['Event']['UnixOnsetTime'] = int(session_number)
    data['RecordInfo']['HostUnixTime'] = int(session_number)
    data['RecordInfo']['DeviceId'] = device
    data['RecordInfo']['SessionId'] = session_number
    
    # Package back into list to keep with template form
    return [data]


def append_modified_entry(json_file_path, sessiontype):
    # Read the JSON data from the file
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
    except Exception as e:
        print(f"Error reading JSON file {json_file_path}: {e}")
    
    # Check if the data is a list of records
    if not isinstance(data, list):
        raise ValueError("JSON data must be a list of records")
    
    if len(sessiontype) == 1:
        # Need to add empty string to that the final inserted sessiontype matches
        # that of the RC+S log (e.g. "sessiontype, ")
        sessiontype.append("")

    if not data:
        warnings.warn(f"JSON data is empty: {json_file_path}")
        warnings.warn("Writing entirely new entry to Eventlog with desired session types.")
        data = add_sessiontype_de_novo(json_file_path, sessiontype)
    else:
        # Get the last entry
        last_entry = data[-1]
        
        # Create a duplicate of the last entry and modify it
        new_entry = copy.deepcopy(last_entry)
        if 'Event' in new_entry:
            new_entry['Event']['EventType'] = 'sessiontype'
            new_entry['Event']['EventSubType'] = ', '.join(sessiontype)
            new_entry['Event']['UnixOffsetTime'] = last_entry['Event']['UnixOffsetTime'] + 1
            new_entry['Event']['UnixOnsetTime'] = last_entry['Event']['UnixOnsetTime'] + 1
            new_entry['RecordInfo']['HostUnixTime'] = last_entry['RecordInfo']['HostUnixTime'] + 1
        else:
            raise KeyError("The last entry does not contain 'Event' key")
        
        # Append the modified entry to the data
        data.append(new_entry)
    
    # Write the updated JSON data back to the file
    with open(json_file_path, 'w') as file:
        json.dump(data, file, indent=4)


def find_device_subdirectory(base_path):
    """
    Find a subdirectory starting with 'Device' within the given base path.
    """
    for entry in os.listdir(base_path):
        full_path = os.path.join(base_path, entry)
        if os.path.isdir(full_path) and entry.startswith('Device'):
            return full_path
    return None


def process_patients(add_sessions_file):
    """
    Process JSON elements from a file and apply the append_modified_entry function.
    """
    
    # try:
    # Read the JSON data from the file
    with open(add_sessions_file, 'r') as file:
        json_data = json.load(file)
    
    with open(PATIENT_DATA_PATHS_FILE) as file2:
        patient_paths = json.load(file2)

    # Iterate through the elements of the JSON data
    for key, value in json_data.items():

        for item in value:
            # Unpack dictionary, as each item is a dictionary with Session key and value of another dict containing sessiontypes
            session, sessiontype_list = list(item.items())[0]
            sessiontype_list = sessiontype_list["sessiontypes"] # get the list from the dict entry

            full_event_log_path = os.path.join(
                                    find_device_subdirectory(os.path.join(patient_paths["Devices"][key], session)),
                                    'EventLog.json'
                                )
        
            # Call the append_modified_entry function with the key and value
            # Here we assume the key is used to determine the sessiontype
            append_modified_entry(full_event_log_path, sessiontype_list)
        
    # except (FileNotFoundError, json.JSONDecodeError) as e:
    #     print(f"Error reading JSON file {add_sessions_file}: {e}")
    # except Exception as e:
    #     print(f"An error occurred: {e}")


if __name__ == "__main__":

    # There should be only one json in the directory path
    add_session_json_path = glob.glob(os.path.join(SESSIONS_TO_ADD_SESSIONTYPES_PATH, '*.json'))

    if not add_session_json_path or not os.path.exists(add_session_json_path[0]):
        print(f"File {add_session_json_path} does not exist.")
    else:
        add_session_json_path = add_session_json_path[0]
        process_patients(add_session_json_path)
        if os.path.exists(add_session_json_path):
            if os.path.isfile(add_session_json_path):
                try:
                    os.remove(add_session_json_path)
                    print(f"File {add_session_json_path} has been deleted.")
                except Exception as e:
                    print(f"Error deleting file {add_session_json_path}: {e}")
