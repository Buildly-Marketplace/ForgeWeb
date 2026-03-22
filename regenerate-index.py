#!/usr/bin/env python3
"""
Regenerate site pages with proper NullRecords branding, assets, and SEO metadata.
Outputs to the docs/ directory for GitHub Pages deployment.
"""
import json
import os
import re
import shutil
from datetime import datetime

# Paths
script_dir = os.path.dirname(os.path.abspath(__file__))
admin_dir = os.path.join(script_dir, 'admin')
templates_dir = os.path.join(script_dir, 'templates')
assets_dir = os.path.join(script_dir, 'assets')
website_root = os.path.join(os.path.dirname(script_dir), 'docs')

# Load site configuration
site_config_path = os.path.join(admin_dir, 'site-config.json')
with open(site_config_path, 'r', encoding='utf-8') as f:
    site_config = json.load(f)

# Load branding configuration
branding_config_path = os.path.join(admin_dir, 'branding-config.json')
if os.path.exists(branding_config_path):
    with open(branding_config_path, 'r', encoding='utf-8') as f:
        branding_config = json.load(f)
        branding = {
            'primaryColor': branding_config.get('colors', {}).get('primary', '#00ffff'),
            'secondaryColor': branding_config.get('colors', {}).get('secondary', '#ff5758'),
            'accentColor': branding_config.get('colors', {}).get('accent', '#ED7512'),
            'font': branding_config.get('typography', {}).get('fontFamily', 'Press Start 2P')
        }
else:
    branding = site_config.get('branding', {})

# Load base template
base_template_path = os.path.join(templates_dir, 'base.html')
with open(base_template_path, 'r', encoding='utf-8') as f:
    base_template = f.read()

# Generate navigation links (NullRecords style)
nav_links = []
mobile_nav_links = []
content_config = site_config.get('content', {})

nav_items = []
if content_config.get('include_store'):
    nav_items.append(('store/', 'Store'))
if content_config.get('include_news'):
    nav_items.append(('news/', 'News'))
if content_config.get('include_about'):
    nav_items.append(('about.html', 'About'))
if content_config.get('include_contact'):
    nav_items.append(('contact.html', 'Contact'))

for href, label in nav_items:
    nav_links.append(f'<a href="{href}" class="nav-link px-3 py-2 text-sm font-mono">{label}</a>')
    mobile_nav_links.append(f'<a href="{href}" class="nav-link block px-3 py-2 text-base font-mono">{label}</a>')

# Load home page content template
home_template_path = os.path.join(templates_dir, 'home-content.html')
if os.path.exists(home_template_path):
    with open(home_template_path, 'r', encoding='utf-8') as f:
        home_content = f.read()
else:
    home_content = '<p class="text-gray-400 font-mono text-center">Content coming soon.</p>'

# Replace template variables
replacements = {
    '{{SITE_NAME}}': site_config.get('site', {}).get('name', 'NullRecords'),
    '{{SITE_DESCRIPTION}}': site_config.get('site', {}).get('description', 'NullRecords Art, Music, Publishing and more.'),
    '{{SITE_AUTHOR}}': site_config.get('site', {}).get('author', 'NullRecords'),
    '{{SITE_URL}}': site_config.get('site', {}).get('url', 'https://www.nullrecords.com'),
    '{{BRAND_PRIMARY_COLOR}}': branding.get('primaryColor', '#00ffff'),
    '{{BRAND_SECONDARY_COLOR}}': branding.get('secondaryColor', '#ff5758'),
    '{{BRAND_ACCENT_COLOR}}': branding.get('accentColor', '#ED7512'),
    '{{TAILWIND_CDN_URL}}': 'https://cdn.tailwindcss.com',
    '{{NAV_LINKS}}': '\n                        '.join(nav_links),
    '{{MOBILE_NAV_LINKS}}': '\n                '.join(mobile_nav_links),
    '{{MAIN_CONTENT}}': home_content,
    '{{FOOTER_LINKS}}': '\n                        '.join([
        '<li><a href="index.html" class="hover:text-cyber-blue">Home</a></li>',
        '<li><a href="store/" class="hover:text-cyber-blue">Store</a></li>' if content_config.get('include_store') else '',
        '<li><a href="news/" class="hover:text-cyber-blue">News</a></li>' if content_config.get('include_news') else '',
        '<li><a href="about.html" class="hover:text-cyber-blue">About</a></li>' if content_config.get('include_about') else '',
        '<li><a href="contact.html" class="hover:text-cyber-blue">Contact</a></li>' if content_config.get('include_contact') else ''
    ]),
    '{{CURRENT_YEAR}}': str(datetime.now().year),
    '{{GITHUB_REPO}}': site_config.get('github', {}).get('repo', 'nullrecords-website'),
    '{{CTA_BUTTONS}}': '<a href="store/" class="inline-block bg-cyber-red hover:bg-opacity-80 text-white font-mono py-3 px-8 rounded-lg transition-all">Browse Store</a>\n                    <a href="news/" class="inline-block border-2 border-cyber-blue text-cyber-blue font-mono py-3 px-8 rounded-lg hover:bg-cyber-blue hover:text-dark-bg transition-all">Latest News</a>'
}

