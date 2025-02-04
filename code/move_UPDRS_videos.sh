#!/usr/bin/env bash

# Define arrays for source and destination directories
src_directories=(
  "/media/dropbox_hdd/Starr Lab Dropbox/RC02LTE/Step7_UPDRS/"
  "/media/dropbox_hdd/Starr Lab Dropbox/RCS18/step7_UPDRS/"
  "/media/dropbox_hdd/Starr Lab Dropbox/RCS17/step7_UPDRS/"
  # Add more source directories here if needed
)

dst_directories=(
  "/media/dropbox_hdd/Starr Lab Dropbox/RC+S Patient Un-Synced Data/RCS02 Un-Synced Data/step7_UPDRS/"
  "/media/dropbox_hdd/Starr Lab Dropbox/RC+S Patient Un-Synced Data/RCS18 Un-Synced Data/step7_UPDRS/"
  "/media/dropbox_hdd/Starr Lab Dropbox/RC+S Patient Un-Synced Data/RCS17 Un-Synced Data/step7_UPDRS/"
  # Add corresponding destination directories here if needed
)

# Check if the number of source and destination directories match
if [ ${#src_directories[@]} -ne ${#dst_directories[@]} ]; then
  echo "Error: The number of source and destination directories must match."
  exit 1
fi

# Iterate through the source directories
for ((i=0; i<${#src_directories[@]}; i++)); do
  src="${src_directories[$i]}"
  dst="${dst_directories[$i]}"

  for src_file in "$src"*; do
    base_file=$(basename "$src_file")
    if [ -f "$src_file" ]; then
      if [ -e "$dst$base_file" ]; then
        base_no_ext="${base_file%.*}"
        ext="${base_file##*.}"
        mv "$src_file" "$dst$base_no_ext"_duplicate."$ext"
      else
        mv "$src_file" "$dst"
      fi
    fi
  done
done
