#!/bin/bash

SRC_DIR="src"
MPREMOTE="mpremote"

# Find all files under src/ and upload each one
find "$SRC_DIR" -type f -name "*.py" | while read -r FILE; do
    # Strip leading src/ to get the remote path
    REMOTE_PATH="${FILE#$SRC_DIR/}"

    echo "Uploading $FILE → :$REMOTE_PATH"
    $MPREMOTE cp "$FILE" ":$REMOTE_PATH"
done

echo "Upload complete."

echo "Executing program."
mpremote exec "import smartchristmas"
echo "Execution terminated."

