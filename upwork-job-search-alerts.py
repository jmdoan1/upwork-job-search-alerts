import time
import os
import random
import pickle
import re
import json
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dotenv import load_dotenv

# Try to use lxml parser, fall back to html.parser if lxml is not available
def get_bs4_parser():
    try:
        import lxml
        return 'lxml'
    except ImportError:
        print("lxml parser not found, falling back to html.parser")
        return 'html.parser'

BS4_PARSER = get_bs4_parser()

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ---------------------------
# Configuration / Flags
# ---------------------------

load_dotenv() 

SAVE_SEARCH_HTML = False
SAVE_POST_HTML = False
SAVE_TELEGRAM_MESSAGE = False
CHECK_INTERVAL = 3  # Time between checks in minutes
MAX_DESCRIPTION_LENGTH = 300
JOB_HISTORY_FILE = "job_history.pkl"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

search_urls_json = os.environ.get("SEARCH_URLS", "[]")
SEARCH_URLS = json.loads(search_urls_json)

USE_PROXY = True
proxy_list_json = os.environ.get("PROXY_LIST", "[]")
PROXY_LIST = json.loads(proxy_list_json)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
]

BASE_URL = "https://www.upwork.com"

# ---------------------------
# Helper Functions
# ---------------------------

def setup_directories():
    for directory in ["debug", "debug/search_html", "debug/job_html", "debug/telegram_messages"]:
        if not os.path.exists(directory):
            os.makedirs(directory)


def get_proxy():
    if not USE_PROXY or not PROXY_LIST:
        return None
    return random.choice(PROXY_LIST)


def get_user_agent():
    return random.choice(USER_AGENTS)


def load_job_history():
    if os.path.exists(JOB_HISTORY_FILE):
        try:
            with open(JOB_HISTORY_FILE, 'rb') as f:
                return pickle.load(f)
        except (pickle.PickleError, EOFError):
            print(f"Error loading job history, starting fresh")
    return set()


def save_job_history(job_history):
    with open(JOB_HISTORY_FILE, 'wb') as f:
        pickle.dump(job_history, f)


def clean_html_for_saving(html_content):
    soup = BeautifulSoup(html_content, BS4_PARSER)
    
    for script in soup.find_all('script'):
        if script.get('src') and any(term in script['src'] for term in ['css', 'style']):
            continue
        script.decompose()
    
    return str(soup)


def save_html(html_content, prefix, identifier):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"./debug/{prefix}/{timestamp}_{identifier}.html"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(clean_html_for_saving(html_content))
    
    print(f"Saved HTML to {filename}")


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print(f"Failed to send Telegram message: {response.text}")
        else:
            print("Telegram message sent successfully")
            
        if SAVE_TELEGRAM_MESSAGE:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"./debug/telegram_messages/{timestamp}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(message)
            print(f"Saved Telegram message to {filename}")
            
    except Exception as e:
        print(f"Error sending Telegram message: {e}")


