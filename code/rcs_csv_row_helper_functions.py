import os
import json
import re
from datetime import datetime


def get_side(rcs):
    return "Left" if rcs[-1] == 'L' else "Right"


def get_start_time(session):
    return datetime.fromtimestamp(int(session[7:17])).strftime('%m-%d-%Y %H:%M:%S')


def get_end_time(session_jsons_path):
    deviceSettings_path = os.path.join(session_jsons_path, 'DeviceSettings.json')
    if os.path.isfile(deviceSettings_path):
        with open(deviceSettings_path) as f:
            try:
                deviceSettings = json.load(f)
                session_end_unix_time = deviceSettings[-1]['RecordInfo']['HostUnixTime']
            except Exception as error:
                print(f"Could not load: {session_jsons_path}/DeviceSettings.json because \n {error}")
                return 'WARNING: No JSON data found.'
        # Drop milliseconds from unix_time
        session_end_unix_time = round(session_end_unix_time/1000)
        return datetime.fromtimestamp(session_end_unix_time).strftime('%m-%d-%Y %H:%M:%S')
    else:
        return 'WARNING: No JSON data found.'


def get_notes(session_eventLog):
    sessionNotes = []
    for entry in session_eventLog:
        if entry['Event']['EventType'] == 'extra_comments' \
                and re.search('note.?:', entry['Event']['EventSubType'], re.IGNORECASE):
            entryNotes = entry['Event']['EventSubType']
            sessionNotes.extend([entryNotes])
    return ' '.join(sessionNotes) if sessionNotes else ''

def get_Dropbox_link(rcs, session_jsons_path):
    DROPBOX_HTML_PREFIX = f"https://www.dropbox.com/home/RC%2BS%20Patient%20Un-Synced%20Data/{rcs[:-1]}%20Un-Synced%20Data/"
    slice_ind = session_jsons_path.find("Summit")
    return DROPBOX_HTML_PREFIX + session_jsons_path[slice_ind:]

# TODO: Figure out good implementation for this... maybe need to use OpenMind, matlab code
def get_percent_disconnect(session_jsons_path):
    return None


def collect_csv_info(rcs, session, session_info_dict, session_eventLog, session_jsons_path):
    session_info_dict["RCS#"] = rcs[:5]
    session_info_dict["Side"] = get_side(rcs)
    session_info_dict["Session#"] = session
    session_info_dict["TimeStarted"] = get_start_time(session)
    session_info_dict["TimeEnded"] = get_end_time(session_jsons_path)
    session_info_dict["Notes"] = get_notes(session_eventLog)
    session_info_dict["Dropbox_Link"] = get_Dropbox_link(rcs, session_jsons_path)
    session_info_dict["Data_Server_Hyperlink"] = f'=HYPERLINK("{session_jsons_path}","jsons_link")'
    session_info_dict["Data_Server_FilePath"] = f"'{session_jsons_path}'"
    #session_info_series["%_Disconnected"] = get_percent_disconnect(session_jsons_path)
    # TODO: Figure out what metadata to collect
    return session_info_dict