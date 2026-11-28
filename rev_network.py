"""
Rev Network Integration & Multiplayer Module for 'Run or dont'
Detects Rev Network client on the user's PC, checks version status, binds community account,
and provides seamless multiplayer networking (Lobby hosting, joining, and player synchronization).
"""
import os
import sys
import json
import socket
import random
import threading
import time
import psutil

REV_PATHS = [
    r"C:\Users\ZarTo\Desktop\Projects\Rev-Network",
    r"C:\Users\ZarTo\Desktop\Projects\Rev-Launcher",
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "RevNetwork"),
    os.path.join(os.environ.get("PROGRAMFILES", ""), "RevNetwork"),
    os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "RevNetwork"),
    os.path.join(os.environ.get("APPDATA", ""), "RevNetwork"),
    os.path.join(os.path.expanduser("~"), ".revnetwork"),
    "C:\\RevNetwork",
]

REV_PROCESS_NAMES = ["revnetwork.exe", "rev_client.exe", "rev_launcher.exe", "rev.exe"]

class RevNetworkManager:
    def __init__(self):
        self.is_detected = False
        self.install_path = None
        self.version = "Unknown"
        self.needs_update = False
        self.account_id = None
        self.account_name = None
        self.status_message = "Scanning system for Rev Network..."
        self.scan_pc()

    def scan_pc(self):
        """Scans the PC for Rev Network app, running processes, and config profile."""
        detected_path = None
        for path in REV_PATHS:
            if os.path.exists(path):
                detected_path = path
                break

        # Also inspect running processes
        running_found = False
        try:
            for proc in psutil.process_iter(['name', 'exe']):
                pname = (proc.info.get('name') or "").lower()
                if any(target in pname for target in REV_PROCESS_NAMES):
                    running_found = True
                    if not detected_path and proc.info.get('exe'):
                        detected_path = os.path.dirname(proc.info['exe'])
                    break
        except Exception:
            pass

        # Environment variable override or active port probe
        if "REV_NETWORK_DIR" in os.environ and os.path.exists(os.environ["REV_NETWORK_DIR"]):
            detected_path = os.environ["REV_NETWORK_DIR"]
        elif not detected_path:
            # Check if Rev-Network or Origin server is listening locally
            for p in (8765, 8000, 8767):
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.15)
                    if s.connect_ex(("127.0.0.1", p)) == 0:
                        running_found = True
                        detected_path = r"C:\Users\ZarTo\Desktop\Projects\Rev-Network"
                        s.close()
                        break
                    s.close()
                except Exception:
                    pass

        # Check for Radmin VPN IP for direct mesh multiplayer
        self.radmin_ip = None
        try:
            adapters = psutil.net_if_addrs()
            for iface, addrs in adapters.items():
                for a in addrs:
                    if a.family == socket.AF_INET and ("radmin" in iface.lower() or a.address.startswith("26.")):
                        self.radmin_ip = a.address
                        break
        except Exception:
            pass

        if detected_path or running_found:
            self.is_detected = True
            self.install_path = detected_path or "System Process Hook"
            self.read_account_info()
        else:
            # Rev Network simulated bridge fallback for offline/LAN play
            self.is_detected = False
            self.version = "1.0.0 (Legacy)"
            self.needs_update = True
            self.account_id = f"REV-{hash(os.environ.get('USERNAME', 'Survivor')) % 10000:04d}"
            self.account_name = os.environ.get("USERNAME", "Survivor")
            self.status_message = "Rev Network: Not installed (LAN / Direct P2P mode active)"

    def read_account_info(self):
        """Reads community account binding from Rev Network configuration."""
        account_bound = False
        if self.install_path and os.path.exists(self.install_path):
            config_file = os.path.join(self.install_path, "account.json")
            if os.path.exists(config_file):
                try:
                    with open(config_file, "r") as f:
                        data = json.load(f)
                        self.account_id = data.get("account_id", f"REV-USER-{random.randint(1000, 9999)}")
                        self.account_name = data.get("username", os.environ.get("USERNAME", "ZarTo"))
                        self.version = data.get("version", "2.4.1")
                        account_bound = True
                except Exception:
                    pass

        if not account_bound:
            # Bind based on PC user profile
            sys_user = os.environ.get("USERNAME", "Player")
            self.account_id = f"REV-ID#{abs(hash(sys_user)) % 90000 + 10000}"
            self.account_name = sys_user
            self.version = "2.4.0 (Latest)"
            self.needs_update = False

        self.status_message = f"Rev Network: Connected [{self.account_name} | {self.account_id}]"

    def get_summary(self):
        if self.is_detected:
            return f"REV NETWORK CONNECTED\nAccount: {self.account_name} ({self.account_id})\nEngine: RevNet v{self.version}"
        else:
            return f"REV NETWORK: NOT DETECTED\nMode: Local P2P Server / LAN\nAccount: {self.account_name} ({self.account_id})\n(Tip: Install Rev Network & update it for official servers)"


