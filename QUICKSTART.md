# 🚀 Quick Start Guide - ForgeWeb

**Welcome to ForgeWeb!** This is the easiest way to create a website and deploy it to GitHub Pages.

## ⚡ Start in 3 Steps

### 1️⃣ Make sure you have Python installed

Check if you have Python 3.8 or higher:

```bash
python3 --version
```

**Don't have Python?** Download it here: https://www.python.org/downloads/

- ✅ **Windows**: Download and install (check "Add Python to PATH")
- ✅ **Mac**: Use `brew install python3` or download from python.org
- ✅ **Linux**: `sudo apt install python3 python3-pip python3-venv`

### 2️⃣ Run the startup script

Open a terminal/command prompt in the ForgeWeb folder and run:

**Linux/Mac:**
```bash
./start.sh
```

**Windows:**
```cmd
start.bat
```

The script will automatically:
- ✅ Create a virtual environment
- ✅ Install all needed packages
- ✅ Set up folders and configuration
- ✅ Start the local server

### 3️⃣ Open your browser

Go to: **http://localhost:8000/admin/**

You'll see:
- **http://localhost:8000/** - A welcome page with a link to the admin
- **http://localhost:8000/admin/** - The admin dashboard where you build your site

That's it! You're ready to build your website! 🎉

---

## 💡 Common Tasks

### Stop the server
Press `Ctrl+C` in the terminal

### Start the server again
Just run the same start script again:
- Linux/Mac: `./start.sh`
- Windows: `start.bat`

### Build your first page
1. Go to http://localhost:8000/admin/
2. Click "Pages" → "New Page"
3. Fill in your content
4. Click "Save" or "Publish"

### Deploy to GitHub Pages
1. Create a GitHub repository for your site
2. In the ForgeWeb admin, go to "Settings" → "GitHub"
3. Enter your repository details
4. Click "Deploy"

---

## 🆘 Need Help?

### "Python 3 is not installed"
→ Install Python from https://www.python.org/downloads/

### "Permission denied" on Linux/Mac
→ Run: `chmod +x start.sh` then `./start.sh`

### "Port 8000 is already in use"
→ The script will detect this and offer to restart the server

### Server won't start
1. Check you're in the ForgeWeb folder
2. Check Python version: `python3 --version` (needs 3.8+)
3. Check the terminal for error messages

### Still stuck?
- See the detailed [INSTALL.md](INSTALL.md) guide
- Check [README.md](README.md) for more features

---

## 📚 What's Next?

Once you're up and running:

1. **Explore the Admin Interface**
   - Dashboard shows your site overview
   - Article Manager for blog posts
   - Page Editor for creating pages
   - Settings for customization

2. **Create Content**
   - Write articles with the rich editor
   - Build custom pages
   - Upload images and media
   - Use AI assistance (if configured)

3. **Customize Your Site**
   - Choose colors and fonts
   - Edit navigation menu
   - Add your logo
   - Set up social media links

4. **Understand File Storage**
   - **Content files** (pages, articles) are saved to the ForgeWeb root directory
   - **Admin files** stay in the `admin/` folder (not deployed)
   - **Your chosen design system** is saved in `admin/site-config.json`
   - Everything is ready for GitHub Pages deployment!

5. **Deploy Online**
   - Push to GitHub
   - Enable GitHub Pages
   - Your site goes live!
   - See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions

---

**Happy building! 🎨✨**

For more details, see:
- [README.md](README.md) - Full documentation
- [INSTALL.md](INSTALL.md) - Detailed installation guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Complete deployment guide
