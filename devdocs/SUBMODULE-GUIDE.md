# 📋 ForgeWeb Submodule Architecture - Quick Reference

## What Changed?

ForgeWeb now uses a **Git submodule** structure instead of a separate `website/` directory. This is cleaner and follows standard Git practices.

## Directory Structure

### Old Structure (❌ Deprecated):
```
ForgeWeb/
├── admin/          ← Admin tools
├── website/        ← User content
└── templates/
```

### New Structure (✅ Current):
```
your-website/       ← Your main Git repository
├── .git/
├── index.html      ← Your homepage
├── articles/       ← Your blog posts
├── assets/         ← Your CSS, images
└── ForgeWeb/       ← Git submodule (admin tools)
    ├── .git/       ← Separate Git repo
    ├── admin/      ← Admin dashboard
    └── templates/  ← Page templates
```

## Key Benefits

1. **Clean Deployment**: Only `your-website/` gets deployed, ForgeWeb stays local
2. **Easy Setup**: `git submodule add https://github.com/Buildly-Marketplace/ForgeWeb.git`
3. **Portable**: Clone your site anywhere, ForgeWeb comes along
4. **Updates**: `cd ForgeWeb && git pull` to update admin tools
5. **Standard Practice**: Uses Git's built-in submodule system

## How Files Are Saved

| Content Type | File Path | Deployed? |
|---|---|---|
| Homepage | `../index.html` | ✅ Yes |
| Pages | `../about.html`, `../contact.html` | ✅ Yes |
| Articles | `../articles/my-post.html` | ✅ Yes |
| Assets | `../assets/images/logo.png` | ✅ Yes |
| Database | `ForgeWeb/admin/forgeweb.db` | ❌ No (local only) |
| Admin Tools | `ForgeWeb/admin/` | ❌ No (submodule) |

## Setup Commands

### For New Projects:
```bash
mkdir my-website
cd my-website
git init
git submodule add https://github.com/Buildly-Marketplace/ForgeWeb.git
cd ForgeWeb
./start.sh
```

### For Existing Projects:
```bash
cd ~/Projects/my-website
git submodule add https://github.com/Buildly-Marketplace/ForgeWeb.git
cd ForgeWeb
./start.sh
```

### Cloning Your Site:
```bash
git clone https://github.com/you/your-website.git
cd your-website
git submodule update --init --recursive
cd ForgeWeb
./start.sh
```

## Code Changes

### file-api.py Path Resolution:
```python
# Old (website/ directory):
self.website_root = os.path.join(parent_dir, 'website')

# New (submodule - parent directory):
forge_web_dir = os.path.dirname(self.admin_dir)  # ForgeWeb/
self.website_root = os.path.dirname(forge_web_dir)  # your-website/
```

### Where Files Are Created:
- **Old**: `ForgeWeb/website/index.html`
- **New**: `your-website/index.html` (parent of ForgeWeb/)

## GitHub Pages Deployment

```bash
# In your website directory (NOT ForgeWeb!)
cd ~/Projects/my-website

# Commit your content
git add index.html articles/ assets/
git commit -m "Update website"
git push

# GitHub Pages automatically deploys the parent directory
# ForgeWeb submodule is NOT deployed
```

## Documentation Files

- **SETUP-REPO.md** - Complete repository setup guide
- **ARCHITECTURE.md** - Detailed architecture explanation
- **DEPLOYMENT.md** - GitHub Pages deployment guide
- **README.md** - Updated with submodule structure

## Testing the Setup

1. Start server: `cd ForgeWeb && ./start.sh`
2. Check startup message shows correct paths:
   ```
   ForgeWeb Directory:  /path/to/your-website/ForgeWeb/
   Website Directory:   /path/to/your-website/
   ```
3. Choose design system (e.g., Bootstrap)
4. Verify `index.html` created at `your-website/index.html` (NOT inside ForgeWeb)
5. Navigate to `http://localhost:8000/` - should show your homepage
6. Navigate to `http://localhost:8000/admin/` - should show admin dashboard

## What Gets Committed Where

### Your Website Repository:
```bash
git add index.html articles/ assets/
git commit -m "Add content"
```
Commits: ✅ HTML, ✅ articles, ✅ assets, ✅ .gitignore, ✅ submodule reference

### ForgeWeb Submodule:
```bash
# Typically you DON'T commit here
# Updates come from upstream via git pull
```
Commits: ✅ Admin code, ✅ templates, ❌ database (gitignored)

## Migration Guide (if you have existing setup)

If you were using the old `website/` directory structure:

```bash
# 1. Navigate to parent directory
cd ~/Projects/buildly/startupinaday

# 2. Create new website repo
mkdir my-website
cd my-website
git init

# 3. Move content from old location
mv ../ForgeWeb/website/* .

# 4. Add ForgeWeb as submodule
git submodule add https://github.com/Buildly-Marketplace/ForgeWeb.git

# 5. Start using it
cd ForgeWeb
./start.sh
```

## Troubleshooting

### "ForgeWeb directory is empty"
```bash
git submodule update --init --recursive
```

### "Files not saving to parent directory"
Check startup message shows correct paths. Should say:
```
Website Directory: /path/to/your-website/
```

### "ForgeWeb appearing in GitHub Pages"
Check `.gitmodules` file exists:
```ini
[submodule "ForgeWeb"]
	path = ForgeWeb
	url = https://github.com/Buildly-Marketplace/ForgeWeb.git
```

## Summary

✅ **Cleaner** - Standard Git submodule practice  
✅ **Simpler** - No separate `website/` directory  
✅ **Portable** - Easy to clone and share  
✅ **Standard** - Follows Git best practices  
✅ **Deployable** - Only parent directory goes to GitHub Pages
