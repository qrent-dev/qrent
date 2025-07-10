import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import tempfile
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
from datetime import datetime
import re
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv('.env')

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_PORT = int(os.getenv("DB_PORT", 3306))

def fetch_db_data():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            port=DB_PORT
        )
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("DESCRIBE properties")
            columns_info = cursor.fetchall()
            available_columns = [col['Field'] for col in columns_info]
            print(f"Available columns in database: {available_columns}")
            
            desired_columns = [
                'house_id', 'description_en', 'available_date', 
                'published_at', 'keywords', 'average_score', 
                'url', 'description_cn'
            ]
            
            existing_columns = [col for col in desired_columns if col in available_columns]
            missing_columns = [col for col in desired_columns if col not in available_columns]
            
            if missing_columns:
                print(f"Warning: Missing columns in database: {missing_columns}")
            
            if not existing_columns:
                print("No required columns found in database")
                return pd.DataFrame()
            
            columns_str = ', '.join(existing_columns)
            sql = f"SELECT {columns_str} FROM properties"
            
            cursor.execute(sql)
            db_data = cursor.fetchall()
            cursor.close()
            connection.close()
            print(f"Successfully fetched data from database with columns: {existing_columns}")
            print(f"Successfully fetched data from database with columns: {existing_columns}")
            return pd.DataFrame(db_data)
        else:
            print("Cannot connect to the database")
            return pd.DataFrame()
    except Error as e:
        print(f"Database error: {e}")
        return pd.DataFrame()

def scrape_property_data(university):
    current_date = datetime.now().strftime('%y%m%d')
    today_file = f"{university}_rentdata_cleaned_{current_date}.csv"
    output_file = f"{university}_rentdata_{current_date}.csv"

    if not os.path.exists(today_file):
        raise FileNotFoundError("Data file not found")

    today_data = pd.read_csv(today_file)

    yesterday_data = None
    yesterday_date = (datetime.now() - pd.Timedelta(days=1)).strftime('%y%m%d')
    yesterday_file = f"{university}_rentdata_{yesterday_date}.csv"
    
    if os.path.exists(yesterday_file):
        print(f"Found previous day's data: {yesterday_file}")
        yesterday_data = pd.read_csv(yesterday_file)
        
        all_required_cols = ['description_en', 'available_date', 'published_at', 'keywords', 'average_score', 'url', 'description_cn']
        for col in all_required_cols:
            if col not in today_data.columns:
                today_data[col] = None
        
        if 'houseId' in today_data.columns and 'houseId' in yesterday_data.columns:
            yesterday_data_unique = yesterday_data.drop_duplicates(subset=['houseId'], keep='first')
            
            for col in all_required_cols:
                if col in yesterday_data_unique.columns:
                    print(f"Mapping column from yesterday's data: {col}")
                    today_data[col] = today_data['houseId'].map(
                        yesterday_data_unique.set_index('houseId')[col]
                    )
                else:
                    print(f"Column {col} not found in yesterday's data, keeping as None")
        else:
            print("Warning: 'houseId' column not found in data files. Cannot map from yesterday's data.")
    else:
        print(f"No previous day's data found: {yesterday_file}")
        db_df = fetch_db_data()
        if not db_df.empty:
            if 'houseId' in today_data.columns:
                db_df_unique = db_df.drop_duplicates(subset=['house_id'], keep='first')
                all_required_cols = ['description_en', 'available_date', 'published_at', 'keywords', 'average_score', 'url', 'description_cn']

                for col in all_required_cols:
                    if col not in today_data.columns:
                        today_data[col] = None

                for col in all_required_cols:
                    if col in db_df_unique.columns:
                        print(f"Mapping column from database: {col}")
                        today_data[col] = today_data['houseId'].map(
                            db_df_unique.set_index('house_id')[col]
                        )
                    else:
                        print(f"Column {col} not found in database, keeping as None")
            else:
                print("Warning: 'houseId' column not found in CSV data. Skipping DB mapping.")
        else:
            print("No data retrieved from the database. Skipping DB mapping.")

    if 'description_en' not in today_data.columns:
        today_data['description_en'] = None
    if 'available_date' not in today_data.columns:
        today_data['available_date'] = None
    
    missing_property_desc = today_data[
        (today_data['description_en'].isna()) | 
        (today_data['description_en'] == 'N/A') |
        (today_data['description_en'] == '')
    ]
    num_missing = len(missing_property_desc)
    print(f"Properties needing detailed scraping: {num_missing}")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920x1080')
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument(f'--user-data-dir={tempfile.mkdtemp()}')

    driver = webdriver.Chrome(options=chrome_options)
    base_url = "https://www.domain.com.au/{}/"
    
    def scrape_data(url):
        try:
            driver.get(url)
            time.sleep(5) 
            soup = BeautifulSoup(driver.page_source, "html.parser")
            description_container = soup.find("div", {"data-testid": "listing-details__description"})
            if description_container:
                headline = description_container.find("h3", {"data-testid": "listing-details__description-headline"})
                paragraphs = description_container.find_all("p")
                description = (headline.text.strip() if headline else "") + " " + " ".join(p.text.strip() for p in paragraphs)
            else:
                description = "N/A"
            available_date = "N/A"
            date_container = soup.find("ul", {"data-testid": "listing-summary-strip"})
            if date_container:
                li_item = date_container.find("li")
                if li_item:
                    date_text = li_item.get_text(strip=True)
                    if "Available Now" in date_text:
                        available_date = "Available Now"
                    elif "Available from" in date_text:
                        strong_tag = li_item.find("strong")
                        available_date = strong_tag.text.strip() if strong_tag else "N/A"
                    else:
                        available_date = "N/A"
            if available_date == "Available Now":
                available_date = datetime.now()
            else:
                try:
                    cleaned = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', available_date)
                    available_date = datetime.strptime(cleaned, "%A, %d %B %Y")
                except Exception as e:
                    available_date = None

            published_at = datetime.now()
            return description, available_date, published_at

        except Exception as e:
            print(f"Error scraping URL {url}: {e}")
            published_at = datetime.now().strftime('%Y-%m-%d')
            return "N/A", "N/A", published_at

    for index, row in tqdm(missing_property_desc.iterrows(), total=num_missing, desc="Property Description & Available Time"):
        address = row['Combined Address']
        url = base_url.format(address)     
        description, avail_date, published_at = scrape_data(url)  
        print(f": index={index}, URL={url}, description={description[:100]}, available_date={avail_date}")

        today_data.at[index, 'description_en'] = description
        today_data.at[index, 'available_date'] = avail_date
        today_data.at[index, 'published_at'] = published_at

    driver.quit()

    today_data.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Merge data to: {output_file}")

    df = pd.read_csv(output_file)
    df['url'] = df['Combined Address'].apply(lambda address: f"https://www.domain.com.au/{address}")
    df.drop(columns=['Combined Address'], inplace=True)
    final_output = f"{university}_rentdata_{current_date}.csv"
    df.to_csv(final_output, index=False)
    print(f"Save to: {final_output}")
