# 🏗️ ForgeWeb Architecture

## Submodule Design Philosophy

ForgeWeb is designed as a **Git submodule** to maintain a clean separation between:
- **Your website content** (HTML, articles, assets) - deployed to GitHub Pages
- **Admin tools** (ForgeWeb dashboard, templates, database) - stays local

## Directory Structure

```
your-website/                         ← Main repository (YOUR content)
├── .git/                            ← Git repository for YOUR website
├── .gitignore                       ← Ignores OS files, editor files
├── index.html                       ← Your homepage (auto-generated)
├── about.html                       ← Your about page
├── contact.html                     ← Your contact page
├── articles/                        ← Blog posts
│   ├── my-first-post.html
│   └── another-article.html
├── assets/                          ← CSS, images, JavaScript
│   ├── css/
│   │   └── custom.css
│   └── images/
│       └── logo.png
└── ForgeWeb/                        ← Git submodule (admin tools)
    ├── .git/                        ← Separate Git repository for ForgeWeb
    ├── admin/                       ← Admin dashboard
    │   ├── index.html               ← Dashboard UI
    │   ├── editor.html              ← Article editor
    │   ├── page-editor.html         ← Page editor
    │   ├── forgeweb.db              ← SQLite database (gitignored)
    │   ├── file-api.py              ← Development server
    │   ├── database.py              ← Database manager
    │   ├── js/                      ← Admin JavaScript
    │   └── css/                     ← Admin styles
    ├── templates/                   ← Page templates
    │   ├── base.html
    │   ├── home-content.html
    │   └── about-content.html
    ├── start.sh                     ← Start server (Unix/Mac)
    ├── start.bat                    ← Start server (Windows)
    └── README.md                    ← ForgeWeb documentation
```

## How It Works

### File Saving Flow

1. **User creates content** in admin dashboard (http://localhost:8000/admin/)
2. **ForgeWeb saves files** to parent directory:
   - Pages → `../index.html`, `../about.html`
   - Articles → `../articles/my-post.html`
   - Assets → `../assets/images/photo.jpg`
3. **User commits to Git** (in parent directory, NOT ForgeWeb)
4. **GitHub Pages deploys** only the parent directory

### What Gets Committed Where

**Your Website Repository (`your-website/`)**:
```bash
git add index.html articles/ assets/
git commit -m "Add new blog post"
git push
```
- ✅ All HTML pages
- ✅ Articles directory
- ✅ Assets (CSS, images)
- ✅ `.gitignore`
- ✅ Submodule reference (`.gitmodules`)

**ForgeWeb Submodule (`ForgeWeb/`)**:
```bash
# You typically DON'T commit anything here
# ForgeWeb updates come from upstream
```
- ✅ Admin dashboard code
- ✅ Templates
- ✅ Server scripts
- ❌ Database (gitignored)
- ❌ User content (saved to parent)

## Key Benefits

### 1. **Clean Deployment**
Only your website content gets deployed to GitHub Pages. ForgeWeb admin tools stay local.

### 2. **Easy Updates**
Update ForgeWeb admin tools without touching your content:
```bash
cd ForgeWeb
git pull origin main
```

### 3. **Portable Development**
Clone your website on any machine, ForgeWeb comes along:
```bash
git clone https://github.com/you/your-website.git
cd your-website
git submodule update --init --recursive
cd ForgeWeb && ./start.sh
```

### 4. **Separation of Concerns**
- **ForgeWeb repository**: Maintains admin tools, templates, and development environment
- **Your repository**: Contains only your content and configuration

## File Paths in Code

### In `file-api.py`:
```python
# ForgeWeb is a submodule - website files go to parent directory
forge_web_dir = os.path.dirname(self.admin_dir)  # /path/to/your-website/ForgeWeb
self.website_root = os.path.dirname(forge_web_dir)  # /path/to/your-website

# Save files to parent directory
page_path = os.path.join(self.website_root, 'index.html')  # ../index.html
article_path = os.path.join(self.website_root, 'articles', 'post.html')  # ../articles/post.html
```

### File Save Locations:
- **Homepage**: `../index.html` (relative to ForgeWeb/admin/)
- **Pages**: `../about.html`, `../contact.html`
- **Articles**: `../articles/my-post.html`
- **Assets**: `../assets/images/logo.png`
- **Database**: `ForgeWeb/admin/forgeweb.db` (local only, gitignored)

## GitHub Pages Deployment

When you push to GitHub:

```bash
cd ~/Projects/your-website  # Parent directory

# Add and commit your content (NOT ForgeWeb files)
git add index.html articles/ assets/
git commit -m "Update website"
git push
```

GitHub Pages sees:
```
your-website/
├── index.html              ← Deployed ✅
├── about.html              ← Deployed ✅
├── articles/               ← Deployed ✅
├── assets/                 ← Deployed ✅
└── ForgeWeb/               ← Ignored (submodule) ❌
```

The `ForgeWeb/` directory is a **submodule reference** - GitHub Pages doesn't deploy submodules, only the files in your main repository.

## Database Storage

The SQLite database (`admin/forgeweb.db`) stores:
- Design system choice (Tailwind, Bootstrap, etc.)
- Site configuration (name, description)
- Page metadata
- Article metadata
- Media library references
- Settings

**Important**: The database is **local only** and **gitignored**. It does NOT get deployed or committed.

## Common Workflows

### Creating a New Page
1. Open admin: `http://localhost:8000/admin/`
2. Click "Page Editor"
3. Write content, click "Save"
4. File saved to: `../my-page.html`
5. Commit: `git add my-page.html && git commit -m "Add new page"`

### Writing a Blog Post
1. Open "Article Editor"
2. Write post, click "Save"
3. File saved to: `../articles/my-post.html`
4. Commit: `git add articles/my-post.html && git commit -m "New blog post"`

### Updating ForgeWeb
1. `cd ForgeWeb`
2. `git pull origin main`
3. `cd .. && git add ForgeWeb`
4. `git commit -m "Update ForgeWeb"`

## Security Notes

- **Database**: Local only, never deployed
- **Admin interface**: Runs on localhost:8000, not accessible publicly
- **File API**: Development server only, not for production
- **GitHub Pages**: Only serves static HTML, no server-side code

## Troubleshooting

### "ForgeWeb directory is empty after cloning"
```bash
git submodule update --init --recursive
```

### "Files not being saved to parent directory"
Check that `file-api.py` has correct path:
```python
self.website_root = os.path.dirname(forge_web_dir)
```

### "ForgeWeb showing up in GitHub Pages"
ForgeWeb shouldn't deploy as a submodule. If it does, check your `.gitmodules` file exists:
```ini
[submodule "ForgeWeb"]
	path = ForgeWeb
	url = https://github.com/Buildly-Marketplace/ForgeWeb.git
```

## Summary

✅ **ForgeWeb = Admin Tools** (submodule, local only)  
✅ **Parent Directory = Your Website** (deployed to GitHub Pages)  
✅ **Database = Local Configuration** (gitignored)  
✅ **Clean Separation** = Easy deployment and updates
