# ForgeWeb Quick Reference

Quick commands and common tasks for ForgeWeb development.

## 🚀 Start/Stop Server

```bash
# Start the server
./start.sh              # Linux/Mac
start.bat               # Windows

# Stop the server
Ctrl+C                  # In terminal
```

Server runs at: `http://localhost:8000/admin/`

## 📂 Folder Structure

```
forgeweb/
├── devdocs/           # All documentation (you are here!)
├── admin/             # Admin interface
│   ├── *.html        # Admin pages
│   ├── js/           # Admin JavaScript
│   └── css/          # Admin styles
├── assets/            # Template assets (copied to website)
│   ├── css/          # Source CSS
│   └── js/           # Source JS
├── templates/         # Page templates
└── website/           # Generated static site
    ├── index.html    # Pages (deployed to GitHub)
    ├── assets/       # CSS/JS (auto-updated)
    └── articles/     # Blog posts
```

## 🎨 Update Branding

When you change branding in the admin:
- `website/assets/css/custom.css` updates automatically
- All pages reflect new colors/fonts immediately
- Just commit and push the CSS file

## 🔧 Update Navigation

When you add/remove pages:
- `website/assets/js/site-config.js` updates automatically
- Navigation appears on all pages
- Just commit and push the JS file

## 📝 Common Tasks

### Create a New Page
1. Go to Admin → Page Editor
2. Create new page
3. Save (auto-creates HTML in `website/`)
4. Commit: `git add website/ && git commit -m "Add page"`

### Update Branding Colors
1. Go to Admin → Branding Manager
2. Change colors
3. Save (auto-updates `custom.css`)
4. Commit: `git add website/assets/ && git commit -m "Update branding"`

### Add Social Media Links
1. Go to Admin → Settings
2. Update social media handles
3. Save (auto-updates `site-config.js`)
4. Commit: `git add website/assets/ && git commit -m "Update social links"`

### Deploy to GitHub Pages
```bash
# Add all website changes
git add website/ .gitignore

# Commit
git commit -m "Update site"

# Push
git push origin main

# On GitHub: Settings → Pages → Deploy from /website
```

## 🐛 Troubleshooting

### Server won't start?
```bash
# Recreate virtual environment
rm -rf venv
./start.sh
```

### Changes not showing?
```bash
# Hard refresh browser
Ctrl+F5           # Windows/Linux
Cmd+Shift+R       # Mac
```

### Port 8000 in use?
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9    # Mac/Linux
netstat -ano | findstr :8000     # Windows
```

## 📚 Documentation

- **[Installation](INSTALL.md)** - Setup guide
- **[Architecture](ARCHITECTURE.md)** - System design
- **[Branding](BRANDING.md)** - Branding system
- **[Static Assets](STATIC-ASSETS.md)** - CSS/JS management
- **[Deployment](DEPLOYMENT.md)** - Publishing guide

## 🔗 Quick Links

- Admin: `http://localhost:8000/admin/`
- Preview: `http://localhost:8000/`
- API: `http://localhost:8000/api/`

## 💡 Tips

- **Use CSS variables** - Reference `var(--brand-primary)` not hex colors
- **Keep custom CSS minimal** - Let the system manage styles
- **Commit often** - Small changes are easier to track
- **Test locally first** - Preview before deploying
- **Check browser console** - Helpful for debugging

## 🎯 Development Workflow

1. Start server: `./start.sh`
2. Make changes in admin
3. Preview at `http://localhost:8000/`
4. Test thoroughly
5. Commit changes: `git add website/`
6. Push to GitHub
7. Verify on GitHub Pages

---

**Need more help?** Check the full docs in [devdocs/](.)
