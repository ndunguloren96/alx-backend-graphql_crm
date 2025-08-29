import os
import requests
from datetime import datetime

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
