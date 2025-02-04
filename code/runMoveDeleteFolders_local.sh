#!/usr/bin/env bash
database_dir="/home/starrlab/bin/code/rcs-database/code"

echo $$

# Runs script that searches for sessionType keywords in eventlog and caches sessions
cd $database_dir
# eval "$(conda shell.bash hook)"
#conda activate db_env
/home/starrlab/miniconda3/envs/db_env/bin/python3 ./cache_session_numbers.py
/home/starrlab/miniconda3/envs/db_env/bin/python3 ./add_sessiontypes_to_session.py
#conda deactivate

# Moves session data from synced to unsynced
cd /usr/local/MATLAB/R2022a/bin
./matlab -nodisplay -nodesktop -logfile "/media/dropbox_hdd/Starr Lab Dropbox/RC+S Patient Un-Synced Data/database/logs/logfile.log" -batch "run /home/starrlab/bin/code/rcs-database/code/move_and_delete_folders.m"
./matlab -nodisplay -nodesktop -logfile "/media/dropbox_hdd/Starr Lab Dropbox/RC+S Patient Un-Synced Data/database/logs/logfile.log" -batch "run /home/starrlab/bin/code/rcs-database/code/move_and_delete_folders.m"

sleep 15m

# # This line was used for databasing demo in lab meeting 04/19/22
# #mv "/media/dropbox_hdd/Starr Lab Dropbox/juan_testing/Clay_database_test/RCS13R/"* "/media/dropbox_hdd/Starr Lab Dropbox/RC+S Patient Un-Synced Data/RCS13 Un-Synced Data/SummitData/SummitContinuousBilateralStreaming/RCS13R/"

# Runs script that creates symlinks and csv entries
cd $database_dir
# conda activate db_env
/home/starrlab/miniconda3/envs/db_env/bin/python3 ./manage_proj_dirs_and_csvs.py
# conda deactivate

# Everything below is from Ro'ee's databasing. Deprecated since he left the lab in 07/2021

# print report log 
# cd /usr/local/MATLAB/R2022a/bin
# ./matlab -nodisplay -nodesktop -logfile "/media/dropbox_hdd/Starr Lab Dropbox/RC+S Patient Un-Synced Data/database/logs/database_log.log" -batch "run /home/starrlab/bin/code/rcs-database/code/create_database_from_device_settings_files.m"

# print reports from device settings 
# ./matlab -nodisplay -nodesktop -logfile "/media/dropbox_hdd/Starr Lab Dropbox/RC+S Patient Un-Synced Data/database/logs/report_log.log" -batch "run /home/starrlab/bin/code/rcs-database-main/code/print_report_from_device_settings_database_file_per_patient.m"

# convert files to .mat 
# ./matlab -nodisplay -nodesktop -logfile "//media/dropbox_hdd/Starr Lab Dropbox/RC+S Patient Un-Synced Data/database/logs/convert_to_mat_file_from_json.log" -batch "run /home/starrlab/bin/code/rcs-database-main/code/convert_all_files_from_mat_into_json.m"

# chop up data in 10 min chunk 
# ./matlab -nodisplay -nodesktop -logfile "/media/dropbox_hdd/Starr Lab Dropbox/RC+S Patient Un-Synced Data/database/logs/process_data_into_10_min_chunks.log" -batch "run /home/starrlab/bin/code/rcs-database-main/code/process_data_into_10_minute_chunks.m"

# create recording report figures  
#./matlab -nodisplay -nodesktop -logfile "/media/starrlab/storage1/Starr Lab Dropbox/RC+S Patient Un-Synced Data/database/logs/figure_reports.log" -batch "run /home/starrlab/bin/code/rcs-database-main/code/plot_database_figures.m"
 
 # Move Step 7 UPDRS videos to unsynced directory
  bash move_UPDRS_videos.sh
