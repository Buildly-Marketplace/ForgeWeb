# 🚀 ForgeWeb Deployment Guide

## 📂 Understanding the File Structure

ForgeWeb separates your website content from the admin tools. Here's how the files are organized:

```
Your Project Directory/
│
├── ForgeWeb/                      ← Admin tools (LOCAL ONLY - not deployed)
│   ├── admin/                     ← Admin interface
│   │   ├── index.html            ← Admin dashboard
│   │   ├── editor.html           ← Content editor
│   │   ├── file-api.py           ← Local development server
│   │   ├── database.py           ← Database manager
│   │   ├── forgeweb.db           ← SQLite database (config, metadata)
│   │   └── site-config.json      ← Config backup
│   ├── templates/                ← Page templates (LOCAL ONLY)
│   │   ├── base.html
│   │   └── article-template.html
│   ├── start.sh / start.bat      ← Startup scripts
│   ├── index.html                ← Redirect to admin (LOCAL ONLY)
│   └── README.md                 ← Documentation
│
└── website/                       ← YOUR WEBSITE (gets deployed to GitHub Pages)
    ├── index.html                 ← YOUR SITE'S HOMEPAGE (deployed)
    ├── 404.html                   ← Error page (deployed)
    ├── about.html                 ← Your pages (deployed)
    ├── contact.html               ← Your pages (deployed)
    │
    ├── articles/                  ← Blog posts (deployed)
    │   ├── my-first-post.html
    │   └── another-article.html
    │
    └── assets/                    ← Site assets (deployed)
        ├── css/
        │   └── custom.css
        ├── images/
        │   └── your-images.jpg
        └── js/
            └── your-scripts.js

```

### 🎯 What Gets Deployed vs What Stays Local

**DEPLOYED to GitHub Pages (from `website/` directory):**
- ✅ `website/index.html` and all `.html` files
- ✅ `website/assets/` folder (CSS, images, JavaScript)
- ✅ `website/articles/` or `website/blog/` folders
- ✅ Any custom content folders you create in `website/`
- ✅ `website/404.html` for custom error page

**Stays LOCAL (not deployed):**
- ❌ `admin/` folder - This is your local admin interface
- ❌ `admin/forgeweb.db` - SQLite database with all your settings
- ❌ `templates/` folder - Source templates, not final pages
- ❌ `start.sh` / `start.bat` - Development scripts
- ❌ `.env` file - Configuration secrets
- ❌ `venv/` folder - Python virtual environment

### 💾 About the Database

ForgeWeb uses a local SQLite database (`admin/forgeweb.db`) to store:
- **Design system configuration** (Tailwind, Bootstrap, etc.)
- **Site settings** (name, description, URLs)
- **Page metadata** (titles, slugs, creation dates)
- **Article metadata** (categories, tags, authors)
- **Media tracking** (uploaded files, alt text)
- **User preferences** (editor settings, etc.)

**Important:** 
- The database is **local only** and never deployed
- It's automatically created on first startup
- Backed up by JSON files for compatibility
- Excluded from Git via `.gitignore`

---

## 🌐 Deploying to GitHub Pages

### Method 1: Automatic Deployment (Recommended)

1. **Initialize Git Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial ForgeWeb site"
   ```

2. **Create GitHub Repository**
   - Go to [github.com/new](https://github.com/new)
   - Name it (e.g., `my-website`)
   - Don't initialize with README
   - Click "Create repository"

3. **Push to GitHub**
   ```bash
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
   git push -u origin main
   ```

4. **Enable GitHub Pages**
   - Go to your repository on GitHub
   - Click **Settings** → **Pages**
   - Under "Source": Select **Deploy from a branch**
   - Under "Branch": Select **main** and **/ (root)**
   - Click **Save**

5. **Your site is live!**
   - URL: `https://YOUR-USERNAME.github.io/YOUR-REPO/`
   - It may take 1-2 minutes to build

### Method 2: Using .gitignore (Clean Deployment)

Create a `.gitignore` file to exclude local-only files:

```bash
# .gitignore
admin/
templates/
venv/
*.pyc
__pycache__/
.env
.DS_Store
start.sh
start.bat
setup-dev.sh
requirements.txt
```

Then deploy:
```bash
git add .gitignore
git add .
git commit -m "Add gitignore and site files"
git push
```

This ensures only your website files are deployed, not admin tools.

---

## 📝 Content Creation Best Practices

### Where to Save Your Files

**Pages (like About, Contact, Services):**
- Save directly in the root: `about.html`, `contact.html`, `services.html`
- These will be accessible at: `yourdomain.com/about.html`

