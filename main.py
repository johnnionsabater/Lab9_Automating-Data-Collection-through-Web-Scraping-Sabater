import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import os
import re
import sqlite3
import time
from urllib.parse import urljoin

def get_soup(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'lxml')
    except Exception as e:
        print(f"Error: {e}")
        return None

def scrape_wikipedia():
    print("\n--- Step 1: Extracting Wikipedia Table ---")
    url = "https://en.wikipedia.org/wiki/Comparison_of_deep_learning_software"
    soup = get_soup(url)
    if not soup: return None

    table = soup.find('table', class_='wikitable')
    if table:
        raw_headers = [th.text.strip() for th in table.find('tr').find_all('th')]
    
        headers = [re.sub(r'\[.*?\]', '', h).replace(' ', '_').strip() for h in raw_headers]
        
        rows = table.find_all('tr')[1:11]
        data = []
        for row in rows:
            cols = row.find_all(['td', 'th'])
            row_data = {headers[i]: cols[i].text.strip() for i in range(len(cols)) if i < len(headers)}
            data.append(row_data)
        return pd.DataFrame(data)
    return None

def save_data(df):
    if df is None: return

    df.to_csv('my_data.csv', index=False)
   
    df.to_json('my_data.json', orient='records', indent=4)

    conn = sqlite3.connect('my_database.db')
    df.to_sql('software_table', conn, if_exists='replace', index=False)
    conn.close()
    print("\n[DONE] Check your folder! Created: my_data.csv, my_data.json, my_database.db")

if __name__ == "__main__":
    result_df = scrape_wikipedia()
    save_data(result_df)
    if result_df is not None:
        print("\nPreview of extracted data:")
        print(result_df.head())