def get_html(url, wait_selector=None):
    print(f"Fetching HTML for {url}")

    options = Options()
    options.add_argument(f"user-agent={get_user_agent()}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--headless")

    proxy = get_proxy()
    if proxy and proxy.startswith("socks"):
        try:
            proxy_parts = proxy.replace("socks5://", "").split("@")
            if len(proxy_parts) > 1:
                credentials, host_port = proxy_parts
                username, password = credentials.split(":")
                host, port = host_port.split(":")
                
                # Create extension for authenticated SOCKS
                manifest_json = """
                {
                    "version": "1.0.0",
                    "manifest_version": 2,
                    "name": "Chrome Proxy",
                    "permissions": [
                        "proxy",
                        "tabs",
                        "unlimitedStorage",
                        "storage",
                        "<all_urls>",
                        "webRequest",
                        "webRequestBlocking"
                    ],
                    "background": {
                        "scripts": ["background.js"]
                    }
                }
                """
                background_js = f"""
                var config = {{
                    mode: "fixed_servers",
                    rules: {{
                        singleProxy: {{
                            scheme: "socks5",
                            host: "{host}",
                            port: {port}
                        }},
                        bypassList: ["localhost"]
                    }}
                }};
                chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});
                function callbackFn(details) {{
                    return {{
                        authCredentials: {{
                            username: "{username}",
                            password: "{password}"
                        }}
                    }};
                }}
                chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {{urls: ["<all_urls>"]}},
                    ['blocking']
                );
                """
                plugin_dir = "proxy_auth_plugin"
                if not os.path.exists(plugin_dir):
                    os.makedirs(plugin_dir)
                with open(os.path.join(plugin_dir, "manifest.json"), "w") as f:
                    f.write(manifest_json)
                with open(os.path.join(plugin_dir, "background.js"), "w") as f:
                    f.write(background_js)

                options.add_argument(f"--load-extension={os.path.abspath(plugin_dir)}")
                print(f"Using SOCKS proxy with auth plugin: {host}:{port}")
            else:
                # No credentials, just host:port
                options.add_argument(f"--proxy-server={proxy}")
                print(f"Using SOCKS proxy (no auth): {proxy}")
        except Exception as e:
            print(f"Error setting up proxy plugin: {e}")
            options.add_argument(f"--proxy-server={proxy}")
    elif proxy:
        options.add_argument(f"--proxy-server={proxy}")
        print(f"Using proxy: {proxy}")

    driver = None
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        driver.set_window_size(1920, 1080)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })

        driver.get(url)
        print("Waiting for page to load...")
        time.sleep(random.uniform(3, 5))

        # Mimic human-like scrolling
        for _ in range(3):
            scroll_amount = random.randint(300, 1000)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(0.1, 0.9))

        if wait_selector:
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
                )
            except Exception as e:
                print(f"Timeout waiting for selector '{wait_selector}'")

        html_content = driver.page_source
        print(f"Response length: {len(html_content)} bytes")

        return html_content

    except Exception as e:
        print(f"Error fetching HTML: {e}")
        return ""
    finally:
        if driver:
            driver.quit()


def extract_text(element, selector, default=""):
    if not element:
        return default
        
    try:
        found = element.select_one(selector)
        if found:
            return found.get_text(strip=True)
    except Exception as e:
        print(f"Error extracting text with selector '{selector}': {str(e)}")
        
    return default


def extract_first_match(element, selectors, default=""):
    if not element:
        return default
        
    for selector in selectors:
        try:
            found = element.select_one(selector)
            if found:
                return found.get_text(strip=True)
        except Exception:
            continue
    
    return default


def extract_job_info_from_search(job_element):
    if not job_element:
        return None
        
    try:
        # Print job element structure for debugging
        print(f"Analyzing job tile with classes: {job_element.get('class', '')}")
        
        job_uid = job_element.get('data-ev-job-uid', '')
        if not job_uid:
            job_uid = job_element.get('data-test-key', '')
        
        title_element = None
        potential_title_selectors = [
            'h2.job-tile-title a',
            'h2.h5.job-tile-title a',
            '[data-test="job-tile-title-link"]',
            '[data-test="job-tile-title"] a',
            'a.air3-link'
        ]
        
        for selector in potential_title_selectors:
            title_element = job_element.select_one(selector)
            if title_element:
                print(f"Found title element using selector: {selector}")
                break
                
        job_title = title_element.get_text(strip=True) if title_element else "Unknown Title"
        job_url = title_element.get('href', '') if title_element else ""
        if job_url and not job_url.startswith('http'):
            job_url = urljoin(BASE_URL, job_url)
        
        posted_time = ""
        published_date_element = job_element.select_one('[data-test="job-pubilshed-date"]')
        if published_date_element:
            time_spans = published_date_element.select('span')
            if len(time_spans) >= 2:
                posted_time = time_spans[1].get_text(strip=True)
            else: 
                full_text = published_date_element.get_text(strip=True)
                posted_time = full_text.replace("Posted", "").strip()
        if not posted_time:
            posted_time_element = job_element.select_one('[data-test="PostedOn"]')
            if posted_time_element:
                span_element = posted_time_element.select_one('span')
                if span_element:
                    posted_time = span_element.get_text(strip=True)
                else:
                    full_text = posted_time_element.get_text(strip=True)
                    posted_time = full_text.replace("Posted", "").strip()
        
        if not posted_time:
            posted_time = "Unknown"
        
        job_type = None
        budget = None
        budget_element = job_element.select_one('[data-test="job-type-label"]')
        if budget_element:
            job_type_text = budget_element.get_text(strip=True)
            if "Hourly" in job_type_text:
                job_type = "Hourly"
                rate_match = re.search(r'\$(\d+\.\d+)\s*-\s*\$(\d+\.\d+)', job_type_text)
                if rate_match:
                    budget = f"${rate_match.group(1)} - ${rate_match.group(2)} per hour"
            elif "Fixed" in job_type_text:
                job_type = "Fixed"
                budget_elem = job_element.select_one('[data-test="is-fixed-price"] strong:nth-of-type(2)')
                if budget_elem:
                    budget = budget_elem.get_text(strip=True)
        
        experience = extract_text(job_element, '[data-test="experience-level"] strong', "Not specified")
        
        duration = extract_text(job_element, '[data-test="duration-label"] strong:nth-of-type(2)', "Not specified")
        
        description = extract_text(job_element, '.air3-line-clamp p', "No description provided")
        
        skills = []
        skill_selectors = [
            '[data-test="TokenClamp"] [data-test="token"]',
            '[data-test="TokenClamp JobAttrs"] [data-test="token"]',
            '.air3-token-container [data-test="token"]',
            '.skills-list [data-test="Skill"] span.air3-badge'
        ]
        
        for selector in skill_selectors:
            skill_elements = job_element.select(selector)
            if skill_elements:
                for skill in skill_elements:
                    if skill.select_one('span'):
                        skill_text = skill.select_one('span').get_text(strip=True)
                    else:
                        skill_text = skill.get_text(strip=True)
                    
                    if skill_text:
                        skills.append(skill_text)
                
                if skills:
                    break
        
        return {
            "job_uid": job_uid,
            "title": job_title,
            "url": job_url,
            "posted_time": posted_time,
            "job_type": job_type,
            "budget": budget,
            "experience_level": experience,
            "duration": duration,
            "description": description,
            "skills": skills,
            "full_details_fetched": False
        }
    except Exception as e:
        print(f"Error extracting job info from search result: {e}")
        return None


