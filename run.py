import os
import sys
from datetime import datetime
from backend.src.utils.logger import laptop_logger

# https://claude.ai/chat/9d1230fb-bd45-4a98-9fd4-f5c2f77a4fec

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import uvicorn
from multiprocessing import Process

# Correct import path for the database service
from services.db_service.service.database_service import db_service_holder
from services.auth_service.service.authorization_service import auth_service_holder
from services.users_service.service.users_service import users_service_holder
from services.admin_service.service.admin_service import admin_service_holder



def run_database_service():
     uvicorn.run(
         "services.db_service.service.database_service:db_service_holder",
         host="0.0.0.0",
         port=8001,
         reload=True
     )


def run_auth_service():
    uvicorn.run(
        "services.auth_service.service.authorization_service:auth_service_holder",
        host="0.0.0.0",
        port=8002,
        reload=True
    )

def run_users_service():
    uvicorn.run(
        'services.users_service.service.users_service:users_service_holder',
        host='0.0.0.0',
        port=8003,
        reload=True
    )


def run_admin_service():
    uvicorn.run(
        "services.admin_service.service.admin_service:admin_service_holder",
        host="0.0.0.0",
        port=8004,
        reload=True
    )


def main():
    # List of services to run
    services = [
        {
            "name": "Database Service",
            "runner": run_database_service
        },
        {
            "name": "Auth Service",
            "runner": run_auth_service
        },
        {
            'name': 'Users Service',
            'runner': run_users_service
        },
        {
            "name": "Admin Service",
            "runner": run_admin_service
        },

        # Add more services here as you develop them
    ]

    # Create processes for each service
    processes = []
    try:
        for service in services:
            with open('app.log', 'a') as f:
                f.write("\n")

            laptop_logger.info(f"New launch at {datetime.now():%Y-%m-%d %H:%M:%S}")

            process = Process(target=service['runner'])
            process.start()
            processes.append(process)

        # Wait for all processes to complete
        for process in processes:
            process.join()

    except KeyboardInterrupt:
        print("\nShutting down services...")
        for process in processes:
            process.terminate()
            process.join()


if __name__ == "__main__":
    main()