#!/usr/bin/env python3
"""
Update ForgeWeb navigation and pages with full schema support.
Run from the forgeweb/admin directory.
"""
import os
import sqlite3
from pathlib import Path
from datetime import datetime

def slugify(title):
    return title.lower().replace(' ', '-').replace('/', '').replace('.', '')

NAV_ITEMS = [
    {"title": "Home", "url": "/", "order": 1, "file": "docs/index.html"},
    {"title": "Store", "url": "/store/", "order": 2, "file": "docs/store/index.html"},
    {"title": "News", "url": "/news/", "order": 3, "file": "docs/news/index.html"},
    {"title": "About", "url": "/about.html", "order": 4, "file": "docs/about.html"},
    {"title": "Contact", "url": "/contact.html", "order": 5, "file": "docs/contact.html"}
]

def get_db():
    db_path = os.path.join(os.path.dirname(__file__), 'forgeweb.db')
    return sqlite3.connect(db_path)

def import_pages_and_nav(conn, base_path):
    cur = conn.cursor()
    # Pages table (full schema)
    cur.execute('''CREATE TABLE IF NOT EXISTS pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        file_path TEXT NOT NULL,
        template TEXT,
        status TEXT DEFAULT 'published',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        published_at TIMESTAMP
    )''')
    # Navigation table (full schema)
    cur.execute('''CREATE TABLE IF NOT EXISTS navigation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        position INTEGER DEFAULT 0,
        parent_id INTEGER,
        is_active BOOLEAN DEFAULT 1,
        open_new_tab BOOLEAN DEFAULT 0,
        css_class TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    cur.execute('DELETE FROM navigation')
    for item in NAV_ITEMS:
        page_path = base_path / item["file"]
        slug = slugify(item["title"])
        now = datetime.now().isoformat()
        # Insert/update page
        cur.execute('''INSERT OR REPLACE INTO pages (title, slug, file_path, template, status, created_at, updated_at, published_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (item['title'], slug, str(page_path), None, 'published', now, now, now))
        # Insert nav item
        cur.execute('''INSERT INTO navigation (title, url, position, is_active, open_new_tab, css_class, created_at, updated_at)
            VALUES (?, ?, ?, 1, 0, NULL, ?, ?)''',
            (item['title'], item['url'], item['order'], now, now))
    conn.commit()
    print(f"Navigation and pages updated for {len(NAV_ITEMS)} sections (full schema).")

def main():
    base = Path(__file__).parent.parent.parent
    conn = get_db()
    import_pages_and_nav(conn, base)
    conn.close()
    print("All navigation and main pages imported (full schema).")

if __name__ == '__main__':
    main()
