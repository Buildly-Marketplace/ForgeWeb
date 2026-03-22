#!/usr/bin/env python3
"""
Import all NullRecords content into ForgeWeb local database.
- News articles (from news_articles.json)
- Daily reports (from daily_reports/)
- Store items (from website/store/store_items.json)
- Artists (from artists.html)

Run from the forgeweb/admin directory.
"""
import os
import json
import sqlite3
from pathlib import Path
from bs4 import BeautifulSoup

def get_db():
    db_path = os.path.join(os.path.dirname(__file__), 'forgeweb.db')
    return sqlite3.connect(db_path)

def import_news_articles(conn, news_json_path):
    with open(news_json_path, 'r') as f:
        articles = json.load(f)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS news (
        id TEXT PRIMARY KEY,
        title TEXT,
        content TEXT,
        url TEXT,
        author TEXT,
        published_date TEXT,
        discovered_date TEXT,
        artist_mentioned TEXT,
        sentiment TEXT,
        article_type TEXT,
        status TEXT,
        tags TEXT,
        excerpt TEXT
    )''')
    for a in articles:
        cur.execute('''INSERT OR REPLACE INTO news (id, title, content, url, author, published_date, discovered_date, artist_mentioned, sentiment, article_type, status, tags, excerpt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (a.get('id'), a.get('title'), a.get('content'), a.get('url'), a.get('author'), a.get('published_date'), a.get('discovered_date'),
             json.dumps(a.get('artist_mentioned')), a.get('sentiment'), a.get('article_type'), a.get('status'), json.dumps(a.get('tags')), a.get('excerpt')))
    conn.commit()
    print(f"Imported {len(articles)} news articles.")

def import_daily_reports(conn, reports_dir):
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS daily_reports (
        filename TEXT PRIMARY KEY,
        content TEXT
    )''')
    count = 0
    for file in Path(reports_dir).glob('*.html'):
        with open(file, 'r') as f:
            html = f.read()
        cur.execute('INSERT OR REPLACE INTO daily_reports (filename, content) VALUES (?, ?)', (file.name, html))
        count += 1
    conn.commit()
    print(f"Imported {count} daily reports.")

def import_store_items(conn, store_json_path):
    with open(store_json_path, 'r') as f:
        items = json.load(f)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS store_items (
        id TEXT PRIMARY KEY,
        type TEXT,
        title TEXT,
        artist TEXT,
        author TEXT,
        cover_art TEXT,
        audio_files TEXT,
        ebook_file TEXT,
        description TEXT,
        suggested_donation REAL,
        download_bundle TEXT
    )''')
    for item in items:
        cur.execute('''INSERT OR REPLACE INTO store_items (id, type, title, artist, author, cover_art, audio_files, ebook_file, description, suggested_donation, download_bundle)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (item.get('id'), item.get('type'), item.get('title'), item.get('artist'), item.get('author'), item.get('cover_art'),
             json.dumps(item.get('audio_files')), item.get('ebook_file'), item.get('description'), item.get('suggested_donation'), item.get('download_bundle')))
    conn.commit()
    print(f"Imported {len(items)} store items.")

def import_artists(conn, artists_html_path):
    with open(artists_html_path, 'r') as f:
        soup = BeautifulSoup(f, 'html.parser')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS artists (
        name TEXT PRIMARY KEY,
        description TEXT,
        genre TEXT,
        founding_date TEXT,
        url TEXT,
        image TEXT,
        albums TEXT
    )''')
    # Parse JSON-LD structured data for artists
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string)
            if data.get('@type') == 'CollectionPage' and 'mainEntity' in data:
                for artist in data['mainEntity']:
                    if artist.get('@type') == 'MusicGroup':
                        cur.execute('''INSERT OR REPLACE INTO artists (name, description, genre, founding_date, url, image, albums)
                            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                            (artist.get('name'), artist.get('description'), json.dumps(artist.get('genre')), artist.get('foundingDate'),
                             artist.get('url'), artist.get('image'), json.dumps(artist.get('album'))))
        except Exception as e:
            print(f"Error parsing artist JSON-LD: {e}")
    conn.commit()
    print("Imported artists from artists.html.")

def main():
    base = Path(__file__).parent.parent.parent
    conn = get_db()
    # News articles - prefer admin copy, fall back to root
    news_path = str(Path(__file__).parent / 'news_articles.json')
    if not os.path.exists(news_path):
        news_path = str(base / 'docs' / 'news_articles.json')
    import_news_articles(conn, news_path)
    import_daily_reports(conn, str(base / 'dashboard/daily_reports'))
    # Store items - prefer admin copy, fall back to docs
    store_path = str(Path(__file__).parent / 'store_items.json')
    if not os.path.exists(store_path):
        store_path = str(base / 'docs' / 'store' / 'store_items.json')
    import_store_items(conn, store_path)
    # Artists - only if file exists (page may not be generated yet)
    artists_path = str(base / 'docs' / 'artists.html')
    if os.path.exists(artists_path):
        import_artists(conn, artists_path)
    else:
        print('Skipped artists import (docs/artists.html not found)')
    conn.close()
    print("All content imported into ForgeWeb database.")

if __name__ == '__main__':
    main()
