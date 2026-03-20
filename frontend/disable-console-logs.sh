#!/bin/bash
# Temporary script to disable console.log in production

echo "Commenting out console.log statements in API files..."

# Find and comment out console.log lines in src/api directory
find src/api -name "*.ts" -type f -exec sed -i 's/^    console\.log/    \/\/ console.log/g' {} +

echo "✅ Console logs disabled in API files"
echo "To re-enable, run: git checkout src/api/"
