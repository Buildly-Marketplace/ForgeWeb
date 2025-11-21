#!/usr/bin/env python3
"""
ForgeWeb Database Manager
Simple SQLite database for storing site configuration, content metadata, and settings
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

class ForgeWebDB:
    """Manage ForgeWeb database operations"""
    
    def __init__(self, db_path=None):
        """Initialize database connection"""
        if db_path is None:
            # Get the directory where this script is located (admin/)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(script_dir, 'forgeweb.db')
        self.db_path = db_path
        self.conn = None
        self.initialize_db()
    
    def initialize_db(self):
        """Create database and tables if they don't exist"""
        # Ensure admin directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Access columns by name
        
        cursor = self.conn.cursor()
        
        # Site configuration table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS site_config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Design system configuration
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS design_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                system_name TEXT NOT NULL,
                cdn_urls TEXT NOT NULL,
                body_classes TEXT,
                custom_css TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Pages metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                file_path TEXT NOT NULL,
                template TEXT,
                status TEXT DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                published_at TIMESTAMP
            )
        ''')
        
        # Articles metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                file_path TEXT NOT NULL,
                category TEXT,
                tags TEXT,
                excerpt TEXT,
                author TEXT,
                status TEXT DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                published_at TIMESTAMP
            )
        ''')
        
        # Media/assets tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                mime_type TEXT,
                file_size INTEGER,
                alt_text TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Settings/preferences
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, key)
            )
        ''')
        
        # Navigation items
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS navigation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                position INTEGER DEFAULT 0,
                parent_id INTEGER,
                is_active BOOLEAN DEFAULT 1,
                open_new_tab BOOLEAN DEFAULT 0,
                css_class TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES navigation(id) ON DELETE CASCADE
            )
        ''')
        
        # Branding configuration
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS branding (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                primary_color TEXT DEFAULT '#1b5fa3',
                secondary_color TEXT DEFAULT '#144a84',
                accent_color TEXT DEFAULT '#f9943b',
                dark_color TEXT DEFAULT '#1F2937',
                light_color TEXT DEFAULT '#F3F4F6',
                font_family TEXT DEFAULT 'Inter',
                logo_path TEXT,
                favicon_path TEXT,
                custom_css TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Social media configuration
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS social_media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL UNIQUE,
                handle TEXT,
                url TEXT,
                enabled BOOLEAN DEFAULT 1,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        print("✓ Database initialized")
    
    def get_site_config(self, key, default=None):
        """Get a site configuration value"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT value FROM site_config WHERE key = ?', (key,))
        row = cursor.fetchone()
        if row:
            try:
                return json.loads(row['value'])
            except json.JSONDecodeError:
                return row['value']
        return default
    
    def set_site_config(self, key, value):
        """Set a site configuration value"""
        cursor = self.conn.cursor()
        value_str = json.dumps(value) if not isinstance(value, str) else value
        cursor.execute('''
            INSERT INTO site_config (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = CURRENT_TIMESTAMP
        ''', (key, value_str))
        self.conn.commit()
    
    def get_design_config(self):
        """Get active design system configuration"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM design_config 
            WHERE is_active = 1 
            ORDER BY updated_at DESC 
            LIMIT 1
        ''')
        row = cursor.fetchone()
        if row:
            return {
                'system': row['system_name'],
                'cdn_urls': json.loads(row['cdn_urls']),
                'body_classes': row['body_classes'],
                'custom_css': row['custom_css']
            }
        return None
    
    def set_design_config(self, system_name, cdn_urls, body_classes='', custom_css=''):
        """Set design system configuration"""
        cursor = self.conn.cursor()
        
        # Deactivate current design
        cursor.execute('UPDATE design_config SET is_active = 0')
        
        # Insert new design config
        cursor.execute('''
            INSERT INTO design_config 
            (system_name, cdn_urls, body_classes, custom_css, is_active)
            VALUES (?, ?, ?, ?, 1)
        ''', (system_name, json.dumps(cdn_urls), body_classes, custom_css))
        
        self.conn.commit()
    
    def add_page(self, title, slug, file_path, template='', status='draft'):
        """Add or update a page"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO pages (title, slug, file_path, template, status, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(slug) DO UPDATE SET
                title = excluded.title,
                file_path = excluded.file_path,
                template = excluded.template,
                status = excluded.status,
                updated_at = CURRENT_TIMESTAMP
        ''', (title, slug, file_path, template, status))
        self.conn.commit()
        return cursor.lastrowid
    
    def add_article(self, title, slug, file_path, category='', tags='', excerpt='', author='', status='draft'):
        """Add or update an article"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO articles (title, slug, file_path, category, tags, excerpt, author, status, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(slug) DO UPDATE SET
                title = excluded.title,
                file_path = excluded.file_path,
                category = excluded.category,
                tags = excluded.tags,
                excerpt = excluded.excerpt,
                author = excluded.author,
                status = excluded.status,
                updated_at = CURRENT_TIMESTAMP
        ''', (title, slug, file_path, category, tags, excerpt, author, status))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_all_pages(self):
        """Get all pages"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM pages ORDER BY updated_at DESC')
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all_articles(self):
        """Get all articles"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM articles ORDER BY updated_at DESC')
        return [dict(row) for row in cursor.fetchall()]
    
    def get_setting(self, category, key, default=None):
        """Get a setting value"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE category = ? AND key = ?', (category, key))
        row = cursor.fetchone()
        if row:
            try:
                return json.loads(row['value'])
            except json.JSONDecodeError:
                return row['value']
        return default
    
    def set_setting(self, category, key, value):
        """Set a setting value"""
        cursor = self.conn.cursor()
        value_str = json.dumps(value) if not isinstance(value, str) else value
        cursor.execute('''
            INSERT INTO settings (category, key, value, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(category, key) DO UPDATE SET
                value = excluded.value,
                updated_at = CURRENT_TIMESTAMP
        ''', (category, key, value_str))
        self.conn.commit()
    
    def migrate_from_json(self):
        """Migrate existing JSON configuration to database"""
        import os
        
        # Migrate site-config.json
        site_config_path = 'admin/site-config.json'
        if os.path.exists(site_config_path):
            with open(site_config_path, 'r') as f:
                config = json.load(f)
            
            # Save site info
            if 'site' in config:
                self.set_site_config('site', config['site'])
            
            # Save design config
            if 'design' in config:
                design = config['design']
                self.set_design_config(
                    design.get('system', 'tailwind'),
                    design.get('cdn_urls', []),
                    design.get('body_classes', ''),
                    design.get('custom_css', '')
                )
            
            # Save branding
            if 'branding' in config:
                self.set_site_config('branding', config['branding'])
            
            # Save social
            if 'social' in config:
                self.set_site_config('social', config['social'])
            
            print("✓ Migrated site-config.json to database")
        
        # Migrate branding-config.json
        branding_config_path = 'admin/branding-config.json'
        if os.path.exists(branding_config_path):
            with open(branding_config_path, 'r') as f:
                branding = json.load(f)
            self.set_site_config('branding', branding)
            print("✓ Migrated branding-config.json to database")
    
    
    # Navigation methods
    def get_navigation_items(self, active_only=True):
        """Get all navigation items"""
        cursor = self.conn.cursor()
        query = 'SELECT * FROM navigation'
        if active_only:
            query += ' WHERE is_active = 1'
        query += ' ORDER BY position ASC, id ASC'
        
        cursor.execute(query)
        items = []
        for row in cursor.fetchall():
            items.append({
                'id': row['id'],
                'title': row['title'],
                'url': row['url'],
                'position': row['position'],
                'parent_id': row['parent_id'],
                'is_active': bool(row['is_active']),
                'open_new_tab': bool(row['open_new_tab']),
                'css_class': row['css_class'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            })
        return items
    
    def add_navigation_item(self, title, url, position=0, parent_id=None, 
                           is_active=True, open_new_tab=False, css_class=''):
        """Add a navigation item"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO navigation 
            (title, url, position, parent_id, is_active, open_new_tab, css_class)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, url, position, parent_id, int(is_active), int(open_new_tab), css_class))
        self.conn.commit()
        return cursor.lastrowid
    
    def update_navigation_item(self, nav_id, title=None, url=None, position=None, 
                               parent_id=None, is_active=None, open_new_tab=None, css_class=None):
        """Update a navigation item"""
        cursor = self.conn.cursor()
        updates = []
        values = []
        
        if title is not None:
            updates.append('title = ?')
            values.append(title)
        if url is not None:
            updates.append('url = ?')
            values.append(url)
        if position is not None:
            updates.append('position = ?')
            values.append(position)
        if parent_id is not None:
            updates.append('parent_id = ?')
            values.append(parent_id)
        if is_active is not None:
            updates.append('is_active = ?')
            values.append(int(is_active))
        if open_new_tab is not None:
            updates.append('open_new_tab = ?')
            values.append(int(open_new_tab))
        if css_class is not None:
            updates.append('css_class = ?')
            values.append(css_class)
        
        if updates:
            updates.append('updated_at = CURRENT_TIMESTAMP')
            values.append(nav_id)
            query = f"UPDATE navigation SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)
            self.conn.commit()
            return cursor.rowcount > 0
        return False
    
    def delete_navigation_item(self, nav_id):
        """Delete a navigation item (and its children due to CASCADE)"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM navigation WHERE id = ?', (nav_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def reorder_navigation(self, order_list):
        """
        Reorder navigation items
        order_list: list of tuples [(id, position), ...]
        """
        cursor = self.conn.cursor()
        for nav_id, position in order_list:
            cursor.execute('''
                UPDATE navigation 
                SET position = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (position, nav_id))
        self.conn.commit()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

# Utility functions
def get_db():
    """Get database instance"""
    return ForgeWebDB()

if __name__ == '__main__':
    # Initialize database and migrate from JSON if needed
    print("Initializing ForgeWeb database...")
    db = ForgeWebDB()
    db.migrate_from_json()
    db.close()
    print("✓ Database setup complete")
