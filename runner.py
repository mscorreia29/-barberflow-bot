import subprocess
import time
import os
import sys

print("[Init] Starting...", flush=True)
print(f"[Init] CWD: {os.getcwd()}", flush=True)
print(f"[Init] PORT: {os.environ.get('PORT', 'not set')}", flush=True)

try:
    api_log = open("/app/api.log", "w")
    print("[Init] Starting API...", flush=True)
    api_proc = subprocess.Popen(
        [sys.executable, "/app/api_server.py"],
        stdout=api_log,
        stderr=subprocess.STDOUT
    )
    print(f"[Init] API PID: {api_proc.pid}", flush=True)
except Exception as e:
    print(f"[Init] ERRO API: {e}", flush=True)

print("[Init] Waiting 5s...", flush=True)
time.sleep(5)

bridge_log = open("/app/bridge.log", "w")
print("[Init] Starting Bridge...", flush=True)
try:
    bridge_proc = subprocess.Popen(
        ["node", "index.js"],
        cwd="/app/whatsapp-bridge",
        stdout=bridge_log,
        stderr=subprocess.STDOUT
    )
    print(f"[Init] Bridge PID: {bridge_proc.pid}", flush=True)
except Exception as e:
    print(f"[Init] ERRO BRIDGE: {e}", flush=True)

print("[Init] Both started. Monitoring...", flush=True)

while True:
    time.sleep(10)
    if api_proc.poll() is not None:
        print(f"[Init] API died ({api_proc.returncode}). Restarting...", flush=True)
        api_log = open("/app/api.log", "a")
        api_proc = subprocess.Popen([sys.executable, "/app/api_server.py"], stdout=api_log, stderr=subprocess.STDOUT)
    if bridge_proc.poll() is not None:
        print(f"[Init] Bridge died ({bridge_proc.returncode}). Restarting...", flush=True)
        bridge_log = open("/app/bridge.log", "a")
        bridge_proc = subprocess.Popen(["node", "index.js"], cwd="/app/whatsapp-bridge", stdout=bridge_log, stderr=subprocess.STDOUT)
