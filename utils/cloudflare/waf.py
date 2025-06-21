from camoufox.sync_api import Camoufox
from pkg.logging import Logger

MULTIPLIER = 1000


def get_waf_cookie(domain: str = "https://disboard.org/") -> tuple[str, str] | None:
    cf_clearance_cookie = None
    user_agent = None

    try:
        with Camoufox(
            webgl_config=("Apple", "Apple M1, or similar"),
            disable_coop=True,
            locale=["en-US"],
            block_webrtc=False,
            block_webgl=False,
            humanize=True,
            geoip=True,
            os="macos",
            i_know_what_im_doing=True,
        ) as browser:
            page = browser.new_page()
            page.goto(domain, wait_until="networkidle", timeout=30 * MULTIPLIER)

            if page.title() == "Just a moment...":
                Logger.log("WRN", "(Detected) - Cloudflare - JS/Captcha")

                while True:
                    captcha_frame = next(
                        (
                            frame
                            for frame in page.frames
                            if "challenges.cloudflare.com" in frame.url
                        ),
                        None,
                    )

                    if captcha_frame:
                        Logger.log("DBG", f"Found Captcha Frame: {captcha_frame.url}")
                        captcha_frame.wait_for_load_state(
                            "networkidle", timeout=10 * MULTIPLIER
                        )
                        captcha_frame.wait_for_timeout(3 * MULTIPLIER)

                        try:
                            frame_element = captcha_frame.frame_element()
                            if not frame_element:
                                Logger.log("WRN", "Frame element not found.")
                                return None

                            box = frame_element.bounding_box()
                            if not box:
                                Logger.log("WRN", "Bounding box not found.")
                                return None

                            checkbox_x = box["x"] + box["width"] / 2
                            checkbox_y = box["y"] + box["height"] / 2

                            Logger.log(
                                "INF",
                                f"Clicking on captcha checkbox at ({checkbox_x}, {checkbox_y})",
                            )
                            page.mouse.click(checkbox_x, checkbox_y)

                            page.wait_for_load_state(
                                "networkidle", timeout=20 * MULTIPLIER
                            )

                            while page.title() == "Just a moment...":
                                Logger.log("INF", "Waiting for captcha to be solved...")
                                page.wait_for_timeout(5 * MULTIPLIER)

                            Logger.log("INF", "Captcha solved successfully.")

                            break

                        except Exception as e:
                            Logger.log("ERR", f"Error while handling captcha: {e}")
                            return None
                    else:
                        Logger.log("WRN", "Captcha frame not found.")
                        return None

            cookies = page.context.cookies()
            for cookie in cookies:
                if cookie["name"] == "cf_clearance":
                    cf_clearance_cookie = f"{cookie['name']}={cookie['value']}"
                    break

            user_agent = page.evaluate("() => navigator.userAgent")
            page.close()
            browser.close()

        if cf_clearance_cookie and user_agent:
            return cf_clearance_cookie, user_agent
        else:
            Logger.log("WRN", "cf_clearance or user-agent not found.")
            return None

    except Exception as e:
        Logger.log("ERR", f"An error occurred: {e}")
        return None