def extract_job_info_from_posting(html_content, job_info):
    if not html_content or not job_info:
        return job_info
    
    try:
        soup = BeautifulSoup(html_content, BS4_PARSER)
        
        description_elem = soup.select_one('[data-test="Description"] p')
        if description_elem:
            job_info["description"] = description_elem.get_text(strip=True)
        
        client_section = soup.select_one('[data-test="AboutClientVisitor"]')
        if client_section:
            member_since = extract_text(client_section, '[data-qa="client-contract-date"] small')
            job_info["client_member_since"] = member_since
            
            client_location = extract_text(client_section, '[data-qa="client-location"] strong')
            city_element = client_section.select_one('[data-qa="client-location"] .nowrap:nth-of-type(1)')
            time_element = client_section.select_one('[data-qa="client-location"] [data-test="LocalTime"]')
            
            location_details = ""
            if city_element:
                city = city_element.get_text(strip=True)
                if city:
                    location_details = city
                    
            if time_element:
                time = time_element.get_text(strip=True)
                if time: 
                    if location_details:
                        location_details += f" | {time}"
                    else:
                        location_details = time
                        
            if location_details:
                job_info["client_location"] = f"{client_location} ({location_details})"
            else:
                job_info["client_location"] = client_location
            
            client_spend = None
            client_spend_elem = client_section.select_one('[data-qa="client-spend"]')
            if client_spend_elem:
                client_spend_text = client_spend_elem.get_text(strip=True)
                spend_match = re.search(r'(\$[\d,.]+[KM]?)', client_spend_text)
                if spend_match:
                    client_spend = spend_match.group(1)
                else:
                    client_spend = client_spend_text
            if client_spend:
                job_info["client_spend"] = client_spend
            
            client_hires = extract_text(client_section, '[data-qa="client-hires"]')
            job_info["client_hires"] = client_hires
            
            client_hours = extract_text(client_section, '[data-qa="client-hours"]')
            if client_hours:
                client_hours = ' '.join(client_hours.split())
            job_info["client_hours"] = client_hours
            
            client_company = extract_text(client_section, '[data-qa="client-company-profile-industry"]')
            client_company_size = extract_text(client_section, '[data-qa="client-company-profile-size"]')
            
            if client_company:
                job_info["client_company"] = f"{client_company} ({client_company_size})" if client_company_size else client_company
        
        activity_section = soup.select_one('[data-test="ClientActivity"]')
        if activity_section:
            proposals = extract_text(activity_section, 'li:nth-of-type(1) .value')
            job_info["proposals"] = proposals
            
            last_viewed = ""
            last_viewed_item = activity_section.select_one('li:nth-of-type(2)')
            if last_viewed_item and 'Last viewed' in last_viewed_item.get_text():
                last_viewed = extract_text(last_viewed_item, '.value')
            job_info["last_viewed"] = last_viewed
            
            interviewing = extract_text(activity_section, 'li .value:-soup-contains("Interviewing")')
            if not interviewing: 
                interviewing_items = activity_section.select('li')
                for item in interviewing_items:
                    if 'Interviewing' in item.get_text():
                        interviewing = extract_text(item, '.value')
                        break
            job_info["interviewing"] = interviewing
            
            invites_sent = ""
            invites_items = activity_section.select('li')
            for item in invites_items:
                if 'Invites sent' in item.get_text():
                    invites_sent = extract_text(item, '.value')
                    break
            job_info["invites_sent"] = invites_sent
            
            unanswered_invites = ""
            unanswered_items = activity_section.select('li')
            for item in unanswered_items:
                if 'Unanswered invites' in item.get_text():
                    unanswered_invites = extract_text(item, '.value')
                    break
            job_info["unanswered_invites"] = unanswered_invites
        
        job_info["full_details_fetched"] = True
        return job_info
        
    except Exception as e:
        print(f"Error extracting job info from posting: {e}")
        return job_info


