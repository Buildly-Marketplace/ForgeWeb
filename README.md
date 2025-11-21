# ForgeWeb

**AI-Powered Static Site Generator for GitHub Pages**

ForgeWeb is a simple, powerful static site generator with a local admin interface. Build beautiful websites with AI assistance and deploy to GitHub Pages in minutes.

![ForgeWeb Logo](assets/forgeweb-logo-512.png)

> **👉 Quick Setup:** See [SETUP-REPO.md](SETUP-REPO.md) for the complete setup guide!

## 🏗️ Simple Architecture

ForgeWeb uses a clean, folder-based structure:

```
your-github-repo/              ← Your GitHub Pages repository
├── .gitignore                 ← Auto-generated (excludes ForgeWeb/)
├── website/                   ← Your content (deployed to GitHub Pages) ✅
│   ├── index.html
│   ├── articles/
│   └── assets/
└── ForgeWeb/                  ← Admin tools (NOT deployed) ❌
    ├── admin/
    └── start.sh
```

**How it works:**
1. Clone ForgeWeb, move it into your GitHub Pages repo
2. ForgeWeb creates a `website/` folder for your content
3. `.gitignore` excludes ForgeWeb from being committed
4. Deploy `website/` folder to GitHub Pages
5. Admin tools stay local on your machine

**Why this approach?**
- ✅ **Simple**: No Git submodules, no complex setup
- ✅ **Clean**: ForgeWeb admin never gets deployed
- ✅ **Portable**: Move ForgeWeb between projects easily
- ✅ **Beginner-Friendly**: Just clone, move, and start building

## 🚀 Features

### 🤖 AI-Powered Content Creation
- **AI Writing Assistant**: Generate high-quality articles with AI help
- **SEO Optimization**: Automatic meta tags, descriptions, and keyword suggestions
- **Social Media Posts**: Auto-generate engaging social media content
- **Content Enhancement**: Improve existing content with AI suggestions

### 📝 Intuitive Content Management
- **Visual Editor**: Rich text editor with live preview
- **Article Manager**: Organize and categorize your content
- **Page Builder**: Create custom pages with flexible templates
- **Media Management**: Upload and organize images and assets

### 🎨 Professional Design
- **Tailwind CSS**: Modern, responsive design framework
- **Mobile-First**: Optimized for all device sizes
- **Customizable Themes**: Easily customize colors and branding
- **SEO-Ready**: Built-in structured data and meta optimization

### 🚀 Easy Deployment
- **GitHub Pages**: One-click deployment to GitHub Pages
- **Local Development**: Built-in development server
- **Version Control**: Git-friendly file structure
- **CI/CD Ready**: Automated deployment workflows

## 📋 Quick Start

### Step 1: Clone ForgeWeb

```bash
git clone https://github.com/Buildly-Marketplace/ForgeWeb.git
```

### Step 2: Create Your GitHub Pages Repository

```bash
# On GitHub.com, create new repo: username.github.io (or any name)

# Clone it locally
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
cd YOUR-REPO

# Move ForgeWeb into your repo
mv ../ForgeWeb .
```

### Step 3: Start Building

```bash
cd ForgeWeb
./start.sh

# Open http://localhost:8000/admin/
```

That's it! ForgeWeb will auto-generate your homepage and create the `website/` folder.

## 🌐 Deploy to GitHub Pages

```bash
# Commit your website content
git add website/ .gitignore
git commit -m "Add website"
git push

# On GitHub: Settings → Pages → Deploy from /website folder
```

Your site goes live at `https://YOUR-USERNAME.github.io/YOUR-REPO/`

## 📋 Quick Start

