import json
import csv
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

# Output CSV file
OUTPUT_FILE = "fyp_urls.csv"

# Media patterns to block (no video data downloaded)
BLOCK_PATTERNS = [
    "**/*.mp4",
    "**/*.m3u8",
    "**/*.ts",
    "**/*.m4a",
    "**/*.aac",
    "**/*video/play*",
    "**/*aweme/v1/aweme/video*",
]

collected_urls = []


def block_media(route):
    """Abort all media requests to prevent video downloads."""
    route.abort()


def handle_response(response):
    """Intercept FYP recommendation API responses and extract video URLs."""
    if "item_list" in response.url or "recommend/item_list" in response.url:
        try:
            data = response.json()
            items = data.get("itemList", data.get("item_list", []))
            for item in items:
                try:
                    video_id = item.get("aweme_id") or item.get("id", "")
                    author = item.get("author", {}).get("unique_id", "unknown")
                    desc = item.get("desc", "")
                    url = f"https://www.tiktok.com/@{author}/video/{video_id}"
                    if url not in [u["url"] for u in collected_urls]:
                        collected_urls.append({
                            "url": url,
                            "author": author,
                            "description": desc[:100],
                            "scraped_at": datetime.now().isoformat()
                        })
                        print(f"[+] {url}")
                except Exception:
                    pass
        except Exception:
            pass


def save_to_csv():
    if not collected_urls:
        print("No URLs collected.")
        return
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["url", "author", "description", "scraped_at"])
        writer.writeheader()
        writer.writerows(collected_urls)
    print(f"\n[✓] Saved {len(collected_urls)} URLs to {OUTPUT_FILE}")


def run_scraper(
    profile_dir="./chrome_profile",
    scroll_count=10,
    scroll_delay=2000,
    headless=False
):
    with sync_playwright() as p:
        print("[*] Launching custom Chromium browser...")
        context = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=headless,
            viewport={"width": 1280, "height": 900},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ]
        )

        page = context.new_page()

        # Block all media file requests
        for pattern in BLOCK_PATTERNS:
            page.route(pattern, block_media)

        # Intercept API responses
        page.on("response", handle_response)

        print("[*] Navigating to TikTok FYP...")
        page.goto("https://www.tiktok.com/foryou", wait_until="domcontentloaded", timeout=30000)

        print(f"[*] Scrolling {scroll_count} times to load FYP videos...")
        for i in range(scroll_count):
            page.keyboard.press("ArrowDown")
            page.wait_for_timeout(scroll_delay)
            print(f"  Scroll {i + 1}/{scroll_count} — {len(collected_urls)} URLs collected so far")

        context.close()

    save_to_csv()


if __name__ == "__main__":
    run_scraper(
        profile_dir="./chrome_profile",  # Persistent Chrome profile path
        scroll_count=20,                  # How many times to scroll FYP
        scroll_delay=2000,                # Delay between scrolls in ms
        headless=False                    # Set True to run without visible window
    )
