# 🚀 ForgeWeb Setup Guide

## Quick Start (3 Steps)

### 1. Clone ForgeWeb
```bash
git clone https://github.com/Buildly-Marketplace/ForgeWeb.git
```

### 2. Create Your GitHub Pages Repository
```bash
# On GitHub.com, create a new repository named: username.github.io
# (or any name for a project site)

# Clone your new repository
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
cd YOUR-REPO

# Move ForgeWeb into your repository
mv ../ForgeWeb .
```

### 3. Start Building
```bash
cd ForgeWeb
./start.sh

# Open http://localhost:8000/admin/
```

That's it! ForgeWeb will:
- Create a `website/` folder for your content
- Generate a `.gitignore` that excludes ForgeWeb from deployment
- Auto-create your homepage when you choose a design system

## 📁 Repository Structure

After setup, your repository looks like this:

```
your-github-repo/              ← Your GitHub Pages repository
├── .git/
├── .gitignore                 ← Auto-generated (excludes ForgeWeb/)
├── README.md                  ← Your project README
├── website/                   ← Deployed to GitHub Pages ✅
│   ├── index.html
│   ├── about.html
│   ├── articles/
│   │   └── my-post.html
│   └── assets/
│       ├── css/
│       └── images/
└── ForgeWeb/                  ← Admin tools (NOT deployed) ❌
    ├── admin/
    │   ├── index.html         ← Admin dashboard
    │   ├── editor.html        ← Article editor
    │   └── forgeweb.db        ← Local database
    ├── templates/
    └── start.sh
```

## 📤 Deploying to GitHub Pages

### Step 1: Commit Your Content

```bash
# In your repository root (not inside ForgeWeb/)
cd ~/path/to/your-github-repo

# Check what's being tracked
git status
# You should see website/ files, NOT ForgeWeb/ (it's gitignored)

# Commit your content
git add website/
git add .gitignore
git commit -m "Add website content"
git push
```

### Step 2: Configure GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Under **Build and deployment**:
   - **Source**: Deploy from a branch
   - **Branch**: `main`
   - **Folder**: `/website`  ← Important: Select /website, not / (root)
4. Click **Save**

Your site will be live at:
- User site: `https://YOUR-USERNAME.github.io/`
- Project site: `https://YOUR-USERNAME.github.io/YOUR-REPO/`

## ✅ What Gets Deployed vs Not Deployed

### Deployed to GitHub Pages (✅):
- `website/index.html` - Your homepage
- `website/about.html`, `website/contact.html` - Your pages
- `website/articles/` - Blog posts
- `website/assets/` - CSS, images, JavaScript
- All files in the `website/` folder

### NOT Deployed (❌):
- `ForgeWeb/` - Admin tools (excluded by .gitignore)
- `ForgeWeb/admin/forgeweb.db` - Database (local only)
- `ForgeWeb/admin/` - Admin dashboard
- Any Python files or admin scripts

## 🔄 Cloning on Another Computer

When you clone your repository on another machine:

```bash
# Clone your repository
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
cd YOUR-REPO

# ForgeWeb folder is already there (not a submodule)
# Just start the server
cd ForgeWeb
./start.sh
```

## 🔧 Updating ForgeWeb

To get the latest ForgeWeb features:

```bash
cd ~/path/to/your-repo/ForgeWeb

# Pull latest updates
git pull origin main

# Restart the server
./start.sh
```

## 💡 Why This Structure?

This approach is **simpler than Git submodules** because:
1. ✅ Clone ForgeWeb once, move it into your repo
2. ✅ `.gitignore` excludes ForgeWeb from commits
3. ✅ Only `website/` folder gets deployed
4. ✅ No submodule complexity
5. ✅ Easy to understand and maintain

## 📝 What Gets Deployed vs What Stays Local

### ✅ Deployed to GitHub Pages (in `my-website/`):
- `index.html` - Your homepage
- `about.html`, `contact.html` - Your pages
- `articles/` - Blog posts
- `assets/` - CSS, images, JavaScript
- All HTML files you create

### ❌ NOT Deployed (in `ForgeWeb/` submodule):
- `ForgeWeb/admin/` - Admin dashboard
- `ForgeWeb/admin/forgeweb.db` - SQLite database
- `ForgeWeb/templates/` - Page templates
- `ForgeWeb/start.sh` - Startup scripts
- All ForgeWeb admin tools

## 🎨 How It Works

1. **ForgeWeb admin tools** are in the `ForgeWeb/` submodule (not deployed)
2. **Your website files** are saved to the parent directory (deployed)
3. **GitHub Pages** only sees and deploys the parent directory
4. **The database** and all admin settings stay local in `ForgeWeb/admin/`

## 🆘 Troubleshooting

### ForgeWeb submodule is empty after cloning
```bash
git submodule update --init --recursive
```

### Changes to website not showing on GitHub Pages
```bash
# Make sure you're committing website files, not ForgeWeb files
git add index.html articles/ assets/
git commit -m "Update website content"
git push
```

### Want to move existing ForgeWeb setup
```bash
# If you have ForgeWeb in the wrong location:
cd ~/Projects
mkdir my-website
cd my-website
git init

# Move your content files to the new location
mv ~/old-location/*.html .
mv ~/old-location/articles .
mv ~/old-location/assets .

# Add ForgeWeb as submodule
git submodule add https://github.com/Buildly-Marketplace/ForgeWeb.git ForgeWeb
```

## 📚 Additional Resources

- [Git Submodules Documentation](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [ForgeWeb Documentation](https://github.com/Buildly-Marketplace/ForgeWeb)