def create_telegram_message(job_info):
    try:
        message = [
            f"<b>🔔 NEW JOB: {job_info.get('title', 'Unknown Title')}</b>",
            f"<b>💰 Budget:</b> {job_info.get('budget', 'Not specified')}",
            f"<b>⏰ Posted:</b> {job_info.get('posted_time', 'Unknown')}",
            f"<b>📋 Job Type:</b> {job_info.get('job_type', 'Not specified')}",
            f"<b>⚙️ Experience:</b> {job_info.get('experience_level', 'Not specified')}",
            f"<b>⏳ Duration:</b> {job_info.get('duration', 'Not specified')}"
        ]
        
        skills = job_info.get('skills', [])
        if skills:
            message.append(f"<b>🔧 Skills:</b> {', '.join(skills)}")
        
        client_info = []
        if job_info.get('client_member_since'):
            client_info.append(f"<b>👤 Client Since:</b> {job_info.get('client_member_since')}")
        if job_info.get('client_location'):
            client_info.append(f"<b>📍 Location:</b> {job_info.get('client_location')}")
        if job_info.get('client_spend'):
            client_info.append(f"<b>💵 Total Spent:</b> {job_info.get('client_spend')}")
        if job_info.get('client_hires'):
            client_info.append(f"<b>🤝 Hires:</b> {job_info.get('client_hires')}")
        if job_info.get('client_hours'):
            client_info.append(f"<b>⏰ Hours:</b> {job_info.get('client_hours')}")
        if job_info.get('client_company'):
            client_info.append(f"<b>🏢 Company:</b> {job_info.get('client_company')}")
            
        activity_info = []
        if job_info.get('proposals'):
            activity_info.append(f"<b>📝 Proposals:</b> {job_info.get('proposals')}")
        if job_info.get('last_viewed'):
            activity_info.append(f"<b>👁 Last Viewed:</b> {job_info.get('last_viewed')}")
        if job_info.get('interviewing'):
            activity_info.append(f"<b>🗣 Interviewing:</b> {job_info.get('interviewing')}")
        if job_info.get('invites_sent'):
            activity_info.append(f"<b>✉️ Invites Sent:</b> {job_info.get('invites_sent')}")
        
        description = job_info.get('description', '')
        if len(description) > MAX_DESCRIPTION_LENGTH:
            description = description[:MAX_DESCRIPTION_LENGTH] + "..."
        message.append(f"\n<b>📄 Description:</b>\n{description}")
            
        if client_info:
            message.append("\n<b>CLIENT INFO:</b>")
            message.extend(client_info)
            
        if activity_info:
            message.append("\n<b>JOB ACTIVITY:</b>")
            message.extend(activity_info)
        
        message.append(f"\n<a href='{job_info.get('url', '')}'>👉 Apply on Upwork</a>")
        
        return "\n".join(message)
    except Exception as e:
        print(f"Error creating Telegram message: {e}")
        return f"New Job: {job_info.get('title', 'Unknown')} - See details at {job_info.get('url', '')}"


def process_job_posting(job_info):
    if not job_info or not job_info.get('url'):
        return job_info
    
    try:
        print(f"Processing job posting: {job_info['title']}")
        
        job_html = get_html(job_info['url'], wait_selector='[data-test="JobDetailsVisitor"]')
        
        if SAVE_POST_HTML and job_html:
            job_id = job_info.get('job_uid', 'unknown')
            save_html(job_html, "job_html", job_id)
        
        updated_info = extract_job_info_from_posting(job_html, job_info)
        
        return updated_info
    except Exception as e:
        print(f"Error processing job posting: {e}")
        return job_info


