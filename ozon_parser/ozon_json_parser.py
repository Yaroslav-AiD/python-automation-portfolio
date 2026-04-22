from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import json
import re
import time
from datetime import datetime
from urllib.parse import unquote

def parse_ozon_selenium_json(query, pages=1):
    """
    Открывает Ozon через Selenium, проходит капчу вручную,
    извлекает JSON с товарами и парсит все данные.
    """
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36")
    
    driver = webdriver.Chrome(options=options)
    all_products = []
    seen_skus = set()
    
    try:
        for page in range(1, pages + 1):
            url = f"https://www.ozon.ru/search/?text={query}&page={page}"
            print(f"\n🔍 Страница {page}...")
            driver.get(url)
            
            if page == 1:
                print("⏳ Пройди капчу вручную и нажми Enter в терминале...")
                input()
            
            time.sleep(3)
            
            # Получаем HTML страницы
            html = driver.page_source
            
            # Ищем JSON с товарами
            pattern = r'<div[^>]*id="state-tileGridDesktop[^"]*"[^>]*data-state="([^"]+)"'
            match = re.search(pattern, html)
            
            if not match:
                pattern2 = r'data-state="({[^"]*&quot;items&quot;:[^"]*})"'
                match = re.search(pattern2, html)
            
            if not match:
                print("   ❌ JSON не найден")
                continue
            
            json_str = match.group(1)
            json_str = json_str.replace('&quot;', '"').replace('\\u002F', '/')
            
            try:
                data = json.loads(json_str)
            except:
                print("   ❌ Ошибка парсинга JSON")
                continue
            
            items = data.get('items', [])
            print(f"   📦 Найдено товаров: {len(items)}")
            
            for item in items:
                try:
                    sku = item.get('sku')
                    if sku in seen_skus:
                        continue
                    seen_skus.add(sku)
                    
                    action = item.get('action', {})
                    link = action.get('link', '')
                    if link:
                        link = "https://www.ozon.ru" + unquote(link)
                    
                    main_state = item.get('mainState', [])
                    
                    title = ""
                    price = ""
                    old_price = ""
                    discount = ""
                    rating = ""
                    reviews = ""
                    image_url = ""
                    
                    for state_item in main_state:
                        if state_item.get('id') == 'name':
                            text_atom = state_item.get('textAtom', {})
                            title = text_atom.get('text', '')
                        
                        elif state_item.get('type') == 'priceV2':
                            price_v2 = state_item.get('priceV2', {})
                            prices = price_v2.get('price', [])
                            if len(prices) >= 1:
                                price = prices[0].get('text', '').replace(' ', ' ')
                            if len(prices) >= 2:
                                old_price = prices[1].get('text', '').replace(' ', ' ')
                            discount = price_v2.get('discount', '').replace('−', '-')
                        
                        elif state_item.get('type') == 'labelListV2':
                            label_list = state_item.get('labelListV2', {})
                            labels = label_list.get('items', [])
                            for lbl in labels:
                                if lbl.get('type') == 'text':
                                    txt = lbl.get('text', {}).get('text', '')
                                    if '.' in txt and any(c.isdigit() for c in txt):
                                        rating = txt
                                    elif 'отзыв' in txt.lower():
                                        reviews = txt.replace('\xa0', ' ')
                    
                    tile_image = item.get('tileImage', {})
                    img_items = tile_image.get('items', [])
                    if img_items:
                        for img in img_items:
                            if img.get('type') == 'image':
                                image_url = img.get('image', {}).get('link', '')
                                break
                    
                    price_clean = re.sub(r'[^\d]', '', price) if price else '0'
                    price_int = int(price_clean) if price_clean else 0
                    
                    all_products.append({
                        "SKU": sku,
                        "Название": title,
                        "Цена": price,
                        "Старая цена": old_price,
                        "Скидка": discount,
                        "Рейтинг": rating,
                        "Отзывы": reviews,
                        "Ссылка": link,
                        "Картинка": image_url,
                        "Цена (число)": price_int
                    })
                    
                    print(f"   ✅ {title[:40]}... - {price}")
                    
                except:
                    continue
                    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        driver.quit()
    
    return all_products

def save_to_excel(products, filename=None):
    if not filename:
        filename = f"ozon_selenium_json_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    if not products:
        print("\n😴 Нет данных")
        return
    
    df = pd.DataFrame(products)
    df = df.drop_duplicates(subset=['SKU'])
    df = df.sort_values('Цена (число)')
    df = df.drop(columns=['Цена (число)'])
    df.to_excel(filename, index=False)
    
    print(f"\n📁 Сохранено: {filename}")
    print(f"   Уникальных товаров: {len(df)}")
    
    if len(df) > 0:
        print("\n🏆 ТОП-5 дешёвых товаров:")
        for _, row in df.head(5).iterrows():
            print(f"   {row['Название'][:40]}... - {row['Цена']}")

if __name__ == "__main__":
    print("=" * 50)
    print("🛒 OZON PARSER (Selenium + JSON)")
    print("=" * 50)
    
    query = input("🔍 Поиск: ").strip() or "ноутбук"
    pages = int(input("📄 Страниц (1-3): ").strip() or "1")
    
    products = parse_ozon_selenium_json(query, min(pages, 3))
    save_to_excel(products)
