# ⚡ ForgeWeb Quick Start

Get your GitHub Pages site running in 5 minutes!

## 🎯 The 3-Step Setup

### 1️⃣ Clone ForgeWeb

```bash
git clone https://github.com/Buildly-Marketplace/ForgeWeb.git
```

### 2️⃣ Create Your GitHub Pages Repo

On GitHub.com, create a new repository:
- **For a user/org site:** Name it `username.github.io`
- **For a project site:** Name it anything (e.g., `my-awesome-site`)

Then clone it:

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
cd YOUR-REPO
```

### 3️⃣ Move ForgeWeb & Start

```bash
# Move ForgeWeb into your repo
mv ../ForgeWeb .

# Start the server
cd ForgeWeb
./start.sh
```

Open `http://localhost:8000/admin/` and start building! 🚀

## 📁 What You Get

After setup, your repository looks like this:

```
YOUR-REPO/
├── .git/                    ← Your Git repository
├── .gitignore               ← Auto-created (excludes ForgeWeb/)
├── README.md                ← Your project README
├── website/                 ← Your website (deployed to GitHub Pages)
│   ├── index.html          ← Homepage (auto-generated)
│   ├── articles/           ← Blog posts
│   └── assets/             ← Images, CSS
└── ForgeWeb/               ← Admin tools (NOT deployed)
    ├── admin/              ← Local admin dashboard
    └── start.sh            ← Start script
```

## 🎨 First Steps in Admin

1. **Choose Design System**
   - Auto-prompts when you first visit admin
   - Pick Tailwind, Bootstrap, Bulma, or others
   - Your homepage is auto-generated!

2. **Create Content**
   - **Pages:** Use Page Editor for static pages (About, Contact, etc.)
   - **Articles:** Use Article Editor for blog posts
   - **AI Help:** Click AI helper for content suggestions

3. **Customize Design**
   - **Branding Manager:** Set colors, fonts, logo
   - **Navigation Manager:** Configure menu links
   - Files save automatically to `website/` folder

## 🚀 Deploy to GitHub Pages

### Step 1: Commit Your Content

```bash
# In your repo root (not inside ForgeWeb/)
cd ~/path/to/YOUR-REPO

# Check what's tracked (website/ should show, ForgeWeb/ should not)
git status

# Commit everything
git add .
git commit -m "Initial website commit"
git push
```

### Step 2: Enable GitHub Pages

1. Go to your repo on GitHub
2. Click **Settings** → **Pages**
3. Under **Build and deployment**:
   - **Source:** Deploy from a branch
   - **Branch:** `main`
   - **Folder:** `/website` ← **Important!**
4. Click **Save**

### Step 3: Visit Your Site! 🎉

Your site will be live at:
- User site: `https://YOUR-USERNAME.github.io/`
- Project site: `https://YOUR-USERNAME.github.io/YOUR-REPO/`

(GitHub takes 1-2 minutes to build and deploy)

## 💡 How It Works

### The Magic of .gitignore

ForgeWeb auto-creates a `.gitignore` file that excludes:
- `ForgeWeb/` - Admin tools
- `*.db` - Local database
- `admin/` - Admin files
- Python cache files

**Result:** Only the `website/` folder gets committed and deployed!

### File Saving

When you create content in the admin dashboard:
- Pages → `website/index.html`, `website/about.html`
- Articles → `website/articles/my-post.html`
- Assets → `website/assets/images/logo.png`

### Deployment

GitHub Pages serves files from the `/website` folder:
- ✅ `website/index.html` → `yoursite.com/index.html`
- ✅ `website/articles/post.html` → `yoursite.com/articles/post.html`
- ❌ `ForgeWeb/` → Not deployed (gitignored)

## 🔧 Common Tasks

### Create a New Page

1. Open `http://localhost:8000/admin/`
2. Click **Page Editor**
3. Write content, click **Save**
4. File saved to `website/your-page.html`
5. Commit and push to deploy

### Write a Blog Post

1. Click **Article Editor**
2. Write your post (use AI helper for ideas!)
3. Click **Save**
4. File saved to `website/articles/your-post.html`
5. Commit and push

### Change Colors/Fonts

1. Click **Branding Manager**
2. Pick your colors and fonts
3. Changes apply immediately
4. CSS saved to `website/assets/css/custom.css`

### Update ForgeWeb

```bash
cd YOUR-REPO/ForgeWeb
git pull origin main
./start.sh
```

## 🆘 Troubleshooting

### Port 8000 already in use?

```bash
# Use a different port
cd ForgeWeb/admin
python file-api.py --port 8001
```

### Files not showing in Git?

Check your `.gitignore` - make sure it excludes `ForgeWeb/` but NOT `website/`

### Website not deploying?

1. Make sure GitHub Pages is set to deploy from `/website` folder
2. Check that `website/index.html` exists
3. Wait 1-2 minutes for GitHub to build

### Want to move ForgeWeb to another project?

```bash
# Just copy the ForgeWeb folder
cp -r path/to/old-project/ForgeWeb path/to/new-project/
cd path/to/new-project/ForgeWeb
./start.sh
```

## 📚 Learn More

- **[SETUP-REPO.md](SETUP-REPO.md)** - Detailed setup instructions
- **[DEPLOYMENT.md](admin/DEPLOYMENT.md)** - Deployment guide
- **[README.md](README.md)** - Full feature documentation

## 🎓 Pro Tips

1. **Use Design System:** Choose one on first visit - makes page creation much easier
2. **AI Helper:** Great for getting started with content ideas
3. **Preview Before Deploy:** Use "View Site" link in admin to preview locally
4. **Commit Often:** Make small commits so you can roll back if needed
5. **Custom Domain:** Add a `CNAME` file to `website/` folder for custom domains

---

**That's it!** You're ready to build amazing websites with ForgeWeb. Happy building! 🚀
