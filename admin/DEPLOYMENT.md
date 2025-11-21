# ForgeWeb Deployment Guide

ForgeWeb uses a **git submodule architecture** to keep admin tools separate from your deployable website.

## 🏗️ File Structure

```
your-website/                    ← Your main repository
├── .git/
├── .gitignore
├── index.html                  ← Homepage (auto-generated)
├── about.html
├── contact.html
├── articles/                   ← Blog posts
│   └── my-first-post.html
├── assets/                     ← CSS, images, JavaScript
│   ├── css/
│   └── images/
└── ForgeWeb/                   ← Git submodule (NOT deployed)
    ├── admin/                  ← Admin dashboard
    │   ├── index.html
    │   ├── editor.html
    │   ├── forgeweb.db         ← SQLite database (local only)
    │   └── file-api.py
    ├── templates/
    └── start.sh
```

## 🚀 Deployment to GitHub Pages

### Step 1: Initialize Your Website Repository

```bash
# Navigate to your website directory
cd ~/Projects/my-website

# Initialize git if not already done
git init

# Make sure you have a .gitignore
cat > .gitignore << 'EOF'
# OS Files
.DS_Store
Thumbs.db

# Editor files
.vscode/
.idea/

# Temporary files
*.tmp
*.bak
EOF

# Commit your content
git add .
git commit -m "Initial website commit"
```

### Step 2: Create GitHub Repository

```bash
# Create a new repository on GitHub (via website), then:
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git branch -M main
git push -u origin main
```

### Step 3: Enable GitHub Pages

### Step 3: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Under **Source**, select:
   - **Branch**: `main`
   - **Folder**: `/ (root)`
4. Click **Save**

Your site will be live at: `https://YOUR-USERNAME.github.io/YOUR-REPO/`

## ✅ What Gets Deployed

### Deployed to GitHub Pages:
- ✅ `index.html` - Your homepage
- ✅ `about.html`, `contact.html` - Your pages
- ✅ `articles/` - Blog posts
- ✅ `assets/` - CSS, images, JavaScript
- ✅ All HTML files you create

### NOT Deployed (stays local):
- ❌ `ForgeWeb/` - Git submodule (admin tools)
- ❌ `ForgeWeb/admin/forgeweb.db` - SQLite database
- ❌ `ForgeWeb/admin/` - Admin dashboard
- ❌ `ForgeWeb/templates/` - Page templates
- ❌ All ForgeWeb admin scripts

## 🔄 Cloning on Another Machine

When you or a team member clones your website repository:

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
cd YOUR-REPO

# Initialize the ForgeWeb submodule
git submodule update --init --recursive

# Start ForgeWeb
cd ForgeWeb
./start.sh
```

## 🔧 Updating ForgeWeb

To update ForgeWeb to the latest version:

```bash
cd ~/Projects/my-website/ForgeWeb

# Pull latest changes
git pull origin main

# Go back to main repo and commit the update
cd ..
git add ForgeWeb
git commit -m "Update ForgeWeb to latest version"
git push
```

## 🌐 Custom Domain

To use a custom domain with GitHub Pages:

1. Add a `CNAME` file to your website root:
   ```bash
   echo "www.yourdomain.com" > CNAME
   git add CNAME
   git commit -m "Add custom domain"
   git push
   ```

2. Configure DNS with your domain provider:
   - Add a `CNAME` record pointing to `YOUR-USERNAME.github.io`
   - Or add `A` records pointing to GitHub's IPs (see [GitHub Docs](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site))

3. Enable HTTPS in GitHub Pages settings

## 🛠️ Troubleshooting

### ForgeWeb submodule is empty after cloning
```bash
git submodule update --init --recursive
```

### Changes not showing on GitHub Pages
```bash
        "primaryColor": "#your-color",
        "secondaryColor": "#your-secondary", 
        "accentColor": "#your-accent"
    }
}
```

### 3. Start Development Server
```bash
cd your-website
python admin/dev-server.py 8000
```

### 4. Access Admin Interface
- **Admin Dashboard:** http://localhost:8000/admin/
- **Content Editor:** http://localhost:8000/admin/editor.html
- **Settings:** http://localhost:8000/admin/settings.html

## Features

### ✅ Works With Any Static Site
- GitHub Pages
- Netlify
- Vercel
- Custom hosting
- Local development

### ✅ Content Management
- Create new articles with AI assistance
- Edit existing HTML files
- Generate SEO-optimized content
- Auto-generate meta tags and structured data

### ✅ AI Integration
- **Ollama (Local):** Run AI locally with privacy
- **OpenAI:** Use GPT models with API key
- **Google Gemini:** Use Gemini Pro with API key

### ✅ Social Media
- Auto-generate posts for Twitter, LinkedIn, Facebook
- Platform-specific optimization
- Custom hashtag suggestions

### ✅ File Management
- Browse and edit website files
- Save directly to local filesystem
- Smart filename generation from titles

## Customization

### Categories
Add/remove content categories in `site-config.json`:
```json
"categories": [
    {"id": "tutorial", "name": "Tutorials", "color": "purple-500"},
    {"id": "news", "name": "News", "color": "red-500"}
]
```

### Folder Structure
Configure where content gets saved:
```json
"folders": [
    {"id": "content/posts/", "name": "Posts"},
    {"id": "content/pages/", "name": "Pages"}
]
```

### Branding
Match your website's colors:
```json
"branding": {
    "primaryColor": "#1e40af",
    "secondaryColor": "#1e3a8a",
    "accentColor": "#f59e0b",
    "font": "Inter"
}
```

### Social Platforms
Enable/disable platforms:
```json
"social": {
    "platforms": {
        "twitter": {"enabled": true, "characterLimit": 280},
        "linkedin": {"enabled": true, "characterLimit": 3000},
        "facebook": {"enabled": false}
    }
}
```

## GitHub Pages Deployment

### Option 1: Include Admin in Repository
1. Add admin folder to your repo
2. Configure `site-config.json` for your site
3. Push to GitHub
4. Admin available at: `https://yourusername.github.io/yoursite/admin/`

### Option 2: Development Branch
1. Create a `dev` branch with admin tools
2. Use for content creation
3. Generated files get committed to `main` branch

## Production Notes

### Security
- **API Keys:** Stored encrypted in browser localStorage
- **File Access:** Admin only accesses files within website directory
- **CORS:** Configured for localhost development

### Performance
- **Lightweight:** No database required
- **Static:** Works with any static hosting
- **Caching:** Intelligent file caching for better performance

### Compatibility
- **Modern Browsers:** Chrome, Firefox, Safari, Edge
- **Mobile Responsive:** Works on tablets and phones
- **File System:** Requires local development server for file saving

## Troubleshooting

### Files Not Saving
1. Make sure you're using `dev-server.py` instead of `python -m http.server`
2. Check that the admin folder has write permissions
3. Verify the `articlesFolder` path in config

### AI Not Working
1. Check AI provider settings in admin/settings.html
2. For Ollama: ensure it's running on localhost:11434
3. For OpenAI/Gemini: verify API keys are entered

### Styling Issues
1. Update `branding` colors in `site-config.json`
2. Modify `admin/css/admin.css` for advanced customization
3. Check that your site's CSS doesn't conflict

## Support

This admin interface is designed to be:
- **Self-contained:** No external dependencies
- **Portable:** Works with any static site
- **Configurable:** Adapts to your workflow
- **Extensible:** Easy to modify and enhance

For issues or customization help, check the configuration files and console logs for debugging information.