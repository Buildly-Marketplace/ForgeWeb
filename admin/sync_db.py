#!/usr/bin/env python3
"""
Sync ForgeWeb database to match the live NullRecords site and JSON configs.

Fixes: pages, navigation, articles, site_config, design_config, branding,
       social_media, and store_items tables.

Run from the project root:
    python3 forgeweb/admin/sync_db.py
"""
import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = Path(SCRIPT_DIR).parent.parent
DB_PATH = os.path.join(SCRIPT_DIR, 'forgeweb.db')
NOW = datetime.utcnow().isoformat()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def sync_pages(conn):
    """Replace pages with the correct set matching the live site."""
    cur = conn.cursor()

    # The actual pages that exist or should exist in docs/
    pages = [
        {"title": "Home",    "slug": "home",    "file_path": "docs/index.html",       "template": "home-content.html",    "status": "published"},
        {"title": "Store",   "slug": "store",   "file_path": "docs/store/index.html", "template": "store-content.html",   "status": "published"},
        {"title": "News",    "slug": "news",    "file_path": "docs/news/index.html",  "template": "news-content.html",    "status": "published"},
        {"title": "About",   "slug": "about",   "file_path": "docs/about.html",       "template": "about-content.html",   "status": "published"},
        {"title": "Contact", "slug": "contact", "file_path": "docs/contact.html",     "template": "contact-content.html", "status": "published"},
    ]

    cur.execute("DELETE FROM pages")
    for p in pages:
        cur.execute(
            """INSERT INTO pages (title, slug, file_path, template, status, created_at, updated_at, published_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (p["title"], p["slug"], p["file_path"], p["template"], p["status"], NOW, NOW, NOW),
        )
    conn.commit()
    print(f"  pages: {len(pages)} rows (Home, Store, News, About, Contact)")


def sync_navigation(conn):
    """Replace navigation items to match the live site nav."""
    cur = conn.cursor()

    nav_items = [
        {"title": "Home",    "url": "/",            "position": 1, "css_class": "nav-link"},
        {"title": "Store",   "url": "/store/",      "position": 2, "css_class": "nav-link"},
        {"title": "News",    "url": "/news/",       "position": 3, "css_class": "nav-link"},
        {"title": "About",   "url": "/about.html",  "position": 4, "css_class": "nav-link"},
        {"title": "Contact", "url": "/contact.html", "position": 5, "css_class": "nav-link"},
    ]

    cur.execute("DELETE FROM navigation")
    for n in nav_items:
        cur.execute(
            """INSERT INTO navigation (title, url, position, parent_id, is_active, open_new_tab, css_class, created_at, updated_at)
               VALUES (?, ?, ?, NULL, 1, 0, ?, ?, ?)""",
            (n["title"], n["url"], n["position"], n["css_class"], NOW, NOW),
        )
    conn.commit()
    print(f"  navigation: {len(nav_items)} rows (Home, Store, News, About, Contact)")


def sync_articles(conn):
    """Populate articles table with the real content pages (About, Contact)."""
    cur = conn.cursor()
    cur.execute("DELETE FROM articles")

    articles = [
        {
            "title": "About NullRecords",
            "slug": "about",
            "file_path": "docs/about.html",
            "category": "page",
            "tags": json.dumps(["about", "nullrecords", "music-label"]),
            "excerpt": "NullRecords: DRM-free, lossless music. Own your music, don't just rent it.",
            "author": "NullRecords",
            "status": "published",
        },
        {
            "title": "Contact NullRecords",
            "slug": "contact",
            "file_path": "docs/contact.html",
            "category": "page",
            "tags": json.dumps(["contact", "nullrecords"]),
            "excerpt": "Get in touch with NullRecords for music, publishing, and collaboration inquiries.",
            "author": "NullRecords",
            "status": "published",
        },
    ]

    for a in articles:
        cur.execute(
            """INSERT INTO articles (title, slug, file_path, category, tags, excerpt, author, status, created_at, updated_at, published_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (a["title"], a["slug"], a["file_path"], a["category"], a["tags"],
             a["excerpt"], a["author"], a["status"], NOW, NOW, NOW),
        )
    conn.commit()
    print(f"  articles: {len(articles)} rows (About, Contact)")


def sync_site_config(conn):
    """Re-import site_config from the current site-config.json."""
    config_path = os.path.join(SCRIPT_DIR, "site-config.json")
    with open(config_path, "r") as f:
        config = json.load(f)

    cur = conn.cursor()

    # Upsert each top-level section
    sections = ["site", "design", "content", "branding", "social", "features",
                 "support", "buildly", "development", "github", "music"]
    for key in sections:
        if key in config:
            val = json.dumps(config[key])
            cur.execute(
                """INSERT INTO site_config (key, value, updated_at)
                   VALUES (?, ?, CURRENT_TIMESTAMP)
                   ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP""",
                (key, val),
            )

    conn.commit()
    print(f"  site_config: {len([k for k in sections if k in config])} keys synced from site-config.json")


def sync_design_config(conn):
    """Set single active design_config row for cyberpunk theme."""
    cur = conn.cursor()
    cur.execute("UPDATE design_config SET is_active = 0")
    cur.execute(
        """INSERT INTO design_config (system_name, cdn_urls, body_classes, custom_css, is_active)
           VALUES (?, ?, ?, ?, 1)""",
        ("tailwind", json.dumps(["https://cdn.tailwindcss.com"]), "bg-dark-bg", "", ),
    )
    conn.commit()
    print("  design_config: active row set to bg-dark-bg (cyberpunk)")


def sync_branding(conn):
    """Populate branding table with cyberpunk color palette."""
    cur = conn.cursor()
    cur.execute("DELETE FROM branding")
    cur.execute(
        """INSERT INTO branding (primary_color, secondary_color, accent_color, dark_color, light_color, font_family, logo_path, favicon_path, custom_css)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        ("#00ffff", "#ff5758", "#ED7512", "#0a0a0a", "#1a1a1a",
         "Press Start 2P", None, None, ""),
    )
    conn.commit()
    print("  branding: cyberpunk palette (#00ffff / #ff5758 / #ED7512)")


def sync_social_media(conn):
    """Populate social_media table with actual NullRecords platforms."""
    cur = conn.cursor()
    cur.execute("DELETE FROM social_media")

    platforms = [
        {"platform": "spotify",      "handle": "My Evil Robot Army", "url": "https://open.spotify.com/artist/4PBJ1WON6gmxC1L35HHh69"},
        {"platform": "apple_music",  "handle": "My Evil Robot Army", "url": "https://music.apple.com/us/artist/my-evil-robot-army/1576251082"},
        {"platform": "bandcamp",     "handle": "nullrecords",       "url": "https://nullrecords.bandcamp.com"},
        {"platform": "youtube",      "handle": "NullRecords",       "url": "https://www.youtube.com/@nullrecords"},
        {"platform": "printify",     "handle": "NullRecords Merch", "url": "https://nullrecords.printify.me/"},
    ]

    for p in platforms:
        cur.execute(
            """INSERT INTO social_media (platform, handle, url, enabled)
               VALUES (?, ?, ?, 1)""",
            (p["platform"], p["handle"], p["url"]),
        )
    conn.commit()
    print(f"  social_media: {len(platforms)} platforms")


def sync_store_items(conn):
    """Create and populate store_items table from store_items.json."""
    store_path = os.path.join(SCRIPT_DIR, "store_items.json")
    if not os.path.exists(store_path):
        store_path = str(PROJECT_ROOT / "docs" / "store" / "store_items.json")

    with open(store_path, "r") as f:
        items = json.load(f)

    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS store_items (
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
        download_bundle TEXT,
        play_now INTEGER DEFAULT 0,
        active INTEGER DEFAULT 1,
        streaming_links TEXT
    )""")

    cur.execute("DELETE FROM store_items")
    for item in items:
        cur.execute(
            """INSERT INTO store_items (id, type, title, artist, author, cover_art, audio_files, ebook_file,
                                        description, suggested_donation, download_bundle, play_now, active, streaming_links)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                item.get("id"), item.get("type"), item.get("title"),
                item.get("artist"), item.get("author"), item.get("cover_art"),
                json.dumps(item.get("audio_files")), item.get("ebook_file"),
                item.get("description"), item.get("suggested_donation"),
                item.get("download_bundle"),
                int(item.get("play_now", False)),
                int(item.get("active", True)),
                json.dumps(item.get("streaming_links")) if item.get("streaming_links") else None,
            ),
        )
    conn.commit()
    print(f"  store_items: {len(items)} items")


def main():
    print(f"Syncing ForgeWeb database: {DB_PATH}")
    print(f"Project root: {PROJECT_ROOT}\n")

    conn = get_db()

    sync_pages(conn)
    sync_navigation(conn)
    sync_articles(conn)
    sync_site_config(conn)
    sync_design_config(conn)
    sync_branding(conn)
    sync_social_media(conn)
    sync_store_items(conn)

    conn.close()
    print("\nSync complete.")


if __name__ == "__main__":
    main()
