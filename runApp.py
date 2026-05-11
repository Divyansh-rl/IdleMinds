import subprocess
import sys
import time
import os

os.environ["FLET_FORCE_WEB_SERVER"] = "true"

services = [
    "app.py",         
    "sudoku.py",    
    "pips.py",
    "zips.py",
    "wordcraft.py",
    "connections.py"     
]

processes = []

print("🚀 Booting up the Python Game Hub...")

try:
    for service in services:
        print(f"-> Starting {service}...")
        
        process = subprocess.Popen([sys.executable, service])
        processes.append(process)
        
        time.sleep(0.5) 

    print("\n✅ All servers are online!")
    print("🎮 Open your browser to: http://127.0.0.1:5000")
    print("🛑 Press 'Ctrl + C' here in the terminal to shut everything down.\n")

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n\nShutting down all game servers...")
    for p in processes:
        p.terminate()
    print("Shutdown complete. Goodbye!")
    sys.exit(0)