**Blog Posts / Articles:**
- Save in `articles/` or `blog/` folder
- Example: `articles/my-first-post.html`
- Accessible at: `yourdomain.com/articles/my-first-post.html`

**Images and Media:**
- Save in `assets/images/`
- Reference in HTML: `<img src="/assets/images/photo.jpg">`

**Custom Styles:**
- Add to `assets/css/custom.css`
- Already linked in your templates

**Custom JavaScript:**
- Add to `assets/js/custom.js`
- Include in your pages as needed

### Design System Integration

When you choose a design system (Tailwind, Bootstrap, etc.):

1. **It's saved in `admin/site-config.json`**
   ```json
   {
     "design": {
       "system": "tailwind",
       "cdn_urls": ["https://cdn.tailwindcss.com"],
       "body_classes": "bg-gray-50"
     }
   }
   ```

2. **Templates automatically use it**
   - All new pages include the CDN links
   - Body classes are applied automatically
   - Consistent styling across your site

3. **You can change it anytime**
   - Go to Admin → Design Chooser
   - Select a new framework
   - Rebuild pages with new design

---

## 🔄 Updating Your Site

### Development Workflow

1. **Start the local server**
   ```bash
   ./start.sh  # or start.bat on Windows
   ```

2. **Open admin interface**
   - Go to `http://localhost:8000/admin/`
   
3. **Create/edit content**
   - Use Page Editor or Article Editor
   - Preview at `http://localhost:8000/`

4. **Commit and push changes**
   ```bash
   git add .
   git commit -m "Updated homepage"
   git push
   ```

5. **GitHub Pages auto-deploys**
   - Changes appear in 1-2 minutes
   - Check Actions tab for build status

### Quick Update Commands

```bash
# Pull latest changes
git pull

# Add all changes
git add .

# Commit with message
git commit -m "Your update message"

# Push to deploy
git push

# All in one command
git add . && git commit -m "Update site" && git push
```

---

## 🎨 Customization Tips

### Custom Domain

1. **Add CNAME file**
   - Create `CNAME` in root (no extension)
   - Add your domain: `www.yourdomain.com`
   
2. **Configure DNS**
   - Add CNAME record pointing to: `USERNAME.github.io`
   - Or A records to GitHub's IPs

3. **Enable in GitHub**
   - Settings → Pages
   - Add custom domain
   - Enable HTTPS

### SEO Optimization

1. **Add meta tags** (templates handle this)
2. **Create `sitemap.xml`**
3. **Add `robots.txt`**
4. **Use semantic HTML**
5. **Optimize images** before uploading

### Analytics

Add Google Analytics or similar to your templates:

```html
<!-- Add to templates/base.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

---

## 🔒 Security & Best Practices

### Never Commit Sensitive Data

**DO NOT commit:**
- API keys in `.env`
- GitHub tokens
- Database credentials
- Private configuration

**Keep in `.gitignore`:**
```
.env
*.key
*.pem
secrets/
```

### Admin Interface Security

The `admin/` folder:
- Only runs locally (localhost:8000)
- Never expose to public internet
- Use `.gitignore` to exclude from deployment
- GitHub Pages won't serve it anyway

---

## 🆘 Troubleshooting

### Site not updating after push

1. Check GitHub Actions (if using)
2. Hard refresh browser: `Ctrl+F5` or `Cmd+Shift+R`
3. Check GitHub Pages settings
4. Wait 2-5 minutes for propagation

### 404 errors on GitHub Pages

1. Ensure `index.html` exists in root
2. Check file names (case-sensitive on Linux servers)
3. Verify GitHub Pages is enabled
4. Check that branch is set correctly

### Design system not applying

1. Check `admin/site-config.json` has design config
2. Verify CDN URLs are accessible
3. Rebuild pages in admin
4. Check browser console for errors

### Local server issues

1. Ensure Python 3.8+ is installed
2. Run `./start.sh` from ForgeWeb directory
3. Check port 8000 isn't in use
4. Review terminal for error messages

---

## 📚 Additional Resources

- **GitHub Pages Docs**: https://docs.github.com/pages
- **Custom Domains**: https://docs.github.com/pages/configuring-a-custom-domain-for-your-github-pages-site
- **Tailwind CSS**: https://tailwindcss.com/docs
- **Bootstrap**: https://getbootstrap.com/docs
- **ForgeWeb Issues**: https://github.com/Buildly-Marketplace/ForgeWeb/issues

---

## ✨ Summary

1. **Create content** in the admin interface
2. **Files are saved** to the ForgeWeb root directory
3. **Commit and push** to GitHub
4. **GitHub Pages** automatically deploys your site
5. **Site is live** at `username.github.io/repository`

**That's it! Your site is version-controlled, backed up, and automatically deployed.** 🎉
