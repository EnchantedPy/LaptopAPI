from src.core.auth_service.views import auth
import uvicorn
from src.utils.logger import logger

import os
import sys
from datetime import datetime

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import uvicorn
from multiprocessing import Process



def run_auth_service():
     uvicorn.run(
         "src.core.auth_service.views:auth",
         host="0.0.0.0",
         port=8000,
         reload=True
     )


def main():
    # List of services to run
    services = [
        {
            "name": "Auth Service",
            "runner": run_auth_service
        },
        # Add more services here as you develop them
    ]

    # Create processes for each service
    processes = []
    try:
        for service in services:
            with open('app.log', 'a') as f:
                f.write("\n")

            logger.info(f"New launch at {datetime.now():%Y-%m-%d %H:%M:%S}")

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