#!/bin/bash

# Script to create a tar archive with specified files and directories
# Usage: ./create-archive.sh [archive-name]

# Set default archive name if not provided
ARCHIVE_NAME=${1:-"ui-project-$(date +%Y%m%d-%H%M%S).tgz"}

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TMP_DIR="$PROJECT_ROOT/tmp"

echo "Creating archive: $ARCHIVE_NAME"
echo "Project root: $PROJECT_ROOT"
echo "Archive location: $TMP_DIR"

# Create tmp directory if it doesn't exist
mkdir -p "$TMP_DIR"

# Change to project root directory
cd "$PROJECT_ROOT"

# Create tar archive with specified files and directories
tar -czf "$TMP_DIR/$ARCHIVE_NAME" \
    scripts/ \
    build.ts \
    build-bundle.ts \
    jest.config.js \
    package-lock.json \
    package.json \
    playwright.config.ts \
    start-dev.sh \
    tsconfig.json \
    types/ \
    tests/

# Check if archive was created successfully
if [ $? -eq 0 ]; then
    echo "✅ Archive created successfully: $TMP_DIR/$ARCHIVE_NAME"
    echo "📦 Archive size: $(du -h "$TMP_DIR/$ARCHIVE_NAME" | cut -f1)"
else
    echo "❌ Failed to create archive"
    exit 1
fi 