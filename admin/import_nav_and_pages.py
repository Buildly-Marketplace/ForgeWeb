#!/usr/bin/env python3
"""
Update ForgeWeb navigation and pages to match www.nullrecords.com + Store.
Run from the forgeweb/admin directory.
"""
import os
import sqlite3
from pathlib import Path

NAV_ITEMS = [
    {"title": "Home", "url": "/", "order": 1, "page_file": "docs/index.html"},
    {"title": "Store", "url": "/store/", "order": 2, "page_file": "docs/store/index.html"},
    {"title": "News", "url": "/news/", "order": 3, "page_file": "docs/news/index.html"},
    {"title": "About", "url": "/about.html", "order": 4, "page_file": "docs/about.html"},
    {"title": "Contact", "url": "/contact.html", "order": 5, "page_file": "docs/contact.html"}
]

def get_db():
    db_path = os.path.join(os.path.dirname(__file__), 'forgeweb.db')
    return sqlite3.connect(db_path)

def import_pages_and_nav(conn, base_path):
    cur = conn.cursor()
    # Pages table
    cur.execute('''CREATE TABLE IF NOT EXISTS pages (
        url TEXT PRIMARY KEY,
        title TEXT,
        content TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    # Navigation table
    cur.execute('''CREATE TABLE IF NOT EXISTS navigation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        url TEXT,
        nav_order INTEGER
    )''')
    cur.execute('DELETE FROM navigation')
    for item in NAV_ITEMS:
        # Read page content
        page_path = base_path / item["page_file"]
        if page_path.exists():
            with open(page_path, 'r') as f:
                content = f.read()
        else:
            content = f"<h1>{item['title']}</h1><p>Content not found.</p>"
        # Insert/update page
        cur.execute('INSERT OR REPLACE INTO pages (url, title, content) VALUES (?, ?, ?)',
                    (item['url'], item['title'], content))
        # Insert nav item
        cur.execute('INSERT INTO navigation (title, url, nav_order) VALUES (?, ?, ?)',
                    (item['title'], item['url'], item['order']))
    conn.commit()
    print(f"Navigation and pages updated for {len(NAV_ITEMS)} sections.")

def main():
    base = Path(__file__).parent.parent.parent
    conn = get_db()
    import_pages_and_nav(conn, base)
    conn.close()
    print("All navigation and main pages imported.")

if __name__ == '__main__':
    main()
