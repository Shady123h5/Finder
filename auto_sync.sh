#!/bin/bash

# Configuration
BRANCH="main"
INTERVAL=60

echo "Starting auto-sync every $INTERVAL seconds..."

while true; do
    echo "--- Syncing at $(date) ---"
    
    # Pull changes from remote
    git pull origin $BRANCH --rebase
    
    # Add and commit local changes
    git add .
    # Only commit if there are changes
    if ! git diff-index --quiet HEAD --; then
        git commit -m "Auto-sync update: $(date)"
        
        # Push to remote
        if git push origin $BRANCH; then
            echo "Successfully synced to GitHub."
        else
            echo "Error: Push failed. Check your GitHub permissions."
        fi
    else
        echo "No changes to commit."
    fi
    
    echo "Waiting $INTERVAL seconds..."
    sleep $INTERVAL
done
