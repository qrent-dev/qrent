#!/bin/bash
# Docker entrypoint script to set up cron job for scraper

# Install cron
apt-get update && apt-get install -y cron

# Create log file
touch /app/scraper/scraper.log
chmod 0644 /app/scraper/scraper.log

# Create crontab file
echo "# Run scraper daily at 1 AM" > /etc/cron.d/scraper-cron
echo "0 1 * * * root cd /app/scraper && python property.py >> /app/scraper/scraper.log 2>&1" >> /etc/cron.d/scraper-cron
echo "" >> /etc/cron.d/scraper-cron

# Give execution rights to cron job
chmod 0644 /etc/cron.d/scraper-cron

# Apply cron job
crontab /etc/cron.d/scraper-cron

# Start cron
service cron start

echo "Cron job has been set up to run scraper daily at 1 AM"
echo "Running initial scraper execution..."

# Run scraper initially
cd /app/scraper && python property.py

# Keep container running
tail -f /app/scraper/scraper.log 