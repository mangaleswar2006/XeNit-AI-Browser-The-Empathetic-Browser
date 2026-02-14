import os
import urllib.request
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo

class BlocklistLoader(QThread):
    loaded = pyqtSignal(set)
    
    def run(self):
        hosts = set()
        blocklist_path = "adblock_list.txt"
        
        # We use StevenBlack's Unified Hosts List (combines AdAway, MVP, etc.)
        # It's the gold standard for system-wide adblocking.
        blocklist_url = "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts"
        
        # Try local first
        if os.path.exists(blocklist_path):
            try:
                with open(blocklist_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Handle "0.0.0.0 domain.com" or just "domain.com"
                            parts = line.split()
                            if len(parts) >= 2 and (parts[0] == "0.0.0.0" or parts[0] == "127.0.0.1"):
                                hosts.add(parts[1])
                            elif len(parts) == 1:
                                hosts.add(parts[0])
            except Exception as e:
                print(f"Error reading local blocklist: {e}")
        
        # If empty or missing, download
        if not hosts:
            try:
                print("Downloading massive unified adblock list (StevenBlack)...")
                
                # Set a proper User-Agent to avoid 403 Forbidden from GitHub
                req = urllib.request.Request(
                    blocklist_url, 
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                
                with urllib.request.urlopen(req) as response:
                    data = response.read().decode('utf-8')
                    # Save for offline use
                    with open(blocklist_path, 'w', encoding='utf-8') as f:
                        f.write(data)
                    
                    for line in data.splitlines():
                        line = line.strip()
                        if line and not line.startswith('#'):
                            parts = line.split()
                            # Hosts format: 0.0.0.0 ad.doubleclick.net
                            if len(parts) >= 2 and (parts[0] == "0.0.0.0" or parts[0] == "127.0.0.1"):
                                hosts.add(parts[1])
                            # Raw domain list support just in case
                            elif len(parts) == 1:
                                hosts.add(parts[0])
                                
                print(f"Downloaded {len(hosts)} rules. Total Shield Active.")
            except Exception as e:
                print(f"Error downloading blocklist: {e}")
                
        self.loaded.emit(hosts)

class AdBlockInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Start with essential hardcoded blocks for immediate protection
        self.blocked_hosts = {
            "doubleclick.net", "adservice.google.com", "googlesyndication.com", "google-analytics.com",
            "adserver.com", "adnxs.com", "pagead2.googlesyndication.com",
            "facebook.com/tr", "connect.facebook.net", "platform.twitter.com",
            # ... keep some key ones for startup speed ...
             "youtube.com/ads", "popads.net"
        }
        
        # Start async loader
        self.loader = BlocklistLoader()
        self.loader.loaded.connect(self.update_blocklist)
        self.loader.start()

    def update_blocklist(self, new_hosts):
        self.blocked_hosts.update(new_hosts)
        print(f"AdBlock Logic Fully Armed: {len(self.blocked_hosts)} domains blocked.")

    def interceptRequest(self, info: QWebEngineUrlRequestInfo):
        url_str = info.requestUrl().toString().lower()
        host = info.requestUrl().host().lower()
        
        # 1. Host-based Blocking (Fast)
        if host in self.blocked_hosts:
            info.block(True)
            return

        # 2. Strict YouTube Ad Blocking (Path/Query based)
        # YouTube loads ads from the same domain or google domains, often identified by path.
        if "youtube.com" in host or "googlevideo.com" in host:
            # Block ad-specific API endpoints
            if "/pagead/" in url_str or \
               "/ptracking" in url_str or \
               "/api/stats/ads" in url_str or \
               "&ad_format=" in url_str or \
               "&ad_type=" in url_str:
                info.block(True)
                print(f"XeNit AdBlock: Blocked YouTube Ad Request -> {url_str[:50]}...")
                return

        # 3. Keyword / Pattern Blocking for other sites
        critical_keywords = ["doubleclick", "adservice", "googlesyndication", "pixel", "tracker", "analytics"]
        for kw in critical_keywords:
            if kw in host:
                info.block(True)
                return
                
        # 4. Universal Ad-Query Blocker (Aggressive)
        # Blocks any request with explicit ad params
        if "google_ads" in url_str or "doubleclick.net" in url_str:
             info.block(True)
             return


