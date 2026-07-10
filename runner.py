import subprocess
import time
import os
import sys

print("[Init] Starting BarberFlow Bot...", flush=True)

api_proc = subprocess.Popen(
    [sys.executable, "/app/api_server.py"],
    stdout=open("/app/api.log", "w"),
    stderr=subprocess.STDOUT
)
print(f"[Init] API started (PID={api_proc.pid})", flush=True)

print("[Init] Waiting 5s for API...", flush=True)
time.sleep(5)

bridge_dir = "/app/whatsapp-bridge"
bridge_log = open("/app/bridge.log", "w")

print(f"[Init] Starting WhatsApp Bridge in {bridge_dir}...", flush=True)
bridge_proc = subprocess.Popen(
    ["node", "index.js"],
    cwd=bridge_dir,
    stdout=bridge_log,
    stderr=subprocess.STDOUT
)
print(f"[Init] Bridge started (PID={bridge_proc.pid})", flush=True)

try:
    while True:
        if bridge_proc.poll() is not None:
            print(f"[Init] Bridge exited with code {bridge_proc.returncode}", flush=True)
            bridge_log.close()
            bridge_log = open("/app/bridge.log", "a")
            bridge_log.write(f"\n[Init] Bridge exited with code {bridge_proc.returncode}\n")
            bridge_log.flush()
            bridge_log.close()
            print("[Init] Restarting bridge in 5s...", flush=True)
            time.sleep(5)
            bridge_log = open("/app/bridge.log", "a")
            bridge_proc = subprocess.Popen(
                ["node", "index.js"],
                cwd=bridge_dir,
                stdout=bridge_log,
                stderr=subprocess.STDOUT
            )
            print(f"[Init] Bridge restarted (PID={bridge_proc.pid})", flush=True)
        
        api_ret = api_proc.poll()
        if api_ret is not None:
            print(f"[Init] API exited with code {api_ret}. Restarting...", flush=True)
            api_proc = subprocess.Popen(
                [sys.executable, "/app/api_server.py"],
                stdout=open("/app/api.log", "w"),
                stderr=subprocess.STDOUT
            )
        
        time.sleep(2)
except KeyboardInterrupt:
    print("[Init] Shutting down...", flush=True)
    bridge_proc.terminate()
    api_proc.terminate()
