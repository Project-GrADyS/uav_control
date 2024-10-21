#!/bin/bash

# Variables
DIRECTORY=~/.config/gradys
FILE=protocol.txt

# Check if directory exists
if [ ! -d "$DIRECTORY" ]; then
  echo "Directory '$DIRECTORY' does not exist. Creating it."
  mkdir "$DIRECTORY"
else
  echo "Directory '$DIRECTORY' already exists."
fi

# Check if file exists in the directory
if [ ! -f "$DIRECTORY/$FILE" ]; then
  echo "File '$FILE' does not exist in '$DIRECTORY'. Creating it."
  touch "$DIRECTORY/$FILE"
else
  echo "File '$FILE' already exists in '$DIRECTORY'."
fi

if grep -q "^$1" "$DIRECTORY/$FILE"; then
  echo "Updating the line that starts with '$1'."
  # Replace the line with "<1> <2>"
  sed -i.bak "s/^$1.*/$1 $2/" "$DIRECTORY/$FILE"
else
  echo "Line starting with '$1' not found. Adding it."
  # Append the new line to the file
  echo "$1 $2" >> "$DIRECTORY/$FILE"
fi