def extract_jobs_from_search(html_content):
    if not html_content:
        return []
        
    jobs = []
    try:
        soup = BeautifulSoup(html_content, BS4_PARSER)
        
        job_elements = soup.select('article.job-tile[data-test="JobTile"]')
        if not job_elements:
            job_elements = soup.select('article[data-test="JobTile"], article.job-tile')
        
        print(f"Found {len(job_elements)} job elements in search results")
        
        # Debug the first job structure if available
        if job_elements and len(job_elements) > 0:
            print("\nSample job element structure:")
            first_job = job_elements[0]
            job_classes = first_job.get('class', [])
            job_attrs = first_job.attrs
            print(f"Classes: {job_classes}")
            print(f"Attributes: {', '.join([f'{k}=\"{v}\"' for k, v in job_attrs.items() if k != 'class'])}")
            
            potential_title_selectors = [
                'h2.job-tile-title a', 
                'h2.h5.job-tile-title a',
                '[data-test="job-tile-title-link"]', 
                '[data-test="job-tile-title"] a',
                'a.air3-link'
            ]
            for selector in potential_title_selectors:
                title_elem = first_job.select_one(selector)
                if title_elem:
                    print(f"Found title using selector '{selector}': {title_elem.get_text(strip=True)}")
                    break
        
        for job_element in job_elements:
            job_info = extract_job_info_from_search(job_element)
            if job_info:
                jobs.append(job_info)
                
        print(f"Successfully extracted data for {len(jobs)} jobs")
        return jobs
    except Exception as e:
        print(f"Error extracting jobs from search: {e}")
        return []


def process_search_page(search_url):
    try:
        html_content = get_html(search_url, wait_selector='article.job-tile[data-test="JobTile"]')
        
        if not html_content:
            print("Failed to fetch search page HTML")
            return []
            
        if SAVE_SEARCH_HTML:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            search_id = search_url.split('?')[0].split('/')[-1] if '/' in search_url else 'search'
            save_html(html_content, "search_html", f"{search_id}_{timestamp}")
        
        soup = BeautifulSoup(html_content, BS4_PARSER)
        job_elements = soup.select('article.job-tile[data-test="JobTile"]')
        if not job_elements:
            print("Warning: No job elements found in search results. HTML structure may have changed.")
            print("Trying alternative selectors...")
            job_elements = soup.select('article.job-tile, [data-test="JobTile"]')
            
        if not job_elements:
            print("Still no job elements found. Saving sample HTML for debugging...")
            debug_path = f"./debug/search_html/debug_empty_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(debug_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"Saved debug snippet to {debug_path}")
            
        return extract_jobs_from_search(html_content)
    except Exception as e:
        print(f"Error processing search page: {e}")
        return []

def main():
    print("Starting Upwork Job Scraper")
    setup_directories()
    
    job_history = load_job_history()
    print(f"Loaded {len(job_history)} previously seen jobs")
    
    while True:
        print("-------------------------------------------")
        print(f"Starting search at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-------------------------------------------")
        
        new_jobs_found = False
        
        for url in SEARCH_URLS:
            print(f"Processing search URL: {url}")
            jobs = process_search_page(url)
            
            for job in jobs:
                job_uid = job.get('job_uid')
                if not job_uid:
                    continue
                    
                if job_uid not in job_history:
                    print(f"Found new job: {job['title']}")
                    
                    detailed_job = process_job_posting(job)
                    
                    message = create_telegram_message(detailed_job)
                    send_telegram_message(message)
                    
                    job_history.add(job_uid)
                    new_jobs_found = True
                else:
                    print(f"Skipping already seen job: {job['title']}")
            
            # Small delay between processing different search URLs
            time.sleep(random.uniform(.2, .9))
            
        if new_jobs_found:
            save_job_history(job_history)
            print(f"Job history updated, now tracking {len(job_history)} jobs")
        
        # Add a small random delay before next check
        jitter = random.uniform(0.8, 1.2)
        wait_time = CHECK_INTERVAL * 60 * jitter
        next_check_time = datetime.now() + timedelta(seconds=wait_time)
        print(f"Next check in about {int(wait_time / 60)} minutes at approximately {next_check_time.strftime('%H:%M:%S')}...\n")
        time.sleep(wait_time)


if __name__ == "__main__":
    main()