import sys
import re
import time
import ctypes
import threading
from tls_client import Session
from ..config.config import load_config
from ..disboard.const import BASE_HEADERS
from ..cloudflare.waf import get_waf_cookie
from ..discordc.invite import get_invite_info
from pkg.logging import Logger
from utils.extra.extra import save_to_file
from datetime import datetime





class Scraper:
    def __init__(self):
        self.config = load_config()
        
        self.session = Session(client_identifier="firefox_120")
        self.headers = BASE_HEADERS.copy()
        self.ratelimited = False
        self.timestamp  = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.success = self.fail = self.err = 0 
        self.keyword = self.config['settings']['tag']
        self.max_pages  = self.config['settings']['max_pages']
        threading.Thread(target=self.SetTitle, daemon=True).start()
        response = get_waf_cookie()
        if response is None:
            self.err+=1
            Logger.log("ERR", "Failed to get WAF cookie")
            sys.exit(1)

        self.headers["Cookie"], self.headers["User-Agent"] = response

    def scrape(self):
        
        url = f"https://disboard.org/servers/tag/{self.keyword}"
        self.session.headers.update(self.headers)
        response = self.session.get(url).text
        try:
            self.csrf = re.search(
            r'<meta name="csrf-token" content="(.*?)"', response
        ).group(1)
        except AttributeError:
            self.err+=1
            Logger.log("ERR", "Failed to get CSRF token")
            sys.exit(1)
        for _ in range(1, self.max_pages + 1):
            url = f"https://disboard.org/servers/tag/{self.keyword}"
            self.session.headers.update(self.headers)
            response = self.session.get(url).text
            self.parse_servers(response)

    def parse_servers(self, response_text: str):
        matches = re.findall(r'<a href="(/server/join/\d+)"[^>]*>', response_text)
        for match in matches:
            while self.ratelimited:
                time.sleep(0.5)
            server_id = match.split("/")[-1]
            Logger.log("DBG", f"Found server ID: {server_id}")
            self.get_invite_code(server_id)

    def get_invite_code(self, server_id: str) -> str | None:
        try:
            headers = self.headers.copy()
            headers["Referer"] = f"https://disboard.org/server/join/{server_id}"
            headers["X-CSRF-Token"] = self.csrf

            response = self.session.post(
                f"https://disboard.org/site/get-invite/{server_id}", headers=headers
            )

            if response.status_code == 429:
                self.fail += 1
                Logger.log(
                    "WRN", f"Rate limited while fetching invite for server {server_id}"
                )
                Logger.log("DBG", f"Sleeping for 30seconds....")
                self.ratelimited = True
                time.sleep(30)
                self.ratelimited = False
                return None
            response = response.text

            invite_code = response.strip().replace('"', "").replace("'", "")
            invite_data = get_invite_info(invite_code)

            self.log_server_info(invite_data, server_id)

            return invite_code

        except Exception as e:
            self.err +=1
            Logger.log("ERR", f"Failed to fetch invite for server {server_id}: {e}")
            return None

    def log_server_info(self, invite_data: dict, fallback_id: str):
        guild = invite_data.get("guild", {})
        profile = invite_data.get("approximate_presence_count", {})
        channel = invite_data.get("channel", {})

        server_name = guild.get("name", "Unknown")
        server_id = guild.get("id", fallback_id)
        member_count = invite_data.get("approximate_member_count", "N/A")
        online_count = invite_data.get("approximate_presence_count", "N/A")
        code = invite_data.get("code", "N/A")
        vanity_url = guild.get("vanity_url_code", None)
        boost_tier = guild.get("premium_tier", "N/A")
        boost_count = guild.get("premium_subscription_count", "N/A")
        channel_name = channel.get("name", "N/A")
        description = guild.get("description", "")
        short_description = (
            (description[:100] + "...") if description else "No description"
        )
        self.success += 1
        Logger.log("INF", f"🛰️  {server_name} [{server_id}]")
        Logger.log("INF", f"├─ 👥 Members: {member_count} (Online: {online_count})")
        Logger.log("INF", f"├─ 🚀 Boosts: {boost_count} (Tier {boost_tier})")
        Logger.log("INF", f"├─ 🔗 Vanity: /{vanity_url or 'None'}")
        Logger.log("INF", f"├─ 📺 Channel: #{channel_name}")
        Logger.log("INF", f"├─ 🎫 Invite: https://discord.gg/{code}")
        Logger.log("INF", f"└─ 📝 Description: {short_description}")

        save_to_file(
            f"""🛰️  {server_name} [{server_id}]
👥 Members: {member_count} (Online: {online_count})
🚀 Boosts: {boost_count} (Tier {boost_tier})
🔗 Vanity: /{vanity_url or 'None'}
📺 Channel: #{channel_name}
🎫 Invite: https://discord.gg/{code}
📝 Description: {short_description}
""",
            self.keyword,
            self.timestamp,
        )
        
    def SetTitle(self):
        return
        while True:
            ctypes.windll.kernel32.SetConsoleTitleW(f"DISBOARD - {self.keyword} | Success: {self.success} | Fail: {self.fail} | Error: {self.err} | RateLimited: {self.ratelimited}")
        