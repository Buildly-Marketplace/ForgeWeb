# My Website

Built with [ForgeWeb](https://github.com/Buildly-Marketplace/ForgeWeb) - an AI-powered static site generator.

## 🌐 Live Site

Visit: [https://YOUR-USERNAME.github.io/YOUR-REPO/](https://YOUR-USERNAME.github.io/YOUR-REPO/)

## 🛠️ Local Development

### Start the Admin Dashboard

```bash
cd ForgeWeb
./start.sh
```

Then open `http://localhost:8000/admin/` in your browser.

### Edit Content

- **Pages:** Use Page Editor to create/edit static pages
- **Articles:** Use Article Editor for blog posts
- **Design:** Customize colors and branding in Branding Manager

### Preview Changes

Visit `http://localhost:8000/` to see your site locally before deploying.

## 📤 Deploying Changes

```bash
# Commit your changes
git add website/
git commit -m "Update content"
git push
```

GitHub Pages will automatically rebuild your site (takes 1-2 minutes).

## 📁 Project Structure

```
├── website/          ← Your website (deployed to GitHub Pages)
│   ├── index.html
│   ├── articles/
│   └── assets/
└── ForgeWeb/        ← Admin tools (not deployed)
    └── admin/
```

## 🔧 Updating ForgeWeb

To get the latest ForgeWeb features:

```bash
cd ForgeWeb
git pull origin main
```

## 📚 Learn More

- [ForgeWeb Documentation](https://github.com/Buildly-Marketplace/ForgeWeb)
- [Quick Start Guide](ForgeWeb/QUICK-START.md)
- [Setup Guide](ForgeWeb/SETUP-REPO.md)
