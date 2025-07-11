#!/usr/bin/env python3
"""Test if the server can start and respond"""

import requests
import time
import subprocess
import sys


def test_server():
    # Start the server
    print("Starting server on port 9999...")
    server = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "main:app",
            "--port",
            "9999",
            "--host",
            "127.0.0.1",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Give it time to start
    time.sleep(5)

    # Check if process is still running
    if server.poll() is not None:
        stdout, stderr = server.communicate()
        print("Server crashed!")
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        return

    # Try to access the status endpoint
    try:
        print("Testing /api/v1/status endpoint...")
        response = requests.get("http://127.0.0.1:9999/api/v1/status", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error accessing endpoint: {e}")

    # Clean up
    server.terminate()
    server.wait()


if __name__ == "__main__":
    test_server()
