import asyncio
import json
import csv
import random
import os
import re
import sys
import time
from datetime import datetime
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

sys.stdout.reconfigure(encoding='utf-8')

CITIES = [
    "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Amasya", "Ankara", "Antalya", "Artvin", "Aydın", "Balıkesir",
    "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli",
    "Diyarbakır", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkari",
    "Hatay", "Isparta", "Mersin", "İstanbul", "İzmir", "Kars", "Kastamonu", "Kayseri", "Kırklareli", "Kırşehir",
    "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", "Kahramanmaraş", "Mardin", "Muğla", "Muş", "Nevşehir",
    "Niğde", "Ordu", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Tekirdağ", "Tokat",
    "Trabzon", "Tunceli", "Şanlıurfa", "Uşak", "Van", "Yozgat", "Zonguldak", "Aksaray", "Bayburt", "Karaman",
    "Kırıkkale", "Batman", "Şırnak", "Bartın", "Ardahan", "Iğdır", "Yalova", "Karabük", "Kilis", "Osmaniye", "Düzce"
]

AUTH_TOKENS = [
    "d1b89781f7acf22cd5c04cae1ad989c7ee8a8e5b"
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36"
]

def extract_locations(text):
    if not text:
        return []
    locations = []
    words = re.findall(r'\b\w+\b', text)
    for word in words:
        capitalized_word = word.capitalize()
        if capitalized_word in CITIES and capitalized_word not in locations:
            locations.append(capitalized_word)
    return locations

os.makedirs("sessions", exist_ok=True)
os.makedirs("states", exist_ok=True)

DATA_FILE = "massive_crisis_data.csv"

# Global Auto-Resume Set
GLOBAL_SCRAPED_URLS = set()
if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'url' in row:
                    GLOBAL_SCRAPED_URLS.add(row['url'])
        print(f"✅ Auto-Resume: massive_crisis_data.csv dosyasından {len(GLOBAL_SCRAPED_URLS)} benzersiz URL yüklendi.")
    except Exception as e:
        print(f"⚠️ Auto-Resume CSV yükleme hatası: {e}")

GLOBAL_STATS = {}
LAST_LOG_TIME = time.time()

def log_metrics():
    global LAST_LOG_TIME
    current_time = time.time()
    if current_time - LAST_LOG_TIME >= 300: # 5 Dakika
        print("\n" + "="*50)
        print("📊 5 DAKİKALIK PERFORMANS & DURUM ÖZETİ 📊")
        for k, v in GLOBAL_STATS.items():
            print(f" 🔹 {k.upper()}: {v} Tweet toplandı.")
        print("="*50 + "\n")
        LAST_LOG_TIME = current_time

def append_single_tweet(tweet_data, file_path):
    if not tweet_data:
        return
    file_exists = os.path.exists(file_path)
    keys = tweet_data.keys()
    with open(file_path, 'a', newline='', encoding='utf-8-sig') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        if not file_exists:
            dict_writer.writeheader()
        dict_writer.writerow(tweet_data)

def get_session_file(token_index):
    session_file = f"sessions/session_{token_index}.json"
    if not os.path.exists(session_file):
        token = AUTH_TOKENS[token_index]
        session_data = {
            "cookies": [
                {
                    "name": "auth_token",
                    "value": token,
                    "domain": ".twitter.com",
                    "path": "/",
                    "expires": 253402300799,
                    "httpOnly": True,
                    "secure": True,
                    "sameSite": "None"
                },
                {
                    "name": "auth_token",
                    "value": token,
                    "domain": ".x.com",
                    "path": "/",
                    "expires": 253402300799,
                    "httpOnly": True,
                    "secure": True,
                    "sameSite": "None"
                }
            ],
            "origins": []
        }
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=4)
    return session_file

async def intercept_route(route):
    if route.request.resource_type in ["image", "stylesheet", "font", "media"]:
        await route.abort()
    else:
        await route.continue_()

