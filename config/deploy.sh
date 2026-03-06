#!/bin/bash
# Deploy Dispatches from Discharge Hell to Hostinger
#
# SETUP:
# 1. Copy this file and fill in your Hostinger credentials
# 2. chmod +x config/deploy.sh
# 3. Store credentials in environment variables, not in this file
#
# FIND YOUR CREDENTIALS:
# - Log into hpanel.hostinger.com
# - Go to Hosting -> Manage -> Advanced -> FTP Accounts
# - Use default account or create a new one

set -e

# Load credentials from environment
FTP_HOST="${DISPATCHES_FTP_HOST}"
FTP_USER="${DISPATCHES_FTP_USER}"
FTP_PASS="${DISPATCHES_FTP_PASS}"

if [ -z "$FTP_HOST" ] || [ -z "$FTP_USER" ] || [ -z "$FTP_PASS" ]; then
    echo "ERROR: Set environment variables DISPATCHES_FTP_HOST, DISPATCHES_FTP_USER, DISPATCHES_FTP_PASS"
    echo ""
    echo "Add to your ~/.bashrc or ~/.zshrc:"
    echo "  export DISPATCHES_FTP_HOST='your-ftp-host'"
    echo "  export DISPATCHES_FTP_USER='your-ftp-username'"
    echo "  export DISPATCHES_FTP_PASS='your-ftp-password'"
    exit 1
fi

echo "Deploying to DispatchesFromDischargeHell.com..."
echo "================================================"

lftp -u "$FTP_USER","$FTP_PASS" "$FTP_HOST" -e "
    set ssl:verify-certificate no;
    mirror --reverse --delete --verbose ./site/ /domains/dispatchesfromdischargehell.com/public_html/;
    quit
"

echo "================================================"
echo "DEPLOYED. Check https://dispatchesfromdischargehell.com"
echo "[$(date)] DEPLOYED via config/deploy.sh" >> logs/pipeline.log
