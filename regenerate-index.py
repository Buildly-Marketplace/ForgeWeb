#!/usr/bin/env python3
"""
Regenerate index.html with proper static assets and SEO metadata
"""
import json
import os
import shutil
from datetime import datetime

# Paths
script_dir = os.path.dirname(os.path.abspath(__file__))
admin_dir = os.path.join(script_dir, 'admin')
templates_dir = os.path.join(script_dir, 'templates')
assets_dir = os.path.join(script_dir, 'assets')
website_root = os.path.join(os.path.dirname(script_dir), 'website')

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
            'primaryColor': branding_config.get('colors', {}).get('primary', '#1b5fa3'),
            'secondaryColor': branding_config.get('colors', {}).get('secondary', '#144a84'),
            'accentColor': branding_config.get('colors', {}).get('accent', '#f9943b'),
            'font': branding_config.get('typography', {}).get('headingFont', 'Inter')
        }
else:
    branding = site_config.get('branding', {})

# Load base template
base_template_path = os.path.join(templates_dir, 'base.html')
with open(base_template_path, 'r', encoding='utf-8') as f:
    base_template = f.read()

# Generate navigation links
nav_links = []
content_config = site_config.get('content', {})
if content_config.get('include_about'):
    nav_links.append('<a href="about.html" class="text-gray-700 hover:text-primary px-3 py-2 rounded-md text-sm font-medium">About</a>')
if content_config.get('include_services'):
    nav_links.append('<a href="services.html" class="text-gray-700 hover:text-primary px-3 py-2 rounded-md text-sm font-medium">Services</a>')
if content_config.get('include_blog'):
    nav_links.append('<a href="blog.html" class="text-gray-700 hover:text-primary px-3 py-2 rounded-md text-sm font-medium">Blog</a>')
if content_config.get('include_contact'):
    nav_links.append('<a href="contact.html" class="text-gray-700 hover:text-primary px-3 py-2 rounded-md text-sm font-medium">Contact</a>')

# Home page content
home_content = f"""
<div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Features Section -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
        <div class="card-hover bg-white p-8 rounded-xl shadow-md">
            <div class="text-5xl mb-4">🚀</div>
            <h3 class="text-2xl font-bold mb-4 text-gray-900">Fast & Modern</h3>
            <p class="text-gray-600">Built with the latest web technologies for optimal performance and user experience.</p>
        </div>
        <div class="card-hover bg-white p-8 rounded-xl shadow-md">
            <div class="text-5xl mb-4">🎨</div>
            <h3 class="text-2xl font-bold mb-4 text-gray-900">Beautiful Design</h3>
            <p class="text-gray-600">Clean, professional layouts that look great on any device.</p>
        </div>
        <div class="card-hover bg-white p-8 rounded-xl shadow-md">
            <div class="text-5xl mb-4">⚡</div>
            <h3 class="text-2xl font-bold mb-4 text-gray-900">Easy to Use</h3>
            <p class="text-gray-600">Intuitive interface that makes getting started quick and simple.</p>
        </div>
    </div>
    
    <!-- Call to Action -->
    <div class="text-center bg-gradient-to-r from-primary to-secondary rounded-2xl p-12 text-white mb-16">
        <h2 class="text-3xl md:text-4xl font-bold mb-4">Ready to Get Started?</h2>
        <p class="text-xl mb-8 text-blue-100">Join us and start building something amazing today.</p>
        <a href="contact.html" class="inline-block bg-accent hover:bg-opacity-90 text-white font-bold py-4 px-10 rounded-lg transition-all transform hover:scale-105">
            Get in Touch
        </a>
    </div>
</div>
"""

# Replace template variables
replacements = {
    '{{SITE_NAME}}': site_config.get('site', {}).get('name', 'My Website'),
    '{{SITE_DESCRIPTION}}': site_config.get('site', {}).get('description', 'A website built with ForgeWeb'),
    '{{SITE_AUTHOR}}': site_config.get('site', {}).get('author', 'Website Owner'),
    '{{SITE_URL}}': site_config.get('site', {}).get('url', 'https://example.com'),
    '{{BRAND_PRIMARY_COLOR}}': branding.get('primaryColor', '#1b5fa3'),
    '{{BRAND_SECONDARY_COLOR}}': branding.get('secondaryColor', '#144a84'),
    '{{BRAND_ACCENT_COLOR}}': branding.get('accentColor', '#f9943b'),
    '{{TAILWIND_CDN_URL}}': 'https://cdn.tailwindcss.com',
    '{{NAV_LINKS}}': '\n                        '.join(nav_links),
    '{{MOBILE_NAV_LINKS}}': '\n                '.join([link.replace('text-gray-700', 'text-gray-700') for link in nav_links]),
    '{{MAIN_CONTENT}}': home_content,
    '{{FOOTER_LINKS}}': '\n                        '.join([
        '<li><a href="index.html" class="hover:text-accent">Home</a></li>',
        '<li><a href="about.html" class="hover:text-accent">About</a></li>' if content_config.get('include_about') else '',
        '<li><a href="contact.html" class="hover:text-accent">Contact</a></li>' if content_config.get('include_contact') else ''
    ]),
    '{{CURRENT_YEAR}}': str(datetime.now().year),
    '{{GITHUB_REPO}}': 'startupinaday',
    '{{CTA_BUTTONS}}': '<a href="about.html" class="inline-block bg-white text-primary font-bold py-3 px-8 rounded-lg hover:bg-opacity-90 transition-all">Learn More</a>\n                    <a href="contact.html" class="inline-block border-2 border-white text-white font-bold py-3 px-8 rounded-lg hover:bg-white hover:text-primary transition-all">Contact Us</a>'
}

html_content = base_template
for placeholder, value in replacements.items():
    html_content = html_content.replace(placeholder, value)

# Handle conditional logo block
import re
html_content = re.sub(r'\{\{#LOGO_PATH\}\}.*?\{\{/LOGO_PATH\}\}', '', html_content, flags=re.DOTALL)

# Ensure website directories exist
os.makedirs(os.path.join(website_root, 'assets', 'css'), exist_ok=True)
os.makedirs(os.path.join(website_root, 'assets', 'js'), exist_ok=True)
os.makedirs(os.path.join(website_root, 'assets', 'images'), exist_ok=True)

# Write index.html
index_path = os.path.join(website_root, 'index.html')
with open(index_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✓ Generated {index_path}")
print(f"  - Title: {site_config.get('site', {}).get('name', 'My Website')}")
print(f"  - Description: {site_config.get('site', {}).get('description', 'N/A')}")
print(f"  - URL: {site_config.get('site', {}).get('url', 'N/A')}")
print(f"  - Author: {site_config.get('site', {}).get('author', 'N/A')}")
print(f"  - Branding: {branding.get('primaryColor')} / {branding.get('secondaryColor')} / {branding.get('accentColor')}")
print(f"  - Static Assets: assets/css/custom.css, assets/js/site-config.js, assets/js/site.js")
