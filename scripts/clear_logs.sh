#!/bin/bash

# Set the folder path, replace "/path/to/log/folder" with your folder path
LOG_FOLDER="./uav_logs"

# Check if the folder exists
if [ -d "$LOG_FOLDER" ]; then
  # Find all .log files and truncate them
  find "$LOG_FOLDER" -type f -name "*.log" -exec truncate -s 0 {} \;
  echo "All log files in $LOG_FOLDER have been cleared."
else
  echo "Folder $LOG_FOLDER does not exist."
fi
