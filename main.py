from camoufox.sync_api import Camoufox

from utils.cloudflare.waf import get_waf_cookie
from utils.disboard.scraper import Scraper


if __name__ == "__main__":
    resp = Scraper().scrape()
