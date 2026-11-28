#!/usr/bin/env python3
"""
Agent de surveillance Kelyanti Hub.
Il envoie uniquement des mesures basiques vers Render en HTTPS.
Il n'ouvre aucun port et n'accepte aucune connexion entrante.
"""
import os
import time
import socket
import subprocess
import urllib.request
import json
import shutil

try:
    import psutil
except ImportError:
    raise SystemExit("Module psutil manquant. Installe-le avec : python3 -m pip install psutil")

HUB_URL = os.environ.get("HUB_URL", "").rstrip("/")
DELL_AGENT_TOKEN = os.environ.get("DELL_AGENT_TOKEN", "")
INTERVAL = 60
TMUX_SESSION = os.environ.get("MINECRAFT_TMUX_SESSION", "kelyanti-mc")
STARTED_AT = time.time()

def minecraft_running():
    # Contrôle uniquement l'existence de la session tmux du serveur.
    result = subprocess.run(
        ["tmux", "has-session", "-t", TMUX_SESSION],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5
    )
    return result.returncode == 0

def collect():
    vm = psutil.virtual_memory()
    uptime = int(time.time() - psutil.boot_time())
    return {
        "hostname": socket.gethostname(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": vm.percent,
        "memory_used_gb": round(vm.used / (1024 ** 3), 2),
        "memory_total_gb": round(vm.total / (1024 ** 3), 2),
        "uptime_seconds": uptime,
        "minecraft_running": minecraft_running()
    }

def send(payload):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        HUB_URL + "/api/dell/heartbeat",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Dell-Token": DELL_AGENT_TOKEN
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        return response.status

def main():
    if not HUB_URL.startswith("https://"):
        raise SystemExit("HUB_URL doit commencer par https://")
    if not DELL_AGENT_TOKEN:
        raise SystemExit("DELL_AGENT_TOKEN absent.")
    print("Agent Kelyanti Hub démarré. Ctrl+C pour arrêter.")
    while True:
        try:
            status = send(collect())
            print("Signal envoyé :", status)
        except Exception as exc:
            print("Envoi impossible :", type(exc).__name__)
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
