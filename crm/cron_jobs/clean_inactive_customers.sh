#!/bin/bash

# Define the project root directory
PROJECT_ROOT="/alx-backend-graphql_crm"

# Ensure script is run from the correct directory
cd "$PROJECT_ROOT" || { echo "Failed to change directory to $PROJECT_ROOT" >> /tmp/customer_cleanup_log.txt; exit 1; }

# Activate virtual environment if necessary (for systems where it's not global)
source venv/bin/activate

# Define log file
LOG_FILE="/tmp/customer_cleanup_log.txt"

# Get current timestamp
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Django command to delete inactive customers
DELETED_COUNT=$(python3 manage.py shell -c "
from core.models import Customer
from datetime import datetime, timedelta
from django.db.models import Count
one_year_ago = datetime.now() - timedelta(days=365)
inactive_customers = Customer.objects.annotate(
    order_count=Count('orders')
).filter(order_count=0, created_at__lt=one_year_ago)
count, _ = inactive_customers.delete()
print(count)
")

# Log the result with a timestamp
echo "$TIMESTAMP: Deleted $DELETED_COUNT customers with no orders in the last year." >> "$LOG_FILE"

# Deactivate virtual environment
deactivate
