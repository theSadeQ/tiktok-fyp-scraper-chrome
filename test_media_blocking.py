"""Test that the scraper blocks all video/audio media requests."""
import json
from playwright.sync_api import sync_playwright

# Media patterns that should be blocked
BLOCK_PATTERNS = [
    "**/*.mp4",
    "**/*.m3u8",
    "**/*.ts",
    "**/*.m4a",
    "**/*.aac",
    "**/*video/play*",
]

blocked_requests = []
leaked_requests = []  # Media requests that were NOT blocked (should be empty)
total_bytes = 0


def block_media(route):
    blocked_requests.append(route.request.url)
    route.abort()


def monitor_response(response):
    """Flag any media response that slipped through the block."""
    url = response.url.lower()
    media_extensions = (".mp4", ".m3u8", ".ts", ".m4a", ".aac")
    media_keywords = ("video/play", "aweme/video", "tiktokcdn.com/video")
    if any(url.endswith(ext) for ext in media_extensions) or \
       any(kw in url for kw in media_keywords):
        leaked_requests.append(response.url)
        print(f"[LEAK DETECTED] {response.url}")


def run_test():
    global total_bytes

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        page = browser.new_page()

        # Apply media blocks
        for pattern in BLOCK_PATTERNS:
            page.route(pattern, block_media)

        # Monitor for leaked media responses
        page.on("response", monitor_response)

        # Track total bytes transferred
        page.on("response", lambda r: None)  # placeholder for byte tracking

        print("[*] Loading TikTok homepage (no login, public page)...")
        try:
            page.goto("https://www.tiktok.com/", wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(5000)
        except Exception as e:
            print(f"[!] Page load warning: {e}")

        browser.close()

    # Build report
    report = {
        "status": "PASS" if not leaked_requests else "FAIL",
        "blocked_count": len(blocked_requests),
        "leaked_count": len(leaked_requests),
        "leaked_urls": leaked_requests,
        "blocked_urls_sample": blocked_requests[:10],
    }

    with open("media_block_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\n========== MEDIA BLOCK TEST REPORT ==========")
    print(f"Status        : {report['status']}")
    print(f"Blocked       : {report['blocked_count']} media requests")
    print(f"Leaked        : {report['leaked_count']} media requests")
    if report["leaked_urls"]:
        print("Leaked URLs:")
        for url in report["leaked_urls"]:
            print(f"  - {url}")
    print("=============================================")

    # Fail the CI job if any media leaked through
    assert len(leaked_requests) == 0, (
        f"FAIL: {len(leaked_requests)} media request(s) were NOT blocked!\n"
        + "\n".join(leaked_requests)
    )
    print("[✓] All media requests were successfully blocked. No video data downloaded.")


if __name__ == "__main__":
    run_test()