async def scrape_task(task_config, browser, token_index=0, task_start_time=None):
    global GLOBAL_SCRAPED_URLS
    
    task_name = task_config['name']
    keywords_list = task_config['keywords']
    since_date = task_config['since']
    until_date = task_config['until']
    max_tweets = task_config['max_tweets']

    state_file = f"states/state_{task_name}.json"
    
    scraped_ids = set()
    total_collected = 0
    last_break_count = 0
    ban_penalty = 300 
    
    if task_start_time is None:
        task_start_time = time.time()
    
    if os.path.exists(state_file):
        with open(state_file, 'r', encoding='utf-8') as f:
            state_data = json.load(f)
            scraped_ids = set(state_data.get('scraped_ids', []))
            total_collected = state_data.get('total_collected', 0)
            last_break_count = total_collected
            print(f"[{task_name.upper()}] Önceki oturumdan {total_collected} tweet hafızaya yüklendi.")
            
    GLOBAL_STATS[task_name] = total_collected
            
    if total_collected >= max_tweets:
        print(f"[{task_name.upper()}] Hedefe ({max_tweets}) zaten ulaşıldı. Bu görev atlanıyor.")
        return True
        
    session_file = get_session_file(token_index)
    selected_ua = random.choice(USER_AGENTS)
    
    context = await browser.new_context(
        viewport={'width': 1366, 'height': 768}, # RAM Tasarrufu için Viewport Küçültüldü
        user_agent=selected_ua,
        storage_state=session_file,
        locale='tr-TR',
        timezone_id='Europe/Istanbul'
    )
    
    page = await context.new_page()
    await Stealth().apply_stealth_async(page)
    await page.route("**/*", intercept_route)
    
    # DEV OR SORGUSU & SHUFFLE KEYWORDS
    shuffled_words = list(keywords_list)
    random.shuffle(shuffled_words) # Her çalıştığında bot patterni kırmak için karıştır
    
    formatted_words = [f'"{w}"' if ' ' in w else w for w in shuffled_words]
    keyword_query = "(" + " OR ".join(formatted_words) + ")"
    query = f"{keyword_query} since:{since_date} until:{until_date} lang:tr"
    encoded_query = query.replace(" ", "%20").replace(":", "%3A").replace('"', "%22")
    url = f"https://twitter.com/search?q={encoded_query}&src=typed_query&f=live"
    
    print(f"[{task_name.upper()}] ⚡ DEEP SCROLL ARAMASI (Shuffled): {keyword_query}")
    
    try:
        await page.goto("https://twitter.com/home", wait_until="commit")
        await asyncio.sleep(2) 
        
        await page.goto(url, wait_until="commit")
        
        try:
            await page.wait_for_selector('article[data-testid="tweet"]', timeout=20000)
        except Exception as e:
            pass
            
        scroll_attempts = 0
        
        while total_collected < max_tweets:
            # Düzenli metrik yazdırma kontrolü
            log_metrics()
            
            # Sayfa çökme kontrolü
            if page.is_closed():
                raise Exception("Page manually closed or crashed.")
                
            if "login" in page.url or await page.locator("text=Log in to X").count() > 0:
                print(f"\n[{task_name.upper()}] 🛡️ [BAN SAVUNMASI] Twitter limiti aşıldı.")
                print(f"[{task_name.upper()}] 🛡️ Ceza süresi: {ban_penalty // 60} dakika uyunuyor...")
                await asyncio.sleep(ban_penalty)
                ban_penalty += 300 
                
                print(f"[{task_name.upper()}] 🛡️ Uykudan uyanıldı. Sayfa yenileniyor...")
                await page.goto("https://twitter.com/home", wait_until="commit")
                await asyncio.sleep(2)
                await page.goto(url, wait_until="commit") 
                continue
                
            try:
                tweets = await page.locator('article[data-testid="tweet"]').all()
            except Exception as e:
                print(f"[{task_name.upper()}] Locator hatası: {e}. Sayfa yenileniyor...")
                await page.goto(url, wait_until="commit")
                continue

            new_tweets_found = False
            
            for tweet in tweets:
                try:
                    time_element = tweet.locator('time')
                    if await time_element.count() == 0:
                        continue
                        
                    tweet_url = await time_element.evaluate("el => el.closest('a').href")
                    
                    # Auto-Resume ve Duplicate Kontrolü
                    if tweet_url in scraped_ids or tweet_url in GLOBAL_SCRAPED_URLS:
                        continue
                        
                    text_locator = tweet.locator('div[data-testid="tweetText"]')
                    tweet_text = await text_locator.inner_text() if await text_locator.count() > 0 else ""
                    tweet_date = await time_element.get_attribute("datetime")
                    user_handle = tweet_url.split('/')[3]
                    locations = extract_locations(tweet_text)
                    
                    tweet_data = {
                        "category": task_name,
                        "user_handle": user_handle,
                        "url": tweet_url,
                        "text": tweet_text.replace('\n', ' '),
                        "date": tweet_date,
                        "extracted_locations": ", ".join(locations),
                        "profile_location": "Bilinmiyor (Profil Ziyareti Gerektirir)"
                    }
                    
                    append_single_tweet(tweet_data, DATA_FILE)
                    
                    scraped_ids.add(tweet_url)
                    GLOBAL_SCRAPED_URLS.add(tweet_url)
                    total_collected += 1
                    GLOBAL_STATS[task_name] = total_collected
                    new_tweets_found = True
                    
                    with open(state_file, 'w', encoding='utf-8') as f:
                        json.dump({'total_collected': total_collected, 'scraped_ids': list(scraped_ids)}, f, ensure_ascii=False)
                        
                    if total_collected % 20 == 0:
                        ban_penalty = 300 
                        
                    elapsed_seconds = time.time() - task_start_time
                    elapsed_mins = elapsed_seconds / 60
                    tweets_per_min = total_collected / elapsed_mins if elapsed_mins > 0 else 0
                    
                    if tweets_per_min > 0:
                        remaining_tweets = max_tweets - total_collected
                        remaining_hours = (remaining_tweets / tweets_per_min) / 60
                    else:
                        remaining_hours = 0
                        
                    print(f"[{task_name.upper()}] Çekilen: {total_collected}/{max_tweets} -> {user_handle}")
                    print(f"    [HIZ] Dakikada Ortalama: {tweets_per_min:.1f} tweet | Toplam Süre: {elapsed_mins:.1f} dk | Kalan Tahmini Süre: {remaining_hours:.1f} saat")
                    
                    if total_collected >= max_tweets:
                        break
                        
                except Exception as e:
                    continue
            
            if total_collected - last_break_count >= 100:
                print(f"[{task_name.upper()}] ☕ 100 Tweet Çekildi: 30 Saniye dinleniliyor...")
                await asyncio.sleep(30.0)
                last_break_count = total_collected
            
            if not new_tweets_found:
                scroll_attempts += 1
            else:
                scroll_attempts = 0 
                
            # Smart Jump: 10 kez yeni tweet bulunamazsa görevi bitir
            if scroll_attempts >= 10:
                print(f"[{task_name.upper()}] ⏭️ Smart Jump: Üst üste 10 scroll işleminde yeni tweet bulunamadı. Tarihteki veriler tükendi. Sıradaki kategoriye geçiliyor...")
                return True
                
            if total_collected >= max_tweets:
                break
                
            # Hızlı Kaydırma
            await page.evaluate("window.scrollBy({top: 3000, behavior: 'smooth'})")
            await asyncio.sleep(2.0)
            
    except Exception as e:
        print(f"[{task_name.upper()}] Beklenmeyen Görev Hatası: {e}")
        raise e 
        
    finally:
        try:
            await context.close()
        except Exception:
            pass
            
    return total_collected >= max_tweets

