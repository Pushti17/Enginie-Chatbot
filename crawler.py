from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from urllib.parse import urljoin, urlparse
import time

# --- Configuration ---
BASE_URL = "https://ssgec.ac.in/"
DOMAIN = "ssgec.ac.in"
OUTPUT_FILE = "ssgec_all_urls.txt"

# --- Setup Chrome in Headless Mode ---
options = Options()
options.add_argument("--headless")  # run without GUI
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)
actions = ActionChains(driver)

visited = set()
to_visit = {BASE_URL}

def is_valid(url):
    """Check if URL belongs to same domain and is not a file link."""
    parsed = urlparse(url)
    if not (parsed.scheme and parsed.netloc and DOMAIN in parsed.netloc):
        return False

    # Skip non-HTML files
    blocked_ext = (
        ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".zip",
        ".doc", ".docx", ".xls", ".xlsx", ".mp4", ".mp3", ".ppt", ".pptx"
    )
    return not url.lower().endswith(blocked_ext)

def extract_links():
    """Extract all anchor hrefs from current page."""
    links = set()
    try:
        elements = driver.find_elements(By.TAG_NAME, "a")
        for el in elements:
            href = el.get_attribute("href")
            if href and is_valid(href):
                links.add(href.split('#')[0].rstrip('/'))
    except Exception:
        pass
    return links

def expand_menus():
    """Hover over or click menu items to reveal hidden dropdowns."""
    try:
        menu_items = driver.find_elements(By.CSS_SELECTOR, "nav a, .menu a, .navbar a")
        for item in menu_items:
            try:
                actions.move_to_element(item).perform()
                time.sleep(0.2)
            except Exception:
                pass
    except Exception:
        pass

print("Starting crawl...\n")

while to_visit:
    current_url = to_visit.pop()
    if current_url in visited or not is_valid(current_url):
        continue

    try:
        driver.get(current_url)
        time.sleep(1.5)  # wait for page + JS
        expand_menus()
        time.sleep(0.5)
        links = extract_links()
        new_links = [l for l in links if l not in visited and is_valid(l)]
        to_visit.update(new_links)
        visited.add(current_url)
        print(f"✅ Crawled: {current_url} | Found {len(new_links)} new links")
    except Exception as e:
        print(f" Skipped: {current_url} due to error ({e})")
        visited.add(current_url)
        continue

# --- Save results ---
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for u in sorted(visited):
        f.write(u + "\n")

print(f"\n Crawling complete!")
print(f"Total unique URLs found: {len(visited)}")
print(f"Saved in: {OUTPUT_FILE}")

driver.quit()
