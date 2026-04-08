#!/bin/bash

# --- Configuration ---
SFTP_USER="fax_sender"
SFTP_PASS="password123"  # Replace with your actual password
SFTP_HOST="localhost"
SFTP_PORT="2022"
INBOUND_DIR="fax-inbound"

# --- Logic ---
FILE_PATH=$1

if [ -z "$FILE_PATH" ]; then
    echo "❌ Usage: ./fax.sh <path_to_file>"
    exit 1
fi

if [ ! -f "$FILE_PATH" ]; then
    echo "❌ Error: File not found at $FILE_PATH"
    exit 1
fi

echo "🚀 'Faxing' $FILE_PATH to $INBOUND_DIR..."

# Use a 'here-doc' to send commands to SFTP
export SSHPASS=$SFTP_PASS
sshpass -e sftp -P $SFTP_PORT -o StrictHostKeyChecking=no $SFTP_USER@$SFTP_HOST <<EOF
put "$FILE_PATH"
bye
EOF

if [ $? -eq 0 ]; then
    echo "✅ Fax successfully sent!"
else
    echo "❌ Fax failed. Check your SFTPGo connection."
fi