async def main():
    # YENİ GÖREV LİSTESİ
    tasks = [
        {
            "name": "yangin_2021",
            "keywords": ["yangın", "alev", "manavgat", "marmaris"],
            "since": "2021-07-28",
            "until": "2021-08-05",
            "max_tweets": 3000
        },
        {
            "name": "bogazici_2021",
            "keywords": ["boğaziçi", "kayyum", "direniş"],
            "since": "2021-01-04",
            "until": "2021-02-10",
            "max_tweets": 3000
        },
        {
            "name": "corlu_2018",
            "keywords": ["çorlu", "tren", "kaza", "ihmal"],
            "since": "2018-07-08",
            "until": "2018-07-15",
            "max_tweets": 3000
        },
        {
            "name": "maden_2024",
            "keywords": ["iliç", "maden", "göçük", "siyanür"],
            "since": "2024-02-13",
            "until": "2024-02-20",
            "max_tweets": 3000
        }
    ]

    for t in tasks:
        GLOBAL_STATS[t['name']] = 0

    print("==================================================")
    print("Twitter DEEP SCROLL Scraper Başlıyor! (Yeni Kategoriler)")
    print(f"Hedeflenen Toplam Tweet: {len(tasks) * 3000}")
    print("Master Dosya: massive_crisis_data.csv")
    print("==================================================\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) 
        
        for task in tasks:
            print(f"\n{'='*50}\n[{task['name'].upper()}] Senaryosu Başlatılıyor...\n{'='*50}")
            
            task_start_time = time.time()
            
            # Restart Loop 
            while True:
                try:
                    is_completed = await scrape_task(task, browser, task_start_time=task_start_time)
                    if is_completed:
                        break
                except Exception as e:
                    print(f"[{task['name'].upper()}] 🚨 Çökme tespit edildi! 10 saniye sonra sessizce baştan başlatılıyor...")
                    await asyncio.sleep(10)
            
            long_sleep = random.uniform(100.0, 140.0)
            print(f"\n✅ [{task['name'].upper()}] Senaryosu bitti. Diğer göreve geçmeden önce mola!")
            print(f"😴 {long_sleep/60:.1f} dakika uyunuyor...")
            await asyncio.sleep(long_sleep)
            
        await browser.close()
        
    print("\n🎉 TÜM GÖREVLER BAŞARIYLA TAMAMLANDI!")

if __name__ == "__main__":
    asyncio.run(main())
