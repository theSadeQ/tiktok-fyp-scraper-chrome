# TikTok FYP Scraper — Custom Chrome

A lightweight tool to collect TikTok **For You Page (FYP) video URLs** without downloading any video data. Uses a persistent Chromium profile with Playwright, intercepting TikTok's recommendation API at the network level.

## How It Works

- Launches a custom Chromium browser with a **persistent profile** (keeps your TikTok login)
- **Blocks all media requests** (`.mp4`, `.m3u8`, `.ts`, `.m4a`) before they download
- Listens to TikTok's internal recommendation API (`item_list`) to extract video URLs
- Saves all collected URLs to `fyp_urls.csv`

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. First-Time Login

On your first run, the browser window will open. Log into TikTok manually. Your session will be saved to `./chrome_profile` for all future runs.

### 3. Run the Scraper

```bash
python scraper.py
```

Collected URLs are saved to `fyp_urls.csv` with columns: `url`, `author`, `description`, `scraped_at`.

## Configuration

Edit the bottom of `scraper.py` to adjust:

| Parameter | Default | Description |
|---|---|---|
| `profile_dir` | `./chrome_profile` | Path to persistent Chromium profile |
| `scroll_count` | `20` | Number of FYP scrolls (more = more URLs) |
| `scroll_delay` | `2000` | Milliseconds between scrolls |
| `headless` | `False` | Run without visible browser window |

## uBlock Origin Rules (Optional)

If you want extra protection when browsing TikTok manually, import `ublock_rules.txt` into uBlock Origin:

1. Open uBlock Origin → Dashboard → **My Filters**
2. Paste the contents of `ublock_rules.txt`
3. Click **Apply changes**

## Output

`fyp_urls.csv` example:

```
url,author,description,scraped_at
https://www.tiktok.com/@user123/video/7380000000000000000,user123,funny cat video,2026-05-12T17:00:00
```

## Notes

- Data usage per session: **~1–5 MB** (only JSON metadata, no video files)
- Works with your **personal FYP** since it uses your logged-in session
- Keep `./chrome_profile` directory to maintain your TikTok session between runs
