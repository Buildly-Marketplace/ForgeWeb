# Static Assets System

## How It Works

ForgeWeb generates a **truly static website** that can be published to GitHub Pages. When you update branding, navigation, or social media settings, it updates **shared CSS and JavaScript files** that are included on all pages. This means:

✅ **No regeneration needed** - Update branding once, all pages change  
✅ **GitHub Pages compatible** - Pure static HTML/CSS/JS  
✅ **Fast and efficient** - Shared files cached by browsers  
✅ **Easy to maintain** - One CSS file, one JS file, all pages use them  

## File Structure

```
website/
├── index.html          ← Includes shared assets
├── about.html          ← Includes shared assets  
├── contact.html        ← Includes shared assets
└── assets/
    ├── css/
    │   └── custom.css  ← **SHARED** - All branding/styles here
    └── js/
        ├── site-config.js  ← **SHARED** - Navigation & social media
        └── site.js         ← **SHARED** - Utility functions
```

## Shared Files

### 1. `assets/css/custom.css`
**Auto-updated when branding changes**

Contains:
- CSS variables with your brand colors
- Button styles  
- Navigation styles
- Card hover effects
- Typography settings
- Custom CSS you add

Example:
```css
:root {
    --brand-primary: #1b5fa3;
    --brand-secondary: #144a84;
    --brand-accent: #f9943b;
}

.btn-brand {
    background-color: var(--brand-primary);
    /* ... */
}
```

**When you change branding colors** in the admin, this file updates automatically, and ALL pages reflect the new colors immediately.

### 2. `assets/js/site-config.js`
**Auto-updated when navigation or social media changes**

Contains:
- Site name
- Navigation menu items
- Social media links
- Current year for copyright

Example:
```javascript
const SITE_CONFIG = {
    siteName: "My Website",
    navigation: [
        { title: 'Home', url: 'index.html' },
        { title: 'About', url: 'about.html' },
        { title: 'Contact', url: 'contact.html' }
    ],
    social: {
        twitter: '@myhandle',
        linkedin: 'mycompany'
    }
};
```

**When you add/remove pages** or update social media, this file updates, and navigation appears on ALL pages.

### 3. `assets/js/site.js`
**Static utility functions**

Contains:
- Mobile menu toggle
- Smooth scrolling
- Share functionality
- Lazy image loading

## How Updates Work

### Updating Branding
1. Change colors/fonts in Branding Manager
2. Click "Save"
3. System updates `assets/css/custom.css`
4. **All pages automatically use new branding** ✨

### Updating Navigation
1. Add/remove pages in Site Setup
2. Click "Generate Site"
3. System updates `assets/js/site-config.js`
4. **All pages show new navigation** ✨

### Updating Social Media
1. Change social media handles in settings
2. Save configuration
3. System updates `assets/js/site-config.js`
4. **All pages show new social links** ✨

### Updating Logo
1. Upload logo in Branding Manager
2. Set logo path (e.g., `assets/images/logo.png`)
3. System updates configuration
4. Regenerate pages OR manually update logo reference
5. **All pages show new logo**

## What Requires Regeneration?

### ✅ NO Regeneration Needed:
- Changing brand colors
- Changing fonts  
- Updating social media handles
- Adding custom CSS
- Modifying navigation (if using JS navigation)

### ⚠️ Regeneration Required:
- Adding entirely new pages
- Changing page titles
- Updating meta descriptions
- Modifying page content
- Changing site structure

## Publishing to GitHub Pages

1. **Initial Setup:**
   - Generate your site
   - Commit the `website/` folder to GitHub
   - Enable GitHub Pages in repo settings
   - Point to `website/` folder or root

2. **After Branding Changes:**
   - Commit updated `website/assets/css/custom.css`
   - Commit updated `website/assets/js/site-config.js`  
   - Push to GitHub
   - Changes appear immediately (no build required)

3. **After Adding Pages:**
   - Generate new pages
   - Commit all updated files
   - Push to GitHub

## Benefits of This Approach

### Traditional Static Site Generator:
```
Change branding → Rebuild entire site → 100 files changed
```

### ForgeWeb Approach:
```
Change branding → Update 1 CSS file → 1 file changed ✨
```

### Why This Matters:
- **Faster commits** - Only 1-2 files change
- **Clearer git history** - See exactly what changed
- **Faster deployments** - GitHub Pages updates quickly
- **Browser caching** - Shared files cached across pages
- **Easy debugging** - One file to check for styles

## Advanced Usage

### Adding Custom CSS

In Branding Manager, add custom CSS:
```css
.my-custom-class {
    background: linear-gradient(135deg, var(--brand-primary), var(--brand-accent));
}
```

This gets added to `custom.css` and works on all pages.

### Extending Navigation

Edit `assets/js/site-config.js` to add dynamic navigation features:
```javascript
// Add dropdown menus
// Add active page highlighting  
// Add breadcrumbs
```

### Custom Fonts

Set custom font URL in typography settings:
```
https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700
```

System adds `@import` to `custom.css` automatically.

## Best Practices

1. **Test locally first** - Preview changes before committing
2. **Use CSS variables** - Reference `var(--brand-primary)` not `#1b5fa3`
3. **Keep custom CSS minimal** - Let the system manage most styles
4. **Commit regularly** - Small changes are easier to track
5. **Document customizations** - Note any manual changes you make

## Troubleshooting

### Colors not updating?
- Check browser cache (Ctrl+F5 / Cmd+Shift+R)
- Verify `custom.css` was updated
- Check console for CSS errors

### Navigation not showing?
- Check `site-config.js` exists in `assets/js/`
- Verify script is included in HTML: `<script src="assets/js/site-config.js"></script>`
- Check browser console for JS errors

### Styles look broken?
- Ensure `custom.css` is loaded: `<link rel="stylesheet" href="assets/css/custom.css">`
- Check file paths are relative to page location
- Verify CSS syntax is valid

## Summary

ForgeWeb uses **shared static files** for branding and navigation:
- ✅ Change once, updates everywhere
- ✅ GitHub Pages compatible  
- ✅ No build step required
- ✅ Fast and efficient
- ✅ Easy to maintain

This is the standard way static sites work - and it's perfect for GitHub Pages! 🚀
