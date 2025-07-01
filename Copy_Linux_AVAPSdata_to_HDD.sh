#!/bin/bash

# Get the absolute path to this script and extract the drive it's on
SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
DEST_DRIVE="$(df --output=target "$SCRIPT_DIR" | tail -1)"

# Source and destination
SRC="/home/export/AVAPSdata"
DST="$DEST_DRIVE/AVAPSdata"

# Print info
echo "Script is running from: $SCRIPT_PATH"
echo "Destination drive mount point: $DEST_DRIVE"
echo "Copying from: $SRC"
echo "Copying to:   $DST"
echo

# Do the copy with rsync
rsync -avh --progress --update "$SRC/" "$DST/"

echo
echo "AVAPS data copy complete."
