This directory moves raw RC+S sessions (i.e. session directories containing json data) from directories synced with patient tablets, to a master directory not synced with any tablet. The primary script is runMoveDeleteFolders_local.sh. A cron job executes this script every morning at 2 am. Original matlab scripts were written by Ro'ee Gilron.

Clay Smyth added extended functionality (2021) to the script mover, by allowing for sessions to be added to 'Project' directories based on user (e.g. patient) inputted 'session-types' into the Report window of the SCBS application. If an identified 'session-type' matches a Project, then that RC+S session will be subsequently added to that Project directory tree and summary CSV. {Project: session-type} pairings are explicitly defined in './database_jsons/project_sessiontype_keywords.json'. A single session can be added to multiple projects by reporting multiple session-types in the Report window, as many-to-many mappings of projects to session-types are allowed. To allow for appropriate filepath generation for symlinks and csv entries, add new patients to 'patient_directory_names.json'. Relevant scripts include:  
  * add_sessions_to_project.py
  * manage_proj_dirs_and_csvs.py
  * cache_session_numbers.py
  * rcs_csv_row_helper_functions.py

To create a new project, create an appropriately named directory in '/dropbox_hdd/Starr Lab Dropbox/Projects/', and a new entry to './database_jsons/project_sessiontype_keywords.json'. The scripts will automatically search for session-types associated with the new project.

To add new session-types to an existing project, either:  
    1. Edit './database_jsons/project_sessiontype_keywords.json'
    2. In an SCBS session, add the comment "Add '<sessionType>' to '<project>'" in the 'comment' box of the Report window.

It is also possible to explicitly add a session to a Project without a session-type. Simply:
    1. In an SCBS session, enter "<Project Name>" into the 'comment' box of the Report window.

Script moving activity is logged into 'manage_proj_dirs_and_csvs_log.log'.

Lastly, it's possible to add user, or patient, notes/comments to an SCBS Session that will get recorded by the databasing script. These notes/comments will be recorded to the project summary CSV under the 'Notes' column. To add a 'Note' to an SCBS Session:

Type one of the following in the 'Comment' box of the Report window during as active SCBS session and hit enter (you can ignore the single quotes).
    * 'Note: <user comment>' 
    * 'Notes: <user comment>'
    * 'note: <user comment>'
    * 'notes: <user comment>'
