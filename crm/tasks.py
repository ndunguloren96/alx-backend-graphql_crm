import os
import django
from celery import shared_task
from datetime import datetime
import requests

# This is a temporary setup to avoid circular imports.
# In a real project, you would use a separate app for models.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from core import models as core_models

@shared_task
def generate_crm_report():
    """
    Generates a CRM report by querying the GraphQL endpoint.
    """
    log_path = '/tmp/crm_report_log.txt'
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # GraphQL query to get aggregate data
    query = """
    query CrmReport {
        allCustomers {
            totalCount
        }
        allOrders {
            totalCount
        }
        totalRevenue
    }
    """
    
    # We'll use a local GraphQL client or direct HTTP request
    try:
        response = requests.post('http://localhost:8000/graphql', json={'query': query})
        data = response.json()
        
        customers = data.get('data', {}).get('allCustomers', {}).get('totalCount', 0)
        orders = data.get('data', {}).get('allOrders', {}).get('totalCount', 0)
        revenue = data.get('data', {}).get('totalRevenue', 0)

        report_message = f"Report: {customers} customers, {orders} orders, {revenue} revenue"
        
        with open(log_path, 'a') as f:
            f.write(f"{timestamp} - {report_message}\n")
        
        print(f"Report generated: {report_message}")

    except requests.exceptions.RequestException as e:
        error_message = f"Connection error while generating report: {e}"
        with open(log_path, 'a') as f:
            f.write(f"{timestamp} - {error_message}\n")
        print(error_message)