### Prerequisites
- **Python 3.8 or higher** - [Download here](https://www.python.org/downloads/)
- **Web browser** (Chrome, Firefox, Safari, or Edge)
- That's it! 🎉

### Get Started in 30 Seconds

1. **Download or Clone ForgeWeb**
   ```bash
   git clone https://github.com/buildlyio/forgeweb.git
   cd forgeweb
   ```

2. **Run the Startup Wizard**
   
   **On Linux/Mac:**
   ```bash
   ./start.sh
   ```
   
   **On Windows:**
   ```cmd
   start.bat
   ```
   
   That's all! The script will:
   - ✅ Set up a virtual environment
   - ✅ Install required packages
   - ✅ Start the local server
   - ✅ Open at `http://localhost:8000/admin/`

3. **Start Building Your Site!**
   - Your browser will guide you through the admin interface
   - All changes are saved automatically
   - Press `Ctrl+C` to stop the server when done

### Restart the Server

Just run the start script again - it remembers everything!

- Linux/Mac: `./start.sh`
- Windows: `start.bat`

For detailed installation instructions and troubleshooting, see [INSTALL.md](INSTALL.md).

## 📂 File Structure & Deployment

ForgeWeb keeps your admin tools separate from your website content:

```
YourProject/
├── ForgeWeb/           # Admin tools (local only, not deployed)
│   ├── admin/         # Admin interface
│   │   ├── index.html     # Dashboard
│   │   ├── editor.html    # Content editor
│   │   ├── forgeweb.db    # SQLite database (settings, metadata)
│   │   ├── site-config.json  # Site configuration (backup)
│   │   └── database.py    # Database manager
│   ├── index.html     # Redirect to admin (local only)
│   └── templates/     # Page templates (local only)
│
└── website/            # YOUR WEBSITE CONTENT (gets deployed!)
    ├── index.html     # YOUR SITE'S HOMEPAGE (deployed)
    ├── 404.html       # Error page (deployed)
    ├── articles/      # Your blog posts (deployed)
    └── assets/        # CSS, images, JS (deployed)
        ├── css/
        ├── images/
        └── js/
```

**Important:** 
- Your website content is saved to the **`website/` directory** - this is what gets deployed!
- The `ForgeWeb/` folder stays local - it's your control panel
- **Settings are stored in SQLite database** (`ForgeWeb/admin/forgeweb.db`) - never deployed
- Your chosen design system, site config, and metadata are in the database
- Only the `website/` directory contents get deployed to GitHub Pages

📖 **See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions and best practices.**

## 📚 Documentation

- **[SETUP-REPO.md](SETUP-REPO.md)** - Complete guide for setting up your website repository
- **[SUBMODULE-GUIDE.md](SUBMODULE-GUIDE.md)** - Quick reference for the submodule architecture
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed explanation of how ForgeWeb works
- **[DEPLOYMENT.md](admin/DEPLOYMENT.md)** - Deploy your site to GitHub Pages
- **[QUICKSTART.md](QUICKSTART.md)** - 3-step quick start guide

## 🎯 Use Cases

### 📰 Blog & Articles
Perfect for creating and managing blog content with AI assistance:
- Generate article ideas and outlines
- Create SEO-optimized content
- Manage categories and tags
- Auto-generate social media posts

### 🏢 Business Websites
Build professional business sites:
- Landing pages with conversion focus
- Service and product pages
- About and team pages
- Contact and pricing pages

### 📚 Documentation Sites
Create comprehensive documentation:
- Technical guides and tutorials
- API documentation
- User manuals
- Knowledge bases

### 🎨 Portfolio Sites
Showcase your work:
- Project galleries
- Case studies
- Professional profiles
- Creative portfolios

## 🏗️ Architecture

ForgeWeb uses a simple but powerful architecture:

```
ForgeWeb/
├── admin/              # Local admin interface
│   ├── index.html     # Dashboard
│   ├── editor.html    # Article editor
│   ├── page-editor.html # Page editor
│   └── js/            # Admin functionality
├── articles/          # Generated articles (output)
├── assets/           # Images, media files
└── *.html           # Generated pages (output)
```

### How It Works
1. **Create Content**: Use the admin interface to write articles and pages
2. **AI Enhancement**: Let AI help optimize your content for SEO and engagement
3. **Generate Files**: ForgeWeb creates static HTML files ready for deployment
4. **Deploy**: Push to GitHub Pages or any static hosting provider

## 🔧 Configuration

ForgeWeb is configured through `admin/site-config.json`:

```json
{
  "site": {
    "name": "Your Site Name",
    "url": "https://yoursite.com",
    "description": "Your site description"
  },
  "content": {
    "articlesFolder": "articles/",
    "categories": [
      {"id": "tech", "name": "Technology"},
      {"id": "business", "name": "Business"}
    ]
  },
  "branding": {
    "primaryColor": "#1b5fa3",
    "secondaryColor": "#144a84"
  }
}
```

## 🤖 AI Integration

ForgeWeb supports multiple AI providers:

- **OpenAI GPT**: Industry-leading content generation
- **Anthropic Claude**: Advanced reasoning and writing
- **Local LLMs**: Run models locally for privacy
- **Custom Endpoints**: Integrate your own AI services

Configure your AI provider in the admin settings to unlock:
- Content generation and enhancement
- SEO optimization suggestions
- Social media post creation
- Writing style improvements

## 📱 Social Media Integration

Generate engaging social media content automatically:

- **Platform-Specific**: Optimized for Twitter, LinkedIn, Facebook
- **Character Limits**: Respects platform constraints
- **Hashtag Generation**: Relevant hashtags for your content
- **Multiple Variations**: Generate several options to choose from

## 🎨 Customization

### Themes and Styling
- Built on Tailwind CSS for easy customization
- Modify colors, fonts, and layouts through configuration
- Custom CSS support for advanced styling
- Responsive design ensures mobile compatibility

### Content Types
- Articles and blog posts
- Static pages (About, Contact, etc.)
- Landing pages
- Portfolio showcases
- Documentation pages

## 📊 SEO & Analytics

### Built-in SEO Features
- Automatic meta tag generation
- Structured data (JSON-LD)
- Open Graph and Twitter Cards
- XML sitemap generation
- Canonical URLs

### Analytics Support
- Google Analytics integration
- Plausible Analytics support
- Custom analytics providers
- Privacy-compliant tracking options

## 🚀 Deployment Options

### GitHub Pages (Recommended)
- Free hosting for public repositories
- Automatic deployments with GitHub Actions
- Custom domain support
- SSL certificates included

### Other Hosting Providers
- Netlify
- Vercel
- Cloudflare Pages
- Any static hosting provider

## 🔒 Privacy & Security

- **Local-First**: Admin interface runs locally
- **No Data Collection**: ForgeWeb doesn't collect user data
- **GDPR Compliant**: Built-in privacy considerations
- **Secure by Default**: Static sites are inherently secure

## 🛠️ Development

### Technology Stack
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Styling**: Tailwind CSS
- **Backend**: Python (for local admin server)
- **AI Integration**: REST APIs for various providers
- **Deployment**: Static files (no server required)

### Contributing
We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on:
- Code standards
- Pull request process
- Issue reporting
- Feature requests

## 📚 Documentation

- **[Installation Guide](INSTALL.md)**: Detailed setup instructions
- **[User Manual](docs/USER_GUIDE.md)**: Complete feature documentation
- **[API Reference](docs/API.md)**: Integration and customization
- **[Deployment Guide](docs/DEPLOYMENT.md)**: Hosting options and setup

## 🆘 Support

### Community Support (Free)
- [GitHub Discussions](https://github.com/buildlyio/forgeweb/discussions)
- [Documentation](https://docs.buildly.io/forgeweb)
- [Issue Tracker](https://github.com/buildlyio/forgeweb/issues)

### Priority Support (Paid)
- **Response Time**: < 1 business day
- **Resolution Target**: 3 business days (best effort)
- **Scope**: Installation, configuration, first deployment
- **Access**: Direct chat support in Buildly Labs

[**Request Partner Help**](https://collab.buildly.io/marketplace) for custom development and advanced integrations.

## 📄 License

ForgeWeb is licensed under the Business Source License 1.1 (BSL-1.1). This means:

- **Free to use** for development, testing, and non-production purposes
- **Free for small businesses** (under specific revenue thresholds)
- **Commercial license available** for larger organizations
- **Converts to Apache 2.0** on October 20, 2027

See [LICENSE.md](LICENSE.md) for full details.

## 🏢 About Buildly

ForgeWeb is developed by [Buildly](https://buildly.io), the AI-powered product development platform. Buildly helps teams build better products faster with:

- **Buildly Core**: Rapid API development framework
- **Buildly Labs**: AI-assisted development tools
- **Collab Hub**: Expert developer marketplace

---

**Ready to get started?** Check out the [Installation Guide](INSTALL.md) or try ForgeWeb today!

[![Deploy to GitHub Pages](https://img.shields.io/badge/Deploy-GitHub%20Pages-brightgreen)](https://github.com/buildlyio/forgeweb-template/generate)
[![Docker](https://img.shields.io/badge/Docker-Available-blue)](https://github.com/buildlyio/forgeweb/pkgs/container/forgeweb)
[![License](https://img.shields.io/badge/License-BSL--1.1-orange)](LICENSE.md)