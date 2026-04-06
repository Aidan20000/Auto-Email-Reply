#!/usr/bin/bash

file="addresses.txt"
FLAGGED_ADDRESSES=""

# Check if file exists and is readable
if [[ ! -r "$file" ]]; then
    echo "Error: File '$file' not found or not readable."
    exit 1
fi

# Read file line by line
while IFS= read -r line || [[ -n "$line" ]]; do
    FLAGGED_ADDRESSES+="$line,"
done < "$file"

export FLAGGED_ADDRESSES


cd /home/rezt2460/code/auto-email-reply
/home/rezt2460/code/auto-email-reply/venv/bin/python main.py

unset FLAGGED_ADDRESSES