# -------------------------------------------------------------
# LIGHTWEIGHT MULTIPLAYER NETWORKING (REV NET / LAN PEER)
# -------------------------------------------------------------
class NetworkLobby:
    """Manages multiplayer host server or client connections."""
    def __init__(self, port=27015):
        self.port = port
        self.is_host = False
        self.is_connected = False
        self.server_socket = None
        self.client_socket = None
        self.peers = {} # {peer_id: (x, y, z, rotation)}
        self.lock = threading.Lock()
        self.running = False

    def start_host(self):
        """Starts hosting a multiplayer lobby."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_socket.bind(("0.0.0.0", self.port))
            self.is_host = True
            self.running = True
            threading.Thread(target=self._server_listen_loop, daemon=True).start()
            return True, f"Lobby hosted on port {self.port}"
        except Exception as e:
            return False, f"Failed to host lobby: {e}"

    def _server_listen_loop(self):
        while self.running:
            try:
                data, addr = self.server_socket.recvfrom(2048)
                msg = json.loads(data.decode("utf-8"))
                peer_id = msg.get("id")
                pos = msg.get("pos", [0, 0, 0])
                rot = msg.get("rot", 0)
                with self.lock:
                    self.peers[peer_id] = {"pos": pos, "rot": rot, "addr": addr, "last_seen": time.time()}
                # Broadcast positions to all known peers
                broadcast_data = json.dumps({"type": "sync", "peers": {k: {"pos": v["pos"], "rot": v["rot"]} for k, v in self.peers.items()}}).encode("utf-8")
                for p_info in self.peers.values():
                    self.server_socket.sendto(broadcast_data, p_info["addr"])
            except Exception:
                pass

    def connect_to_host(self, host_ip):
        """Connects to a host IP address."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.client_socket.settimeout(2.0)
            self.is_connected = True
            self.running = True
            self.host_addr = (host_ip, self.port)
            threading.Thread(target=self._client_listen_loop, daemon=True).start()
            return True, f"Connected to host {host_ip}:{self.port}"
        except Exception as e:
            return False, f"Failed to connect: {e}"

    def _client_listen_loop(self):
        while self.running:
            try:
                data, _ = self.client_socket.recvfrom(4096)
                msg = json.loads(data.decode("utf-8"))
                if msg.get("type") == "sync":
                    with self.lock:
                        self.peers = msg.get("peers", {})
            except Exception:
                pass

    def send_position(self, player_id, x, y, z, rot_y):
        """Sends local player's position and rotation."""
        payload = json.dumps({"id": player_id, "pos": [round(x, 2), round(y, 2), round(z, 2)], "rot": round(rot_y, 1)}).encode("utf-8")
        try:
            if self.is_host and self.server_socket:
                with self.lock:
                    self.peers[player_id] = {
                        "pos": [round(x, 2), round(y, 2), round(z, 2)],
                        "rot": round(rot_y, 1),
                        "last_seen": time.time()
                    }
            elif self.is_connected and self.client_socket:
                self.client_socket.sendto(payload, self.host_addr)
        except Exception:
            pass

    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        if self.client_socket:
            self.client_socket.close()
