from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import json
from datetime import datetime

# ========== НАСТРОЙКИ ==========
KEYWORDS = ["парсинг", "парсер", "скрипт", "автоматизация", "бот",
    "telegram", "excel", "google", "api", "python",
    "сбор данных", "рассылка", "ии", "ai", "десктоп",
    "приложение", "битрикс", "контактов", "голос",
    "распознавание", "нейросеть", "chatgpt", "openai",
    "веб-скрапинг", "selenium", "requests", "pandas",
    "озон", "wildberries", "маркетплейс", "авито",
    "парсить", "спарсить", "выгрузка данных"]
URL = "https://kwork.ru/projects"
OUTPUT_FILE = "kwork_orders.json"
# ===============================

def main():
    print("=" * 50)
    print("🔍 KWORK SELENIUM PARSER")
    print("=" * 50)
    
    # Настройки браузера
    options = Options()
    options.add_argument("--headless")  # Убери, если хочешь видеть окно
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36")
    
    driver = webdriver.Chrome(options=options)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Загружаем страницу...")
    driver.get(URL)
    
    # Ждём загрузки
    import time
    time.sleep(3)
    
    # Ищем все ссылки на проекты
    links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/projects/']")
    print(f"Найдено ссылок на проекты: {len(links)}")
    
    orders = []
    seen = set()
    
    for link in links:
        href = link.get_attribute('href')
        title = link.text.strip()
        
        if not href or not title:
            continue
        
        # Чистим URL
        clean_href = href.split('?')[0]
        if clean_href in seen:
            continue
        seen.add(clean_href)
        
        # Фильтр по ключевым словам
        title_lower = title.lower()
        if not any(kw.lower() in title_lower for kw in KEYWORDS):
            continue
        
        order_id = clean_href.split('/')[-1]
        
        order = {
            "id": order_id,
            "title": title,
            "url": clean_href,
            "found_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        orders.append(order)
        print(f"✅ {title[:70]}...")
    
    driver.quit()
    
    if orders:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(orders, f, ensure_ascii=False, indent=2)
        print(f"\n📁 Сохранено {len(orders)} заказов в {OUTPUT_FILE}")
    else:
        print("😴 Ничего не найдено")

if __name__ == "__main__":
    main()
