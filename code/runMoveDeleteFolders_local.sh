#!/usr/bin/env bash
database_dir=`pwd`
echo $$

eval "$(conda shell.bash hook)"
conda activate db_env
python3 ./cache_session_numbers.py
conda deactivate

cd /usr/local/MATLAB/R2021b/bin
./matlab -nodisplay -nodesktop -logfile "/media/dropbox_hdd/Starr Lab Dropbox/RC+S Patient Un-Synced Data/database/logs/logfile.log" -batch "run /home/starrlab/bin/code/rcs-database/code/move_and_delete_folders.m"
./matlab -nodisplay -nodesktop -logfile "/media/dropbox_hdd/Starr Lab Dropbox/RC+S Patient Un-Synced Data/database/logs/logfile.log" -batch "run /home/starrlab/bin/code/rcs-database/code/move_and_delete_folders.m"

cd $database_dir
conda activate db_env
python3 ./manage_proj_dirs_and_csvs.py
conda deactivate
# print report log 
# ./matlab -nodisplay -nodesktop -logfile "/media/dropbox_hdd/Starr Lab Dropbox/RC+S Patient Un-Synced Data/database/logs/database_log.log" -batch "run /home/starrlab/bin/code/rcs-database-main/code/create_database_from_device_settings_files.m"

# print reports from device settings 
# ./matlab -nodisplay -nodesktop -logfile "/media/dropbox_hdd/Starr Lab Dropbox/RC+S Patient Un-Synced Data/database/logs/report_log.log" -batch "run /home/starrlab/bin/code/rcs-database-main/code/print_report_from_device_settings_database_file_per_patient.m"

# convert files to .mat 
# ./matlab -nodisplay -nodesktop -logfile "//media/dropbox_hdd/Starr Lab Dropbox/RC+S Patient Un-Synced Data/database/logs/convert_to_mat_file_from_json.log" -batch "run /home/starrlab/bin/code/rcs-database-main/code/convert_all_files_from_mat_into_json.m"

# chop up data in 10 min chunk 
# ./matlab -nodisplay -nodesktop -logfile "/media/dropbox_hdd/Starr Lab Dropbox/RC+S Patient Un-Synced Data/database/logs/process_data_into_10_min_chunks.log" -batch "run /home/starrlab/bin/code/rcs-database-main/code/process_data_into_10_minute_chunks.m"

# create recording report figures  
#./matlab -nodisplay -nodesktop -logfile "/media/starrlab/storage1/Starr Lab Dropbox/RC+S Patient Un-Synced Data/database/logs/figure_reports.log" -batch "run /home/starrlab/bin/code/rcs-database-main/code/plot_database_figures.m"
