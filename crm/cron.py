import os
import requests
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    """
    Logs a heartbeat message to a file to confirm the CRM app is alive.
    Optionally queries the GraphQL hello field to verify the endpoint is responsive.
    """
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_message = f"{timestamp} CRM is alive"
    
    # Optional: Verify GraphQL endpoint
    try:
        response = requests.post('http://localhost:8000/graphql', json={'query': 'query { hello }'})
        if response.status_code == 200:
            log_message += " and GraphQL is responsive."
        else:
            log_message += " but GraphQL endpoint is not responsive."
    except requests.exceptions.RequestException as e:
        log_message += f" but failed to connect to GraphQL endpoint: {e}"

    log_path = '/tmp/crm_heartbeat_log.txt'
    with open(log_path, 'a') as f:
        f.write(log_message + '\n')
    
    print(log_message)

def update_low_stock():
    """
    Executes a GraphQL mutation to update low-stock products.
    """
    log_path = '/tmp/low_stock_updates_log.txt'
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Define the GraphQL mutation
    mutation = """
        mutation UpdateLowStockProducts {
            updateLowStockProducts {
                success
                message
                updatedProducts {
                    name
                    stock
                }
            }
        }
    """
    
    # Send the mutation request
    try:
        response = requests.post('http://localhost:8000/graphql', json={'query': mutation})
        data = response.json()
        
        # Log the result
        mutation_result = data.get('data', {}).get('updateLowStockProducts', {})
        
        if mutation_result.get('success'):
            message = mutation_result.get('message')
            updated_products = mutation_result.get('updatedProducts', [])
            
            with open(log_path, 'a') as f:
                f.write(f"{timestamp}: {message}\n")
                if updated_products:
                    for product in updated_products:
                        f.write(f"  - Updated: {product['name']}, New Stock: {product['stock']}\n")
                else:
                     f.write(f"  - No products updated.\n")

        else:
            error_message = f"Mutation failed: {data.get('errors', 'Unknown error')}"
            with open(log_path, 'a') as f:
                f.write(f"{timestamp}: {error_message}\n")
    except requests.exceptions.RequestException as e:
        error_message = f"Connection error: {e}"
        with open(log_path, 'a') as f:
            f.write(f"{timestamp}: {error_message}\n")

