import os
import django
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.http import HTTPTransport

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

# GraphQL endpoint URL
GRAPHQL_URL = 'http://localhost:8000/graphql'

# GraphQL query to get recent orders
QUERY = gql("""
    query GetRecentOrders {
        allOrders {
            edges {
                node {
                    id
                    orderDate
                    customer {
                        email
                    }
                }
            }
        }
    }
""")

def send_order_reminders():
    """
    Queries for recent orders and logs reminders.
    """
    log_file_path = '/tmp/order_reminders_log.txt'
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Use a try-except block to handle potential connection errors
    try:
        transport = HTTPTransport(url=GRAPHQL_URL)
        client = Client(transport=transport, fetch_schema_from_transport=True)
        result = client.execute(QUERY)
        
        orders = result.get('allOrders', {}).get('edges', [])
        
        # Filter orders from the last 7 days
        seven_days_ago = datetime.now().astimezone() - timedelta(days=7)
        recent_orders = [
            order['node'] for order in orders
            if datetime.fromisoformat(order['node']['orderDate']).astimezone() > seven_days_ago
        ]

        if not recent_orders:
            message = f"{timestamp}: No new order reminders to send."
            print(message)
            with open(log_file_path, "a") as log_file:
                log_file.write(message + '\n')
            return

        with open(log_file_path, "a") as log_file:
            log_file.write(f"{timestamp}: Processing order reminders...\n")
            for order in recent_orders:
                order_id = order['id']
                customer_email = order['customer']['email']
                log_entry = f"Order ID: {order_id}, Customer Email: {customer_email}"
                log_file.write(log_entry + '\n')
                print(log_entry)

        print("Order reminders processed!")

    except Exception as e:
        error_message = f"{timestamp}: An error occurred while processing order reminders: {e}"
        print(error_message)
        with open(log_file_path, "a") as log_file:
            log_file.write(error_message + '\n')

if __name__ == '__main__':
    send_order_reminders()