html_content = base_template
for placeholder, value in replacements.items():
    html_content = html_content.replace(placeholder, value)

# Handle conditional logo block
html_content = re.sub(r'\{\{#LOGO_PATH\}\}.*?\{\{/LOGO_PATH\}\}', '', html_content, flags=re.DOTALL)

# Ensure output directories exist
os.makedirs(os.path.join(website_root, 'assets', 'css'), exist_ok=True)
os.makedirs(os.path.join(website_root, 'assets', 'js'), exist_ok=True)

# Write index.html
index_path = os.path.join(website_root, 'index.html')
with open(index_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✓ Generated {index_path}")
print(f"  - Title: {site_config.get('site', {}).get('name', 'NullRecords')}")
print(f"  - URL: {site_config.get('site', {}).get('url', 'N/A')}")
print(f"  - Branding: {branding.get('primaryColor')} / {branding.get('secondaryColor')} / {branding.get('accentColor')}")
print(f"  - Font: {branding.get('font')}")
print(f"  - Pages: Home" + 
      (' + Store' if content_config.get('include_store') else '') +
      (' + News' if content_config.get('include_news') else '') +
      (' + About' if content_config.get('include_about') else '') +
      (' + Contact' if content_config.get('include_contact') else ''))

# --- Generate About page ---
if content_config.get('include_about'):
    about_template_path = os.path.join(templates_dir, 'about-content.html')
    if os.path.exists(about_template_path):
        with open(about_template_path, 'r', encoding='utf-8') as f:
            about_content = f.read()
        about_replacements = dict(replacements)
        about_replacements['{{MAIN_CONTENT}}'] = about_content
        about_html = base_template
        for placeholder, value in about_replacements.items():
            about_html = about_html.replace(placeholder, value)
        about_html = re.sub(r'\{\{#LOGO_PATH\}\}.*?\{\{/LOGO_PATH\}\}', '', about_html, flags=re.DOTALL)
        about_path = os.path.join(website_root, 'about.html')
        with open(about_path, 'w', encoding='utf-8') as f:
            f.write(about_html)
        print(f"✓ Generated {about_path}")

# --- Generate Contact page ---
if content_config.get('include_contact'):
    contact_template_path = os.path.join(templates_dir, 'contact-content.html')
    if os.path.exists(contact_template_path):
        with open(contact_template_path, 'r', encoding='utf-8') as f:
            contact_content = f.read()
        contact_replacements = dict(replacements)
        contact_replacements['{{MAIN_CONTENT}}'] = contact_content
        contact_html = base_template
        for placeholder, value in contact_replacements.items():
            contact_html = contact_html.replace(placeholder, value)
        contact_html = re.sub(r'\{\{#LOGO_PATH\}\}.*?\{\{/LOGO_PATH\}\}', '', contact_html, flags=re.DOTALL)
        contact_path = os.path.join(website_root, 'contact.html')
        with open(contact_path, 'w', encoding='utf-8') as f:
            f.write(contact_html)
        print(f"✓ Generated {contact_path}")
