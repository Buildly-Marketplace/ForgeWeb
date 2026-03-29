#!/usr/bin/env python3
"""
ForgeWeb Local Server
Enhanced server for the admin interface with site generation and preview capabilities.
"""

import json
import os
import sys
import shutil
import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote
from datetime import datetime
import threading
import argparse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

# Import database
try:
    from database import ForgeWebDB
    db = ForgeWebDB()
    print("✓ Database connected")
except Exception as e:
    print(f"⚠️  Database initialization failed: {e}")
    db = None

try:
    import requests
except ImportError:
    requests = None
    print("⚠️  requests library not installed. GitHub integration will be limited.")

try:
    from dotenv import load_dotenv
    # Load environment variables from .env file
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✓ Loaded environment variables from {env_path}")
except ImportError:
    load_dotenv = None
    print("⚠️  python-dotenv not installed. Using system environment variables only.")

class ForgeWebHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.admin_dir = os.path.dirname(os.path.abspath(__file__))
        # ForgeWeb directory (parent of admin/)
        forge_web_dir = os.path.dirname(self.admin_dir)
        # GitHub Pages repo root (parent of ForgeWeb/)
        
        # Initialize Jinja2 template environment
        template_dir = os.path.join(self.admin_dir, 'templates')
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
        repo_root = os.path.dirname(forge_web_dir)

        # GitHub Pages branch deploys expect site content in `docs/`.
        # Always use `docs/` as the website root (create it if missing).
        self.website_root = os.path.join(repo_root, 'docs')
        os.makedirs(self.website_root, exist_ok=True)

        # Create expected docs subdirectories if they are missing
        os.makedirs(os.path.join(self.website_root, 'articles'), exist_ok=True)
        os.makedirs(os.path.join(self.website_root, 'assets', 'css'), exist_ok=True)
        os.makedirs(os.path.join(self.website_root, 'assets', 'images'), exist_ok=True)
        
        # Initialize repo with .gitignore if it doesn't exist
        self._initialize_repo()
        
        super().__init__(*args, **kwargs)
    
    def _initialize_repo(self):
        """Initialize GitHub Pages repository with .gitignore"""
        repo_root = os.path.dirname(os.path.dirname(self.admin_dir))
        gitignore_path = os.path.join(repo_root, '.gitignore')
        
        if not os.path.exists(gitignore_path):
            gitignore_content = """# ForgeWeb GitHub Pages Repository
# Only the docs/ folder gets deployed to GitHub Pages

# ForgeWeb admin tools (not deployed)
ForgeWeb/

# Database and config (local only)
*.db
*.sqlite
*.sqlite3
admin/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
venv/
env/
.venv/
.env
.env.local

# OS Files
.DS_Store
Thumbs.db
*.swp
*.swo
*~

# Editor files
.vscode/
.idea/
*.sublime-project
*.sublime-workspace

# Temporary files
*.tmp
*.bak
*.cache
.pytest_cache/
*.log
"""
            with open(gitignore_path, 'w') as f:
                f.write(gitignore_content)
            print(f"✓ Created .gitignore in repository root")
            print(f"  └─ ForgeWeb/ and admin files will not be committed")
    
    def load_branding_config(self):
        """Load branding configuration from site-config.json and branding-config.json"""
        branding = {
            'primaryColor': '#1b5fa3',
            'secondaryColor': '#144a84',
            'accentColor': '#f9943b',
            'darkColor': '#1F2937',
            'lightColor': '#F3F4F6',
            'font': 'Inter'
        }
        
        # Load from site-config.json
        site_config_path = os.path.join(self.admin_dir, 'site-config.json')
        if os.path.exists(site_config_path):
            try:
                with open(site_config_path, 'r', encoding='utf-8') as f:
                    site_config = json.load(f)
                    if 'branding' in site_config:
                        branding.update(site_config['branding'])
            except Exception as e:
                print(f"Warning: Could not load site-config.json: {e}")
        
        # Load from branding-config.json (takes precedence)
        branding_config_path = os.path.join(self.admin_dir, 'branding-config.json')
        if os.path.exists(branding_config_path):
            try:
                with open(branding_config_path, 'r', encoding='utf-8') as f:
                    branding_config = json.load(f)
                    if 'colors' in branding_config:
                        colors = branding_config['colors']
                        if 'primary' in colors:
                            branding['primaryColor'] = colors['primary']
                        if 'secondary' in colors:
                            branding['secondaryColor'] = colors['secondary']
                    if 'typography' in branding_config:
                        typography = branding_config['typography']
                        if 'headingFont' in typography:
                            branding['font'] = typography['headingFont']
            except Exception as e:
                print(f"Warning: Could not load branding-config.json: {e}")
        
        return branding
    
    def get_config_value(self, key, default=None):
        """Get configuration value from environment or config file"""
        # First check environment variables
        env_value = os.getenv(key)
        if env_value is not None:
            return env_value
        
        # Then check site config
        config_path = os.path.join(self.admin_dir, 'site-config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return config.get(key.lower(), default)
            except:
                pass
        
        return default

    def do_GET(self):
        """Handle GET requests for both admin and preview"""
        parsed_path = urlparse(self.path)
        
        # Handle /admin redirect (without trailing slash)
        if self.path == '/admin':
            self.send_response(301)
            self.send_header('Location', '/admin/')
            self.end_headers()
            return
        
        if self.path.startswith('/admin/'):
            # Serve admin files
            self.serve_admin_file(parsed_path.path)
        elif self.path.startswith('/preview/'):
            # Serve preview of generated site
            preview_path = self.path.replace('/preview/', '')
            self.serve_preview_file(preview_path)
        elif self.path.startswith('/api/'):
            # Handle API requests
            self.handle_api_get_request()
        else:
            # Serve generated site files (main website)
            self.serve_site_file(parsed_path.path)

    def do_POST(self):
        """Handle POST requests for API endpoints"""
        if self.path == '/api/save-file':
            self.handle_save_file()
        elif self.path == '/api/create-preview':
            self.handle_create_preview()
        elif self.path == '/api/upload':
            self.handle_upload()
        elif self.path == '/api/ai-generate':
            self.handle_ai_generate()
        elif self.path == '/api/setup-site' or self.path == '/api/site-setup':
            self.handle_setup_site()
        elif self.path == '/api/design-system':
            self.handle_design_system()
        elif self.path == '/api/branding':
            self.handle_branding_request()
        elif self.path == '/api/social-accounts':
            self.handle_social_accounts()
        elif self.path == '/api/settings':
            self.handle_settings()
        elif self.path == '/api/import-html':
            self.handle_html_import()
        elif self.path == '/api/navigation':
            self.handle_navigation_add()
        elif self.path.startswith('/api/navigation/'):
            self.handle_navigation_update()
        elif self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            self.send_error(404, "API endpoint not found")
    
    def do_PUT(self):
        """Handle PUT requests for updates"""
        if self.path.startswith('/api/navigation/'):
            self.handle_navigation_update()
        else:
            self.send_error(404, "API endpoint not found")
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        if self.path.startswith('/api/navigation/'):
            self.handle_navigation_delete()
        else:
            self.send_error(404, "API endpoint not found")

    def render_template(self, template_name, **context):
        """Render a Jinja2 template with context"""
        try:
            template = self.jinja_env.get_template(template_name)
            html = template.render(**context)
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
            return True
        except TemplateNotFound:
            self.send_error(404, f"Template not found: {template_name}")
            return False
        except Exception as e:
            self.send_error(500, f"Template error: {str(e)}")
            return False
    
    def serve_admin_file(self, path):
        """Serve admin interface files with template support"""
        # Remove /admin/ prefix
        file_path = path[7:] if path.startswith('/admin/') else path
        
        if not file_path or file_path == '/':
            file_path = 'index.html'
        
        # Map URLs to template files - ALL admin pages use templates now
        template_pages = {
            'index.html': 'dashboard.html',
            'site-setup.html': 'site-setup.html',
            'design-chooser.html': 'design-chooser.html',
            'branding-manager.html': 'branding-manager.html',
            'navigation-manager.html': 'navigation-manager.html',
            'page-editor.html': 'page-editor.html',
            'editor.html': 'editor.html',
            'articles-manager.html': 'articles-manager.html',
            'html-import.html': 'html-import.html',
            'media-library.html': 'media-library.html',
            'settings.html': 'settings.html',
            'social.html': 'social.html'
        }
        
        if file_path in template_pages:
            # Use template rendering
            context = self.get_template_context()
            context['current_page'] = file_path.replace('.html', '')
            
            if self.render_template(template_pages[file_path], **context):
                return
        
        # Fall back to serving static files (CSS, JS, images, etc.)
        full_path = os.path.join(self.admin_dir, file_path)
        
        if os.path.exists(full_path) and os.path.isfile(full_path):
            self.serve_file(full_path)
        else:
            self.send_error(404, f"Admin file not found: {file_path}")
    
    def get_template_context(self):
        """Get common context for all templates"""
        context = {
            'site_name': 'ForgeWeb',
            'version': '2.0',
            'current_year': datetime.now().year,
            'page_count': 0,
            'article_count': 0,
            'nav_count': 0,
            'branding': {}
        }
        
        # Add site config and counts if available
        if db:
            # Load common site settings
            site_name = db.get_site_config('site_name')
            if site_name:
                context['site_name'] = site_name
            
            site_config = db.get_site_config('site')
            if isinstance(site_config, dict):
                context['site_name'] = site_config.get('name', context['site_name'])
                context['site_url'] = site_config.get('url', '')
            
            site_url = db.get_site_config('site_url')
            if site_url:
                context['site_url'] = site_url
            
            # Load branding for templates
            try:
                branding_data = db.get_site_config('branding')
                if isinstance(branding_data, dict):
                    context['branding'] = {
                        'primary_color': branding_data.get('primaryColor', ''),
                        'secondary_color': branding_data.get('secondaryColor', ''),
                        'accent_color': branding_data.get('accentColor', ''),
                    }
            except Exception:
                pass
            
            # Load counts for dashboard
            try:
                pages = db.get_all_pages()
                context['page_count'] = len(pages) if pages else 0
            except Exception:
                pass
            try:
                articles = db.get_all_articles()
                context['article_count'] = len(articles) if articles else 0
            except Exception:
                pass
            try:
                nav_items = db.get_navigation_items(active_only=False)
                context['nav_count'] = len(nav_items) if nav_items else 0
            except Exception:
                pass
        
        return context

    def serve_site_file(self, path):
        """Serve generated site files, mapping directory requests to index.html"""
        if not path or path == '/':
            path = 'index.html'
        elif path.startswith('/'):
            path = path[1:]

        # If path ends with '/', treat as directory and append 'index.html'
        if path.endswith('/') or (os.path.isdir(os.path.join(self.website_root, path))):
            path = os.path.join(path, 'index.html')

        full_path = os.path.join(self.website_root, path)

        if os.path.exists(full_path) and os.path.isfile(full_path):
            self.serve_file(full_path)
        else:
            # Try to serve 404.html if it exists
            error_404_path = os.path.join(self.website_root, '404.html')
            if os.path.exists(error_404_path):
                self.send_response(404)
                self.serve_file(error_404_path, send_response=False)
            else:
                self.send_error(404, f"Page not found: {path}")

    def serve_preview_file(self, path):
        """Serve preview files (same as site files but with different URL structure)"""
        self.serve_site_file(path)

    def serve_file(self, file_path, send_response=True):
        """Serve a file with appropriate headers"""
        try:
            # Determine content type
            content_type = self.get_content_type(file_path)
            
            if send_response:
                self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
                
        except Exception as e:
            print(f"Error serving file {file_path}: {e}")
            if send_response:
                self.send_error(500, "Internal server error")

    def get_content_type(self, file_path):
        """Get content type based on file extension"""
        ext = os.path.splitext(file_path)[1].lower()
        content_types = {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon',
            '.txt': 'text/plain',
            '.xml': 'application/xml',
        }
        return content_types.get(ext, 'application/octet-stream')

    def handle_create_preview(self):
        """Handle preview creation - writes temp HTML to a preview file"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            content = data.get('content', '')
            filename = data.get('filename', 'preview.html')

            # Write to a temp preview file in the website root
            preview_dir = os.path.join(self.website_root, '_preview')
            os.makedirs(preview_dir, exist_ok=True)
            preview_file = os.path.join(preview_dir, 'index.html')

            with open(preview_file, 'w', encoding='utf-8') as f:
                f.write(content)

            self.send_json_response({
                'success': True,
                'previewFile': '_preview/index.html'
            })
        except Exception as e:
            print(f'Preview error: {e}')
            self.send_json_error(500, str(e))

    # ── File Upload ────────────────────────────────────────

    def handle_upload(self):
        """Handle multipart file upload to assets/uploads/"""
        import cgi
        import io
        try:
            content_type = self.headers.get('Content-Type', '')
            if 'multipart/form-data' not in content_type:
                self.send_json_error(400, 'Expected multipart/form-data')
                return

            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            # Parse multipart data
            boundary = content_type.split('boundary=')[-1].encode()
            environ = {
                'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': content_type,
                'CONTENT_LENGTH': str(content_length),
            }
            fs = cgi.FieldStorage(
                fp=io.BytesIO(body),
                environ=environ,
                keep_blank_values=True,
            )

            file_item = fs['file'] if 'file' in fs else None
            if file_item is None or not file_item.filename:
                self.send_json_error(400, 'No file provided')
                return

            # Sanitize filename
            original = os.path.basename(file_item.filename)
            safe_name = original.replace(' ', '_')
            for ch in ['..', '/', '\\', '\x00']:
                safe_name = safe_name.replace(ch, '')

            # Allowed extensions
            allowed_ext = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp',
                           '.ico', '.mp3', '.mp4', '.pdf', '.css', '.js', '.woff', '.woff2'}
            ext = os.path.splitext(safe_name)[1].lower()
            if ext not in allowed_ext:
                self.send_json_error(400, f'File type {ext} not allowed')
                return

            upload_dir = os.path.join(self.website_root, 'assets', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)

            dest = os.path.join(upload_dir, safe_name)
            # Avoid overwriting — append timestamp if exists
            if os.path.exists(dest):
                stem, extension = os.path.splitext(safe_name)
                safe_name = f"{stem}_{int(datetime.now().timestamp())}{extension}"
                dest = os.path.join(upload_dir, safe_name)

            file_data = file_item.file.read()
            with open(dest, 'wb') as f:
                f.write(file_data)

            rel_path = f'assets/uploads/{safe_name}'

            # Track in database
            if db:
                try:
                    mime = self.guess_type_for_ext(ext)
                    db.execute(
                        'INSERT INTO media (filename, file_path, mime_type, file_size) VALUES (?, ?, ?, ?)',
                        (safe_name, rel_path, mime, len(file_data))
                    )
                except Exception:
                    pass

            self.send_json_response({
                'success': True,
                'filename': safe_name,
                'path': rel_path,
                'url': f'/{rel_path}',
                'size': len(file_data)
            })
            print(f"✓ Uploaded: {rel_path} ({len(file_data)} bytes)")

        except Exception as e:
            print(f"✗ Upload error: {e}")
            self.send_json_error(500, str(e))

    def guess_type_for_ext(self, ext):
        types = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                 '.gif': 'image/gif', '.svg': 'image/svg+xml', '.webp': 'image/webp',
                 '.ico': 'image/x-icon', '.mp3': 'audio/mpeg', '.mp4': 'video/mp4',
                 '.pdf': 'application/pdf', '.css': 'text/css', '.js': 'application/javascript',
                 '.woff': 'font/woff', '.woff2': 'font/woff2'}
        return types.get(ext, 'application/octet-stream')

    # ── AI Generation ──────────────────────────────────────

    def _get_ai_provider_config(self):
        """Read AI provider config from the settings stored in localStorage-style JSON or DB."""
        config = {'providers': {}, 'active': None}
        if db:
            try:
                row = db.get_site_config('ai_providers')
                if row:
                    config['providers'] = row
                    for name, prov in row.items():
                        if prov.get('enabled'):
                            config['active'] = name
                            break
            except Exception:
                pass
        return config

    def handle_ai_generate(self):
        """Proxy prompt to configured AI provider and return result."""
        try:
            content_length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(content_length).decode('utf-8'))

            prompt = data.get('prompt', '')
            context_html = data.get('context', '')
            provider = data.get('provider', 'ollama')
            endpoint = data.get('endpoint', '')
            model = data.get('model', '')
            api_key = data.get('apiKey', '')

            if not prompt:
                self.send_json_error(400, 'Missing prompt')
                return

            system_msg = (
                "You are an expert web developer assistant embedded in a page editor. "
                "The user is editing an HTML page. Return ONLY the HTML code they asked for, "
                "no markdown fences, no explanations — just the raw HTML snippet. "
                "Use the same CSS framework/classes present in the current page."
            )
            if context_html:
                system_msg += f"\n\nCurrent page HTML (truncated):\n{context_html[:3000]}"

            result = None

            if provider == 'ollama':
                ep = endpoint or 'http://localhost:11434'
                mdl = model or 'llama3'
                result = self._call_ollama(ep, mdl, system_msg, prompt)
            elif provider == 'openai':
                ep = endpoint or 'https://api.openai.com/v1'
                mdl = model or 'gpt-3.5-turbo'
                if not api_key:
                    self.send_json_error(400, 'OpenAI API key not configured')
                    return
                result = self._call_openai(ep, mdl, api_key, system_msg, prompt)
            elif provider == 'gemini':
                mdl = model or 'gemini-pro'
                if not api_key:
                    self.send_json_error(400, 'Gemini API key not configured')
                    return
                result = self._call_gemini(api_key, mdl, system_msg, prompt)
            else:
                self.send_json_error(400, f'Unknown provider: {provider}')
                return

            if result is None:
                self.send_json_error(502, 'AI provider returned no response')
                return

            self.send_json_response({'success': True, 'code': result})

        except Exception as e:
            print(f"AI generate error: {e}")
            self.send_json_error(500, str(e))

    def _call_ollama(self, endpoint, model, system_msg, prompt):
        """Call Ollama /api/chat endpoint."""
        import urllib.request
        url = f"{endpoint.rstrip('/')}/api/chat"
        payload = json.dumps({
            'model': model,
            'messages': [
                {'role': 'system', 'content': system_msg},
                {'role': 'user', 'content': prompt}
            ],
            'stream': False
        }).encode()
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = json.loads(resp.read().decode())
                return body.get('message', {}).get('content', '')
        except Exception as e:
            print(f"Ollama error: {e}")
            return None

    def _call_openai(self, endpoint, model, api_key, system_msg, prompt):
        """Call OpenAI-compatible /chat/completions endpoint."""
        import urllib.request
        url = f"{endpoint.rstrip('/')}/chat/completions"
        payload = json.dumps({
            'model': model,
            'messages': [
                {'role': 'system', 'content': system_msg},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.7
        }).encode()
        req = urllib.request.Request(url, data=payload, headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        })
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = json.loads(resp.read().decode())
                return body['choices'][0]['message']['content']
        except Exception as e:
            print(f"OpenAI error: {e}")
            return None

    def _call_gemini(self, api_key, model, system_msg, prompt):
        """Call Google Gemini generateContent endpoint."""
        import urllib.request
        url = f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent?key={api_key}"
        payload = json.dumps({
            'contents': [{'parts': [{'text': f"{system_msg}\n\n{prompt}"}]}]
        }).encode()
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = json.loads(resp.read().decode())
                return body['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            print(f"Gemini error: {e}")
            return None

    def handle_save_file(self):
        """Handle file save requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            file_path = data.get('path') or data.get('file')
            file_content = data.get('content')
            
            if not file_path or file_content is None:
                self.send_json_error(400, "Missing path or content")
                return
            
            # Clean and validate path
            clean_path = self.clean_path(file_path)
            full_path = os.path.join(self.website_root, clean_path)
            
            # Ensure directory exists
            dir_path = os.path.dirname(full_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            
            # Write file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            response = {
                'success': True,
                'message': f'File saved to {clean_path}',
                'path': clean_path,
                'size': len(file_content)
            }
            
            self.send_json_response(response)
            print(f"✓ Saved: {clean_path} ({len(file_content)} bytes)")
            
        except Exception as e:
            print(f"✗ Save error: {e}")
            self.send_json_error(500, str(e))

    def handle_setup_site(self):
        """Handle site setup requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Handle both action-based and direct data formats
            action = data.get('action')
            site_data = data.get('data', data)  # Use data directly if no action
            
            if action == 'update-config' or not action:
                result = self.update_site_config(site_data)
            elif action == 'generate-site':
                result = self.generate_site_files(site_data)
            elif action == 'create-github-repo':
                result = self.create_github_repo(site_data)
            else:
                # Handle direct site configuration without action
                result = self.update_site_config(site_data)
                
            self.send_json_response(result)
            
        except Exception as e:
            print(f"✗ Setup error: {e}")
            self.send_json_error(500, str(e))

    def handle_design_system(self):
        """Handle design system configuration"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            system_name = data.get('system', 'tailwind')
            cdn_urls = data.get('cdn_urls', [])
            body_classes = data.get('body_classes', '')
            custom_css = data.get('custom_css', '')
            
            # Save to database if available
            if db:
                db.set_design_config(system_name, cdn_urls, body_classes, custom_css)
            
            # Also save to JSON for backward compatibility
            config_path = os.path.join(self.admin_dir, 'site-config.json')
            config = {}
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
            
            config['design'] = {
                'system': system_name,
                'cdn_urls': cdn_urls,
                'custom_css': custom_css,
                'body_classes': body_classes
            }
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            response = {
                'success': True,
                'message': f'Design system set to {system_name}',
                'design': config['design']
            }
            
            self.send_json_response(response)
            print(f"✓ Design system configured: {system_name}")
            
        except Exception as e:
            print(f"✗ Design system error: {e}")
            self.send_json_error(500, str(e))

    def handle_api_get_request(self):
        """Handle GET API requests"""
        try:
            if self.path == '/api/navigation':
                # Get all navigation items
                if not db:
                    self.send_json_error(500, 'Database not available')
                    return
                
                nav_items = db.get_navigation_items(active_only=False)
                self.send_json_response({'navigation': nav_items})
            elif self.path == '/api/articles-list':
                # Get all articles
                if not db:
                    self.send_json_error(500, 'Database not available')
                    return
                articles = db.get_all_articles()
                self.send_json_response({'articles': articles})
            elif self.path == '/api/branding':
                branding_config = self.load_branding_config()
                self.send_json_response(branding_config)
            elif self.path == '/api/design-system':
                # Return design system configuration
                config_path = os.path.join(self.admin_dir, 'site-config.json')
                design_config = {}
                if os.path.exists(config_path):
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        design_config = config.get('design', {})
                
                # Also try to get from database
                if db and not design_config:
                    db_config = db.get_design_config()
                    if db_config:
                        design_config = db_config
                
                self.send_json_response({'design': design_config})
            elif self.path == '/api/site-status':
                # Check if user has created their homepage
                homepage_path = os.path.join(self.website_root, 'index.html')
                has_homepage = os.path.exists(homepage_path)
                self.send_json_response({
                    'status': 'running',
                    'admin_url': '/admin/',
                    'website_root': self.website_root,
                    'has_homepage': has_homepage
                })
            elif self.path == '/api/preview-url':
                self.send_json_response({'preview_url': f'http://localhost:{self.server.server_port}/'})
            elif self.path.startswith('/api/load-file?'):
                # Load a file from the website directory
                parsed = urlparse(self.path)
                params = parse_qs(parsed.query)
                filename = params.get('file', [''])[0]
                
                if not filename:
                    self.send_json_error(400, 'Missing file parameter')
                    return
                
                # Security: prevent directory traversal
                if '..' in filename or filename.startswith('/'):
                    self.send_json_error(403, 'Invalid file path')
                    return
                
                file_path = os.path.join(self.website_root, filename)
                
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.send_json_response({'content': content, 'filename': filename})
                else:
                    self.send_json_error(404, f'File not found: {filename}')
            elif self.path == '/api/list-html-files':
                # List all HTML files in the website directory
                files = []
                
                if os.path.exists(self.website_root):
                    for root, dirs, filenames in os.walk(self.website_root):
                        for filename in filenames:
                            if filename.endswith('.html'):
                                # Get relative path from website root
                                full_path = os.path.join(root, filename)
                                rel_path = os.path.relpath(full_path, self.website_root)
                                
                                # Try to extract page title from HTML
                                description = rel_path
                                try:
                                    with open(full_path, 'r', encoding='utf-8') as f:
                                        content = f.read(2000)  # Read first 2000 chars
                                        import re
                                        title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
                                        if title_match:
                                            description = title_match.group(1).strip()
                                except:
                                    pass
                                
                                files.append({
                                    'filename': rel_path,
                                    'description': description
                                })
                
                self.send_json_response({'files': files})
            elif self.path == '/api/site-config' or self.path == '/api/site-setup-data':
                # Load site configuration from database only
                site_config = {}
                
                if db:
                    # Load from database
                    site_data = db.get_site_config('site')
                    github_data = db.get_site_config('github')
                    content_data = db.get_site_config('content')
                    
                    if site_data:
                        site_config['site'] = site_data
                    if github_data:
                        site_config['github'] = github_data
                    if content_data:
                        site_config['content'] = content_data
                
                # Return config (empty if nothing in database)
                self.send_json_response({'config': site_config})
            
            elif self.path == '/api/social-accounts':
                # Return social media accounts configuration
                social_config = self.load_social_accounts()
                self.send_json_response(social_config)
            
            elif self.path == '/api/settings':
                # Return app settings
                settings = self.load_settings()
                self.send_json_response(settings)
            
            elif self.path == '/api/media':
                # List uploaded media files
                media_dir = os.path.join(self.website_root, 'assets', 'uploads')
                files = []
                if os.path.isdir(media_dir):
                    for fname in sorted(os.listdir(media_dir)):
                        fpath = os.path.join(media_dir, fname)
                        if os.path.isfile(fpath):
                            files.append({
                                'filename': fname,
                                'path': f'assets/uploads/{fname}',
                                'url': f'/assets/uploads/{fname}',
                                'size': os.path.getsize(fpath)
                            })
                self.send_json_response({'files': files})
            
            elif self.path == '/api/ai-status':
                # Return configured AI providers and their status
                self.send_json_response(self._get_ai_provider_config())
            
            else:
                endpoint = self.path.replace('/api/', '')
                self.send_json_error(404, f"API endpoint not found: {endpoint}")
                
        except Exception as e:
            self.send_json_error(500, str(e))

    def handle_api_request(self):
        """Handle other API requests"""
        try:
            # Parse the API endpoint
            endpoint = self.path.replace('/api/', '')
            
            if endpoint == 'site-status':
                self.send_json_response({'status': 'running', 'admin_url': '/admin/'})
            elif endpoint == 'preview-url':
                self.send_json_response({'preview_url': f'http://localhost:{self.server.server_port}/'})
            else:
                self.send_json_error(404, f"API endpoint not found: {endpoint}")
                
        except Exception as e:
            self.send_json_error(500, str(e))

    def update_site_config(self, site_data):
        """Update site configuration"""
        config_path = os.path.join(self.admin_dir, 'site-config.json')
        
        # Load existing config
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Update config with new data
        config.update({
            'site': {
                'name': site_data.get('siteName', 'My Website'),
                'url': f"https://{site_data.get('githubUsername', 'username')}.github.io/{site_data.get('githubRepo', 'repository')}",
                'description': site_data.get('siteDescription', 'A website built with ForgeWeb'),
                'author': site_data.get('siteAuthor', 'Website Owner'),
                'generator': 'ForgeWeb v1.0.0',
                'support_url': 'https://docs.buildly.io/forgeweb'
            },
            'github': {
                'username': site_data.get('githubUsername', ''),
                'repo': site_data.get('githubRepo', ''),  # Changed from 'repository' to 'repo'
                'pages_enabled': True
            },
            'content': {
                'site_type': site_data.get('siteType', 'blog'),
                'include_about': site_data.get('includeAbout', True),
                'include_contact': site_data.get('includeContact', True),
                'include_blog': site_data.get('includeBlog', True),
                'include_portfolio': site_data.get('includePortfolio', False),
                'include_services': site_data.get('includeServices', False),
                'include_sample_content': site_data.get('includeSampleContent', True)
            }
        })
        
        # Also save to database if available
        if db:
            db.set_site_config('site', config['site'])
            db.set_site_config('github', config['github'])
            db.set_site_config('content', config['content'])
            print("✓ Site configuration saved to database")
        
        # Save updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return {'success': True, 'message': 'Site configuration updated'}

    def generate_site_files(self, site_data):
        """Generate site files based on configuration"""
        try:
            # Load templates
            template_dir = os.path.join(os.path.dirname(self.admin_dir), 'templates')
            base_template_path = os.path.join(template_dir, 'base.html')
            
            if not os.path.exists(base_template_path):
                return {'success': False, 'error': 'Base template not found'}
            
            with open(base_template_path, 'r', encoding='utf-8') as f:
                base_template = f.read()
            
            # Initialize static assets (CSS/JS) - THIS IS KEY!
            self.initialize_static_assets()
            
            # Generate pages based on configuration
            pages_generated = []
            
            # Always generate home page
            home_content = self.load_content_template('home-content.html')
            home_page = self.generate_page(base_template, 'Home', home_content, site_data)
            self.write_page('index.html', home_page)
            pages_generated.append('index.html')
            
            # Generate optional pages
            if site_data.get('includeAbout', True):
                about_content = self.load_content_template('about-content.html')
                about_page = self.generate_page(base_template, 'About', about_content, site_data)
                self.write_page('about.html', about_page)
                pages_generated.append('about.html')
            
            if site_data.get('includeContact', True):
                contact_content = self.load_content_template('contact-content.html')
                contact_page = self.generate_page(base_template, 'Contact', contact_content, site_data)
                self.write_page('contact.html', contact_page)
                pages_generated.append('contact.html')
            
            # Create navigation items in database based on selected pages
            if db:
                self.create_navigation_from_site_config(site_data)
            
            return {
                'success': True, 
                'message': f'Generated {len(pages_generated)} pages with shared CSS/JS',
                'pages': pages_generated,
                'note': 'Static assets (CSS/JS) created - update branding to affect all pages'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def load_content_template(self, template_name):
        """Load content template"""
        template_path = os.path.join(self.website_root, 'templates', template_name)
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        return f"<h1>Content for {template_name}</h1><p>Template not found, but page generated successfully.</p>"

    def generate_page(self, base_template, title, content, site_data):
        """Generate a complete page from template and content"""
        # Load branding configuration
        branding = self.load_branding_config()
        
        # Replace all template variables
        replacements = {
            '{{TITLE}}': title,
            '{{SITE_TITLE}}': title,
            '{{SITE_NAME}}': site_data.get('siteName', 'My Website'),
            '{{CONTENT}}': content,
            '{{DESCRIPTION}}': site_data.get('siteDescription', 'A website built with ForgeWeb'),
            '{{SITE_DESCRIPTION}}': site_data.get('siteDescription', 'A website built with ForgeWeb'),
            '{{SITE_AUTHOR}}': site_data.get('siteAuthor', 'Website Owner'),
            '{{SITE_URL}}': site_data.get('siteUrl', 'https://example.com'),
            '{{BRAND_PRIMARY_COLOR}}': branding.get('primaryColor', '#1b5fa3'),
            '{{BRAND_SECONDARY_COLOR}}': branding.get('secondaryColor', '#144a84'),
            '{{BRAND_ACCENT_COLOR}}': branding.get('accentColor', '#f9943b'),
            '{{BRAND_FONT}}': branding.get('font', 'Inter'),
            '{{TAILWIND_CDN_URL}}': 'https://cdn.tailwindcss.com',
            '{{CUSTOM_CSS_PATH}}': 'assets/css/custom.css',
            '{{NAV_LINKS}}': self.generate_nav_links(site_data),
            '{{MOBILE_NAV_LINKS}}': self.generate_nav_links(site_data),
            '{{CURRENT_YEAR}}': str(datetime.now().year)
        }
        
        page = base_template
        for placeholder, value in replacements.items():
            page = page.replace(placeholder, value)
        
        # Handle conditional blocks {{#LOGO_PATH}}...{{/LOGO_PATH}}
        import re
        logo_path = site_data.get('logoPath', '')
        if logo_path:
            page = page.replace('{{#LOGO_PATH}}', '').replace('{{/LOGO_PATH}}', '')
            page = page.replace('{{LOGO_PATH}}', logo_path)
        else:
            page = re.sub(r'\{\{#LOGO_PATH\}\}.*?\{\{/LOGO_PATH\}\}', '', page, flags=re.DOTALL)
        
        return page

    def write_page(self, filename, content):
        """Write page content to file"""
        page_path = os.path.join(self.website_root, filename)
        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def create_github_repo(self, site_data):
        """Create GitHub repository (placeholder)"""
        # This would require GitHub API integration
        return {
            'success': True, 
            'message': 'GitHub repository creation not yet implemented',
            'note': 'Please create repository manually at GitHub.com'
        }

    def run_site_generator(self, site_data):
        """Run the site generator to create files"""
        from datetime import datetime
        
        # Basic site generator implementation
        files_created = []
        
        # Generate index.html
        index_content = self.generate_basic_page(
            title=site_data.get('siteName', 'My Website'),
            description=site_data.get('siteDescription', 'Welcome to my website'),
            content=f"""
            <div class="text-center py-16">
                <h1 class="text-4xl font-bold text-gray-900 mb-4">{site_data.get('siteName', 'My Website')}</h1>
                <p class="text-xl text-gray-600 mb-8">{site_data.get('siteDescription', 'Welcome to my website')}</p>
                <div class="space-x-4">
                    {"<a href='about.html' class='bg-blue-600 text-white px-6 py-3 rounded-lg'>About</a>" if site_data.get('includeAbout') else ""}
                    {"<a href='contact.html' class='bg-green-600 text-white px-6 py-3 rounded-lg'>Contact</a>" if site_data.get('includeContact') else ""}
                </div>
            </div>
            """,
            site_data=site_data
        )
        
        self.write_file('index.html', index_content)
        files_created.append('index.html')
        
        # Generate additional pages based on configuration
        if site_data.get('includeAbout'):
            about_content = self.generate_about_page(site_data)
            self.write_file('about.html', about_content)
            files_created.append('about.html')
            
        if site_data.get('includeContact'):
            contact_content = self.generate_contact_page(site_data)
            self.write_file('contact.html', contact_content)
            files_created.append('contact.html')
            
        # Generate robots.txt and sitemap.xml
        self.write_file('robots.txt', self.generate_robots_txt(site_data))
        self.write_file('sitemap.xml', self.generate_sitemap(site_data, files_created))
        files_created.extend(['robots.txt', 'sitemap.xml'])
        
        return files_created

    def generate_basic_page(self, title, description, content, site_data):
        """Generate a basic HTML page using template"""
        template_path = os.path.join(self.website_root, 'templates', 'base.html')
        
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
        else:
            # Fallback basic template
            template_content = self.get_fallback_template()
        
        # Load branding configuration
        branding = self.load_branding_config()
        
        # Prepare template variables
        template_vars = {
            'SITE_TITLE': title,
            'SITE_NAME': site_data.get('siteName', 'My Website'),
            'SITE_DESCRIPTION': description,
            'SITE_AUTHOR': site_data.get('siteAuthor', 'Website Owner'),
            'SITE_URL': f"https://{site_data.get('githubUsername', 'username')}.github.io/{site_data.get('githubRepo', 'repository')}",
            'CURRENT_YEAR': str(datetime.now().year),
            'CONTENT': content,
            'NAV_LINKS': self.generate_nav_links(site_data),
            'LOGO_PATH': self.get_config_value('LOGO_PATH', 'assets/images/logo.png'),
            'TAILWIND_CDN_URL': self.get_config_value('TAILWIND_CDN_URL', 'https://cdn.tailwindcss.com'),
            'CUSTOM_CSS_PATH': self.get_config_value('CUSTOM_CSS_PATH', 'assets/css/custom.css'),
            'BRAND_PRIMARY_COLOR': branding.get('primaryColor', '#1b5fa3'),
            'BRAND_SECONDARY_COLOR': branding.get('secondaryColor', '#144a84'),
            'BRAND_ACCENT_COLOR': branding.get('accentColor', '#f9943b'),
            'BRAND_FONT': branding.get('font', 'Inter'),
            'FAVICON_PATH': '/favicon.ico'
        }
        
        # Replace template variables
        for key, value in template_vars.items():
            # Handle conditional blocks {{#VARIABLE}}...{{/VARIABLE}}
            if value:
                # Show content between conditional tags
                template_content = template_content.replace(f'{{{{#{key}}}}}', '')
                template_content = template_content.replace(f'{{{{/{key}}}}}', '')
            else:
                # Remove content between conditional tags
                import re
                pattern = f'{{{{#{key}}}}}.*?{{{{/{key}}}}}'
                template_content = re.sub(pattern, '', template_content, flags=re.DOTALL)
            
            # Replace simple variables
            template_content = template_content.replace(f'{{{{{key}}}}}', str(value))
        
        return template_content
    
    def get_fallback_template(self):
        """Basic fallback template if base.html is not found"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{SITE_TITLE}}</title>
    <meta name="description" content="{{SITE_DESCRIPTION}}">
    <script src="{{TAILWIND_CDN_URL}}"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '{{BRAND_PRIMARY_COLOR}}',
                        secondary: '{{BRAND_SECONDARY_COLOR}}',
                        accent: '{{BRAND_ACCENT_COLOR}}'
                    }
                }
            }
        }
    </script>
</head>
<body class="bg-gray-50">
    <nav class="bg-white shadow-sm">
        <div class="max-w-6xl mx-auto px-4 py-4">
            <div class="flex justify-between items-center">
                <h1 class="text-xl font-bold text-primary">{{SITE_NAME}}</h1>
                <div class="space-x-4">{{NAV_LINKS}}</div>
            </div>
        </div>
    </nav>
    <main class="max-w-6xl mx-auto px-4 py-8">{{CONTENT}}</main>
    <footer class="bg-gray-800 text-white py-8 mt-16">
        <div class="max-w-6xl mx-auto px-4 text-center">
            <p>&copy; {{CURRENT_YEAR}} {{SITE_AUTHOR}}. Created with ForgeWeb.</p>
        </div>
    </footer>
</body>
</html>"""
    
    def generate_nav_links(self, site_data):
        """Generate navigation links based on site configuration"""
        links = []
        
        if site_data.get('includeAbout'):
            links.append('<a href="about.html" class="nav-link">About</a>')
        if site_data.get('includeContact'):
            links.append('<a href="contact.html" class="nav-link">Contact</a>')
        if site_data.get('includeBlog'):
            links.append('<a href="blog.html" class="nav-link">Blog</a>')
        if site_data.get('includePortfolio'):
            links.append('<a href="portfolio.html" class="nav-link">Portfolio</a>')
        if site_data.get('includeServices'):
            links.append('<a href="services.html" class="nav-link">Services</a>')
        
        return '\n                    '.join(links)

    def generate_about_page(self, site_data):
        """Generate about page"""
        content = f"""
        <div class="max-w-4xl mx-auto">
            <h1 class="text-4xl font-bold text-gray-900 mb-8">About {site_data.get('siteName', 'Us')}</h1>
            <div class="prose prose-lg">
                <p>Welcome to {site_data.get('siteName', 'our website')}. {site_data.get('siteDescription', 'This is our story.')}</p>
                <p>We're passionate about creating great experiences and building meaningful connections with our community.</p>
                <p>This website was created with ForgeWeb, an AI-powered static site generator by Buildly.</p>
            </div>
        </div>
        """
        return self.generate_basic_page(f"About - {site_data.get('siteName', 'My Website')}", f"Learn more about {site_data.get('siteName', 'us')}", content, site_data)

    def generate_contact_page(self, site_data):
        """Generate contact page"""
        content = f"""
        <div class="max-w-4xl mx-auto">
            <h1 class="text-4xl font-bold text-gray-900 mb-8">Contact Us</h1>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-12">
                <div>
                    <h2 class="text-2xl font-bold mb-4">Get in touch</h2>
                    <form class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium mb-2">Name</label>
                            <input type="text" class="w-full px-3 py-2 border rounded-md" required>
                        </div>
                        <div>
                            <label class="block text-sm font-medium mb-2">Email</label>
                            <input type="email" class="w-full px-3 py-2 border rounded-md" required>
                        </div>
                        <div>
                            <label class="block text-sm font-medium mb-2">Message</label>
                            <textarea class="w-full px-3 py-2 border rounded-md" rows="4" required></textarea>
                        </div>
                        <button type="submit" class="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700">
                            Send Message
                        </button>
                    </form>
                </div>
                <div>
                    <h2 class="text-2xl font-bold mb-4">Contact Information</h2>
                    <div class="space-y-2">
                        <p><strong>Email:</strong> hello@{site_data.get('githubRepo', 'website')}.com</p>
                        <p><strong>Website:</strong> {site_data.get('siteName', 'My Website')}</p>
                    </div>
                </div>
            </div>
        </div>
        """
        return self.generate_basic_page(f"Contact - {site_data.get('siteName', 'My Website')}", f"Contact {site_data.get('siteName', 'us')}", content, site_data)

    def generate_robots_txt(self, site_data):
        """Generate robots.txt"""
        site_url = f"https://{site_data.get('githubUsername', 'username')}.github.io/{site_data.get('githubRepo', 'repository')}"
        return f"""User-agent: *
Allow: /

Sitemap: {site_url}/sitemap.xml"""

    def generate_sitemap(self, site_data, files):
        """Generate sitemap.xml"""
        site_url = f"https://{site_data.get('githubUsername', 'username')}.github.io/{site_data.get('githubRepo', 'repository')}"
        urls = []
        
        for file in files:
            if file.endswith('.html'):
                if file == 'index.html':
                    url = site_url
                else:
                    url = f"{site_url}/{file}"
                urls.append(f"  <url><loc>{url}</loc><changefreq>weekly</changefreq></url>")
        
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""

    def handle_branding_request(self):
        """Handle branding configuration requests"""
        try:
            if self.command == 'GET':
                # Return current branding settings
                branding_config = self.load_branding_config()
                self.send_json_response(branding_config)
            
            elif self.command == 'POST':
                # Save new branding settings
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                branding_data = json.loads(post_data.decode('utf-8'))
                
                result = self.save_branding_config(branding_data)
                self.send_json_response(result)
            
            else:
                self.send_json_error(405, "Method not allowed")
                
        except Exception as e:
            print(f"✗ Branding request error: {e}")
            self.send_json_error(500, str(e))

    def load_branding_config(self):
        """Load current branding configuration"""
        try:
            # Check for branding config file
            branding_path = os.path.join(self.admin_dir, 'branding-config.json')
            if os.path.exists(branding_path):
                with open(branding_path, 'r') as f:
                    return json.load(f)
            
            # Return default branding configuration
            return {
                'colors': {
                    'primary': self.get_config_value('BRAND_PRIMARY_COLOR', '#1b5fa3'),
                    'secondary': self.get_config_value('BRAND_SECONDARY_COLOR', '#144a84'),
                    'accent': self.get_config_value('BRAND_ACCENT_COLOR', '#f9943b')
                },
                'typography': {
                    'fontFamily': 'system',
                    'customFontUrl': '',
                    'borderRadius': 'md'
                },
                'assets': {
                    'logoPath': self.get_config_value('LOGO_PATH', ''),
                    'logoAltText': 'Company Logo',
                    'faviconPath': '/favicon.ico'
                },
                'customCSS': ''
            }
            
        except Exception as e:
            print(f"Error loading branding config: {e}")
            return {'error': str(e)}

    def save_branding_config(self, branding_data):
        """Save branding configuration and update static assets"""
        try:
            branding_path = os.path.join(self.admin_dir, 'branding-config.json')
            
            # Save branding configuration to JSON file
            with open(branding_path, 'w', encoding='utf-8') as f:
                json.dump(branding_data, f, indent=2)
            
            # Also update site-config.json branding section
            site_config_path = os.path.join(self.admin_dir, 'site-config.json')
            if os.path.exists(site_config_path):
                with open(site_config_path, 'r', encoding='utf-8') as f:
                    site_config = json.load(f)
                
                # Update branding section
                site_config['branding'] = self.convert_branding_format(branding_data)
                
                with open(site_config_path, 'w', encoding='utf-8') as f:
                    json.dump(site_config, f, indent=2)
            
            # Save to database if available
            if db:
                db.set_site_config('branding', branding_data)
                print("✓ Branding saved to database")
            
            # UPDATE STATIC ASSETS - This is the key part!
            self.update_static_assets(branding_data)
            
            return {
                'success': True,
                'message': 'Branding updated! All pages will now use the new branding.',
                'note': 'CSS and JS files updated - changes apply to all pages'
            }
            
        except Exception as e:
            print(f"Error saving branding config: {e}")
            return {'success': False, 'error': str(e)}
    
    def convert_branding_format(self, branding_data):
        """Convert branding-config.json format to site-config.json format"""
        colors = branding_data.get('colors', {})
        typography = branding_data.get('typography', {})
        
        return {
            'primaryColor': colors.get('primary', '#1b5fa3'),
            'secondaryColor': colors.get('secondary', '#144a84'),
            'accentColor': colors.get('accent', '#f9943b'),
            'darkColor': colors.get('dark', '#1F2937'),
            'lightColor': colors.get('light', '#F3F4F6'),
            'font': typography.get('headingFont', 'Inter')
        }
    
    def update_static_assets(self, branding_data):
        """Update CSS and JS files in docs/assets with new branding"""
        # Ensure assets directories exist
        css_dir = os.path.join(self.website_root, 'assets', 'css')
        js_dir = os.path.join(self.website_root, 'assets', 'js')
        os.makedirs(css_dir, exist_ok=True)
        os.makedirs(js_dir, exist_ok=True)
        
        # Update custom.css with new branding
        css_content = self.generate_custom_css(branding_data)
        css_path = os.path.join(css_dir, 'custom.css')
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css_content)
        print(f"✓ Updated {css_path}")
        
        # Copy site.js (navigation and utilities)
        source_js = os.path.join(os.path.dirname(self.admin_dir), 'assets', 'js', 'site.js')
        if os.path.exists(source_js):
            dest_js = os.path.join(js_dir, 'site.js')
            shutil.copy2(source_js, dest_js)
            print(f"✓ Copied {dest_js}")
        
        # Update site-config.js with navigation and social data
        self.generate_site_config_js()
        
        return True
    
    
    def build_navigation_from_config(self, site_config):
        """Build navigation array from site-config.json"""
        navigation = []
        navigation.append({'title': 'Home', 'url': 'index.html'})
        
        content_config = site_config.get('content', {})
        if content_config.get('include_about'):
            navigation.append({'title': 'About', 'url': 'about.html'})
        if content_config.get('include_services'):
            navigation.append({'title': 'Services', 'url': 'services.html'})
        if content_config.get('include_portfolio'):
            navigation.append({'title': 'Portfolio', 'url': 'portfolio.html'})
        if content_config.get('include_blog'):
            navigation.append({'title': 'Blog', 'url': 'blog.html'})
        if content_config.get('include_contact'):
            navigation.append({'title': 'Contact', 'url': 'contact.html'})
        
        return navigation
    
    def generate_site_config_js(self):
        """Generate site-config.js with navigation and social media data"""
        try:
            # Load site configuration
            site_config_path = os.path.join(self.admin_dir, 'site-config.json')
            if not os.path.exists(site_config_path):
                return
            
            with open(site_config_path, 'r', encoding='utf-8') as f:
                site_config = json.load(f)
            
            # Build navigation array - try database first
            navigation = []
            if db:
                db_nav_items = db.get_navigation_items(active_only=True)
                if db_nav_items:
                    # Use database navigation
                    for item in db_nav_items:
                        nav_item = {
                            'title': item['title'],
                            'url': item['url']
                        }
                        if item.get('open_new_tab'):
                            nav_item['target'] = '_blank'
                        if item.get('css_class'):
                            nav_item['class'] = item['css_class']
                        navigation.append(nav_item)
                else:
                    # Fall back to config-based navigation
                    navigation = self.build_navigation_from_config(site_config)
            else:
                # No database, use config
                navigation = self.build_navigation_from_config(site_config)
            
            # Get social media configuration
            social_config = site_config.get('social', {})
            social = {
                'twitter': social_config.get('platforms', {}).get('twitter', {}).get('handle', ''),
                'linkedin': social_config.get('platforms', {}).get('linkedin', {}).get('handle', ''),
                'facebook': social_config.get('platforms', {}).get('facebook', {}).get('handle', ''),
                'github': social_config.get('platforms', {}).get('github', {}).get('handle', '')
            }
            
            # Generate JavaScript file
            js_content = f"""/**
 * Site Configuration
 * Auto-generated from site-config.json
 * This file is loaded by all pages to provide navigation and social media links
 */

const SITE_CONFIG = {{
    siteName: {json.dumps(site_config.get('site', {}).get('name', 'My Website'))},
    siteUrl: {json.dumps(site_config.get('site', {}).get('url', ''))},
    description: {json.dumps(site_config.get('site', {}).get('description', ''))},
    navigation: {json.dumps(navigation, indent=4)},
    social: {json.dumps(social, indent=4)},
    currentYear: new Date().getFullYear()
}};

/**
 * Initialize navigation on page load
 */
function initNavigation() {{
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    
    // Update active state in navigation
    SITE_CONFIG.navigation.forEach(item => {{
        item.active = item.url === currentPage;
    }});
}}

/**
 * Toggle mobile menu
 */
function toggleMobileMenu() {{
    const menu = document.getElementById('mobile-menu');
    if (menu) {{
        menu.classList.toggle('hidden');
    }}
}}

/**
 * Build navigation HTML from SITE_CONFIG and inject into the page.
 * Targets elements with id="site-nav" or the first <nav> on the page.
 */
function injectNavigation() {{
    const nav = SITE_CONFIG.navigation;
    if (!nav || nav.length === 0) return;

    const container = document.getElementById('site-nav')
                   || document.querySelector('nav ul')
                   || document.querySelector('nav');
    if (!container) return;

    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const isList = container.tagName === 'UL';

    const links = nav.map(item => {{
        const isActive = item.url === currentPage;
        const target = item.target ? ` target="${{item.target}}"` : '';
        const cls = (item['class'] || '') + (isActive ? ' active' : '');
        const a = `<a href="${{item.url}}" class="nav-link${{cls ? ' ' + cls.trim() : ''}}"${{target}}>${{item.title}}</a>`;
        return isList ? `<li>${{a}}</li>` : a;
    }}).join('\\n');

    container.innerHTML = links;
}}

/**
 * Initialize page
 */
document.addEventListener('DOMContentLoaded', () => {{
    initNavigation();
    injectNavigation();
    
    // Update copyright year if element exists
    const yearElement = document.getElementById('current-year');
    if (yearElement) {{
        yearElement.textContent = SITE_CONFIG.currentYear;
    }}
}});
"""
            
            # Save to docs/assets/js/
            js_dir = os.path.join(self.website_root, 'assets', 'js')
            os.makedirs(js_dir, exist_ok=True)
            js_path = os.path.join(js_dir, 'site-config.js')
            
            with open(js_path, 'w', encoding='utf-8') as f:
                f.write(js_content)
            
            print(f"✓ Generated {js_path}")
            return True
            
        except Exception as e:
            print(f"Error generating site-config.js: {e}")
            return False
    
    def initialize_static_assets(self):
        """Initialize static CSS and JS files for the website"""
        try:
            # Load current branding
            branding = self.load_branding_config()
            
            # Create assets directories
            css_dir = os.path.join(self.website_root, 'assets', 'css')
            js_dir = os.path.join(self.website_root, 'assets', 'js')
            img_dir = os.path.join(self.website_root, 'assets', 'images')
            os.makedirs(css_dir, exist_ok=True)
            os.makedirs(js_dir, exist_ok=True)
            os.makedirs(img_dir, exist_ok=True)
            
            # Generate custom.css with current branding
            css_content = self.generate_custom_css({
                'colors': {
                    'primary': branding.get('primaryColor', '#1b5fa3'),
                    'secondary': branding.get('secondaryColor', '#144a84'),
                    'accent': branding.get('accentColor', '#f9943b')
                },
                'typography': {
                    'fontFamily': 'system',
                    'borderRadius': 'md'
                },
                'customCSS': ''
            })
            
            css_path = os.path.join(css_dir, 'custom.css')
            with open(css_path, 'w', encoding='utf-8') as f:
                f.write(css_content)
            print(f"✓ Created {css_path}")
            
            # Copy or create site.js
            source_js = os.path.join(os.path.dirname(self.admin_dir), 'assets', 'js', 'site.js')
            dest_js = os.path.join(js_dir, 'site.js')
            if os.path.exists(source_js):
                shutil.copy2(source_js, dest_js)
                print(f"✓ Copied {dest_js}")
            else:
                # Create basic site.js if source doesn't exist
                basic_js = """// Site utilities
function toggleMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    if (menu) menu.classList.toggle('hidden');
}
document.addEventListener('DOMContentLoaded', () => {
    const yearEl = document.getElementById('current-year');
    if (yearEl) yearEl.textContent = new Date().getFullYear();
});
"""
                with open(dest_js, 'w', encoding='utf-8') as f:
                    f.write(basic_js)
                print(f"✓ Created {dest_js}")
            
            # Generate site-config.js with navigation
            self.generate_site_config_js()
            
            print("✓ Static assets initialized")
            return True
            
        except Exception as e:
            print(f"Error initializing static assets: {e}")
            return False

    def generate_custom_css(self, branding_data):
        """Generate custom CSS with branding variables"""
        colors = branding_data.get('colors', {})
        typography = branding_data.get('typography', {})
        custom_css = branding_data.get('customCSS', '')
        
        css_content = f"""/* ForgeWeb Custom Styles - Auto-generated */
:root {{
    /* Brand colors */
    --brand-primary: {colors.get('primary', '#1b5fa3')};
    --brand-secondary: {colors.get('secondary', '#144a84')};
    --brand-accent: {colors.get('accent', '#f9943b')};
    
    /* Additional brand variables */
    --brand-text: #1f2937;
    --brand-bg: #f9fafb;
    --brand-border: #e5e7eb;
}}

/* Typography */
{self.get_font_css(typography)}

/* Custom button styles */
.btn-brand {{
    background-color: var(--brand-primary);
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: {self.get_border_radius(typography.get('borderRadius', 'md'))};
    font-weight: 500;
    transition: background-color 0.2s;
}}

.btn-brand:hover {{
    background-color: var(--brand-secondary);
}}

.btn-brand-outline {{
    border: 2px solid var(--brand-primary);
    color: var(--brand-primary);
    padding: 0.75rem 1.5rem;
    border-radius: {self.get_border_radius(typography.get('borderRadius', 'md'))};
    font-weight: 500;
    background: transparent;
    transition: all 0.2s;
}}

.btn-brand-outline:hover {{
    background-color: var(--brand-primary);
    color: white;
}}

/* Navigation enhancements */
.nav-link {{
    color: #374151;
    transition: color 0.2s;
}}

.nav-link:hover {{
    color: var(--brand-primary);
}}

.nav-link.active {{
    color: var(--brand-primary);
}}

/* Card hover effects */
.card-hover {{
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}}

.card-hover:hover {{
    transform: translateY(-4px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}}

/* Custom CSS from user */
{custom_css}
"""
        return css_content

    def get_font_css(self, typography):
        """Generate font CSS based on typography settings"""
        font_family = typography.get('fontFamily', 'system')
        custom_url = typography.get('customFontUrl', '')
        
        if font_family == 'custom' and custom_url:
            return f"""@import url('{custom_url}');
body {{ font-family: 'Custom Font', system-ui, sans-serif; }}"""
        elif font_family == 'inter':
            return """@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
body { font-family: 'Inter', system-ui, sans-serif; }"""
        elif font_family == 'roboto':
            return """@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
body { font-family: 'Roboto', system-ui, sans-serif; }"""
        elif font_family == 'opensans':
            return """@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;500;600;700&display=swap');
body { font-family: 'Open Sans', system-ui, sans-serif; }"""
        elif font_family == 'lato':
            return """@import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&display=swap');
body { font-family: 'Lato', system-ui, sans-serif; }"""
        elif font_family == 'montserrat':
            return """@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');
body { font-family: 'Montserrat', system-ui, sans-serif; }"""
        else:
            return """body { font-family: system-ui, -apple-system, sans-serif; }"""

    def get_border_radius(self, radius_setting):
        """Convert border radius setting to CSS value"""
        radius_map = {
            'none': '0px',
            'sm': '4px',
            'md': '8px',
            'lg': '12px',
            'xl': '16px',
            'full': '50%'
        }
        return radius_map.get(radius_setting, '8px')

    def update_env_variables(self, branding_data):
        """Update environment variables with branding data"""
        try:
            colors = branding_data.get('colors', {})
            # Update in-memory configuration (for current session)
            if colors.get('primary'):
                os.environ['BRAND_PRIMARY_COLOR'] = colors['primary']
            if colors.get('secondary'):
                os.environ['BRAND_SECONDARY_COLOR'] = colors['secondary']
            if colors.get('accent'):
                os.environ['BRAND_ACCENT_COLOR'] = colors['accent']
        except Exception as e:
            print(f"Warning: Could not update environment variables: {e}")
    
    # Navigation API handlers
    def handle_navigation_add(self):
        """Handle POST /api/navigation - Add new navigation item"""
        try:
            if not db:
                self.send_json_error(500, 'Database not available')
                return
            
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Extract parameters
            title = data.get('title', '').strip()
            url = data.get('url', '').strip()
            position = data.get('position', 0)
            parent_id = data.get('parent_id')
            is_active = data.get('is_active', True)
            open_new_tab = data.get('open_new_tab', False)
            css_class = data.get('css_class', '')
            
            # Validate required fields
            if not title or not url:
                self.send_json_error(400, 'Title and URL are required')
                return
            
            # Add to database
            nav_id = db.add_navigation_item(
                title=title,
                url=url,
                position=position,
                parent_id=parent_id,
                is_active=is_active,
                open_new_tab=open_new_tab,
                css_class=css_class
            )
            
            # Regenerate site-config.js
            self.generate_site_config_js()
            
            self.send_json_response({
                'success': True,
                'id': nav_id,
                'message': 'Navigation item added successfully'
            })
            
        except Exception as e:
            print(f"Error adding navigation item: {e}")
            self.send_json_error(500, str(e))
    
    def handle_navigation_update(self):
        """Handle PUT/POST /api/navigation/:id - Update navigation item"""
        try:
            if not db:
                self.send_json_error(500, 'Database not available')
                return
            
            # Extract ID from path
            nav_id = self.path.split('/')[-1]
            try:
                nav_id = int(nav_id)
            except ValueError:
                self.send_json_error(400, 'Invalid navigation ID')
                return
            
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Update in database (only provided fields)
            success = db.update_navigation_item(
                nav_id=nav_id,
                title=data.get('title'),
                url=data.get('url'),
                position=data.get('position'),
                parent_id=data.get('parent_id'),
                is_active=data.get('is_active'),
                open_new_tab=data.get('open_new_tab'),
                css_class=data.get('css_class')
            )
            
            if not success:
                self.send_json_error(404, 'Navigation item not found')
                return
            
            # Regenerate site-config.js
            self.generate_site_config_js()
            
            self.send_json_response({
                'success': True,
                'message': 'Navigation item updated successfully'
            })
            
        except Exception as e:
            print(f"Error updating navigation item: {e}")
            self.send_json_error(500, str(e))
    
    def handle_navigation_delete(self):
        """Handle DELETE /api/navigation/:id - Delete navigation item"""
        try:
            if not db:
                self.send_json_error(500, 'Database not available')
                return
            
            # Extract ID from path
            nav_id = self.path.split('/')[-1]
            try:
                nav_id = int(nav_id)
            except ValueError:
                self.send_json_error(400, 'Invalid navigation ID')
                return
            
            # Delete from database
            success = db.delete_navigation_item(nav_id)
            
            if not success:
                self.send_json_error(404, 'Navigation item not found')
                return
            
            # Regenerate site-config.js
            self.generate_site_config_js()
            
            self.send_json_response({
                'success': True,
                'message': 'Navigation item deleted successfully'
            })
            
        except Exception as e:
            print(f"Error deleting navigation item: {e}")
            self.send_json_error(500, str(e))


    def handle_social_accounts(self):
        """Handle social media accounts save/update"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            accounts_data = json.loads(post_data.decode('utf-8'))
            
            # Save to site-config.json
            site_config_path = os.path.join(self.admin_dir, 'site-config.json')
            site_config = {}
            if os.path.exists(site_config_path):
                with open(site_config_path, 'r') as f:
                    site_config = json.load(f)
            
            site_config['social'] = accounts_data
            
            with open(site_config_path, 'w') as f:
                json.dump(site_config, f, indent=2)
            
            # Also save to database if available
            if db:
                db.set_site_config('social', accounts_data)
            
            self.send_json_response({
                'success': True,
                'message': 'Social media accounts saved successfully'
            })
            
        except Exception as e:
            print(f"Error saving social accounts: {e}")
            self.send_json_error(500, str(e))
    
    def handle_settings(self):
        """Handle app settings save/update"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            settings_data = json.loads(post_data.decode('utf-8'))
            
            # Save to site-config.json
            site_config_path = os.path.join(self.admin_dir, 'site-config.json')
            site_config = {}
            if os.path.exists(site_config_path):
                with open(site_config_path, 'r') as f:
                    site_config = json.load(f)
            
            # Merge settings into config
            site_config['settings'] = settings_data
            
            with open(site_config_path, 'w') as f:
                json.dump(site_config, f, indent=2)
            
            # Also save to database if available
            if db:
                # Save each setting category to database
                for category, values in settings_data.items():
                    for key, value in values.items():
                        db.set_setting(category, key, value)
            
            self.send_json_response({
                'success': True,
                'message': 'Settings saved successfully'
            })
            
        except Exception as e:
            print(f"Error saving settings: {e}")
            self.send_json_error(500, str(e))
    
    def load_social_accounts(self):
        """Load social media accounts from config"""
        try:
            # Try database first
            if db:
                social_data = db.get_site_config('social')
                if social_data:
                    return social_data
            
            # Fallback to file
            site_config_path = os.path.join(self.admin_dir, 'site-config.json')
            if os.path.exists(site_config_path):
                with open(site_config_path, 'r') as f:
                    site_config = json.load(f)
                    return site_config.get('social', {})
            
            # Return empty structure
            return {
                'linkedin': {'company': '', 'personal': '', 'template': ''},
                'bluesky': {'handle': '', 'display': '', 'template': ''},
                'mastodon': {'instance': '', 'username': '', 'template': ''}
            }
        except Exception as e:
            print(f"Error loading social accounts: {e}")
            return {}
    
    def load_settings(self):
        """Load app settings from database or config file"""
        try:
            settings = {}
            
            # Try database first
            if db:
                # Load settings by category
                for category in ['aiProviders', 'content', 'social']:
                    category_settings = db.get_site_config(f'settings_{category}')
                    if category_settings:
                        settings[category] = category_settings
            
            # Fallback to file
            if not settings:
                site_config_path = os.path.join(self.admin_dir, 'site-config.json')
                if os.path.exists(site_config_path):
                    with open(site_config_path, 'r') as f:
                        site_config = json.load(f)
                        settings = site_config.get('settings', {})
            
            return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            return {}

    def handle_html_import(self):
        """Handle HTML import requests"""
        try:
            # Placeholder for HTML import functionality
            self.send_json_response({
                'success': False,
                'message': 'HTML import functionality coming soon'
            })
        except Exception as e:
            self.send_json_error(500, str(e))

    def create_github_repo(self, site_data):
        """Create GitHub repository (requires requests library)"""
        if not requests:
            return {'success': False, 'error': 'requests library not available'}
        
        github_token = site_data.get('githubToken')
        if not github_token:
            return {'success': False, 'error': 'No GitHub token provided'}
        
        try:
            # Create repository via GitHub API
            headers = {
                'Authorization': f'token {github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            repo_data = {
                'name': site_data.get('githubRepo'),
                'description': site_data.get('siteDescription', 'Website created with ForgeWeb'),
                'homepage': f"https://{site_data.get('githubUsername')}.github.io/{site_data.get('githubRepo')}",
                'private': False,
                'has_pages': True
            }
            
            response = requests.post(
                'https://api.github.com/user/repos',
                headers=headers,
                json=repo_data
            )
            
            if response.status_code == 201:
                return {'success': True, 'message': 'GitHub repository created successfully'}
            else:
                return {'success': False, 'error': f'GitHub API error: {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': f'GitHub creation failed: {str(e)}'}

    def write_file(self, path, content):
        """Write file to website root"""
        full_path = os.path.join(self.website_root, path)
        dir_path = os.path.dirname(full_path)
        
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def clean_path(self, path):
        """Clean and validate file path"""
        clean_path = path.replace('../', '')
        if clean_path.startswith('/'):
            clean_path = clean_path[1:]
        return clean_path

    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def send_json_error(self, status_code, message):
        """Send JSON error response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        error_data = {'error': message, 'status': status_code}
        self.wfile.write(json.dumps(error_data).encode('utf-8'))

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def start_forgeweb_server(port=8000, host='localhost'):
    """Start the ForgeWeb server"""
    try:
        server = HTTPServer((host, port), ForgeWebHandler)
        server.server_port = port  # Store port for handlers to access
        
        # Create a temporary handler to get paths
        class PathHandler(ForgeWebHandler):
            def __init__(self):
                self.admin_dir = os.path.dirname(os.path.abspath(__file__))
                forge_web_dir = os.path.dirname(self.admin_dir)
                repo_root = os.path.dirname(forge_web_dir)
                # Always report docs/ as the website root (GitHub Pages branch deploy)
                self.website_root = os.path.join(repo_root, 'docs')
        
        path_info = PathHandler()
        repo_root = os.path.dirname(os.path.dirname(path_info.admin_dir))
        
        print(f"""
🚀 ForgeWeb Server Running!

📂 Directory Structure:
   Repository Root:     {repo_root}/
   ├── ForgeWeb/        (admin tools, not deployed)
   └── docs/            (your content, deployed to GitHub Pages)
   
   ➡️  Your pages save to: {path_info.website_root}/
   ➡️  ForgeWeb excluded via .gitignore

🌐 Admin Dashboard:
   http://{host}:{port}/admin/
   
💡 First Steps:
   1. Open the admin dashboard above
   2. Choose a design system (auto-prompts)
   3. Your homepage will be auto-generated
   4. Then preview at: http://{host}:{port}/
   
📚 Documentation:
   • Quick Start: ForgeWeb/QUICK-START.md
   • Setup Guide: ForgeWeb/SETUP-REPO.md
   
Press Ctrl+C to stop the server.
        """)
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n👋 ForgeWeb server stopped.")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ForgeWeb Local Server')
    parser.add_argument('--port', type=int, default=8000, help='Port number (default: 8000)')
    parser.add_argument('--host', default='localhost', help='Host address (default: localhost)')
    
    args = parser.parse_args()
    start_forgeweb_server(args.port, args.host)