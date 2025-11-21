# ForgeWeb Branding System

## Overview

ForgeWeb now has a universal branding system that applies your brand colors, fonts, and styling consistently across:
- All admin interface pages
- All generated website pages
- Templates and content

## Configuration Files

### 1. `site-config.json`
Main site configuration including branding section:

```json
{
  "branding": {
    "primaryColor": "#1b5fa3",
    "secondaryColor": "#144a84",
    "accentColor": "#f9943b",
    "darkColor": "#1F2937",
    "lightColor": "#F3F4F6",
    "font": "Inter"
  }
}
```

### 2. `branding-config.json`
Dedicated branding configuration (takes precedence):

```json
{
  "colors": {
    "primary": "#1b5fa3",
    "secondary": "#f9943b"
  },
  "typography": {
    "headingFont": "Inter",
    "bodyFont": "Inter"
  }
}
```

## How Branding is Applied

### Backend (file-api.py)

The server automatically applies branding when generating pages:

1. **`load_branding_config()`** - Loads branding from both config files
2. **`generate_page()`** - Replaces template variables with branding values
3. **`generate_basic_page()`** - Uses branding for all generated pages

Template variables replaced:
- `{{BRAND_PRIMARY_COLOR}}`
- `{{BRAND_SECONDARY_COLOR}}`
- `{{BRAND_ACCENT_COLOR}}`
- `{{BRAND_FONT}}`

### Frontend (branding.js)

The JavaScript utility (`js/branding.js`) applies branding to admin pages:

**Usage:**
```html
<script src="js/branding.js"></script>
```

**Features:**
- Auto-loads branding from `/api/branding`
- Applies CSS custom properties (`--color-primary`, etc.)
- Loads custom fonts from Google Fonts
- Overrides hardcoded Tailwind classes
- Global instance: `window.brandingManager`

**Manual usage:**
```javascript
// Get branding value
const primaryColor = brandingManager.getValue('primaryColor');

// Reload and reapply
await brandingManager.loadBranding();
await brandingManager.applyBranding();
```

## Adding Branding to New Pages

### Admin Pages

Simply include the branding script:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>My Admin Page</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <!-- Your content -->
    
    <script src="js/branding.js"></script>
</body>
</html>
```

The branding will be applied automatically!

### Generated Website Pages

Use the template system in `templates/base.html`:

```html
<script>
    tailwind.config = {
        theme: {
            extend: {
                colors: {
                    'primary': '{{BRAND_PRIMARY_COLOR}}',
                    'secondary': '{{BRAND_SECONDARY_COLOR}}',
                    'accent': '{{BRAND_ACCENT_COLOR}}'
                }
            }
        }
    }
</script>
```

The placeholders will be replaced automatically when pages are generated.

## Branding Color Classes

The system provides these standardized CSS classes:

### Tailwind-style Classes
- `.bg-buildly-primary` - Primary background color
- `.text-buildly-primary` - Primary text color
- `.bg-buildly-secondary` - Secondary background color
- `.text-buildly-secondary` - Secondary text color
- `.bg-buildly-accent` - Accent background color
- `.text-buildly-accent` - Accent text color

### CSS Custom Properties
```css
:root {
    --color-primary: #1b5fa3;
    --color-secondary: #144a84;
    --color-accent: #f9943b;
    --color-dark: #1F2937;
    --color-light: #F3F4F6;
}
```

## API Endpoints

### GET `/api/branding`
Returns the current branding configuration:

```json
{
  "primaryColor": "#1b5fa3",
  "secondaryColor": "#144a84",
  "accentColor": "#f9943b",
  "darkColor": "#1F2937",
  "lightColor": "#F3F4F6",
  "font": "Inter"
}
```

## Updating Branding

### Method 1: Edit Configuration Files
1. Edit `site-config.json` or `branding-config.json`
2. Refresh admin pages (branding auto-reloads)
3. Regenerate website pages to apply changes

### Method 2: Via Branding Manager (Future)
The branding manager interface (`branding-manager.html`) allows visual editing.

### Method 3: Programmatically
```javascript
// Update branding via API
await fetch('/api/branding', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        primaryColor: '#FF6600',
        secondaryColor: '#003366',
        accentColor: '#FFCC00',
        font: 'Roboto'
    })
});
```

## Color Overrides

The branding system overrides these common Tailwind classes to use your branding:

| Original Class | Maps To |
|---------------|---------|
| `.bg-purple-600`, `.bg-blue-600`, `.bg-indigo-600` | Primary Color |
| `.bg-green-600` | Secondary Color |
| `.bg-yellow-600`, `.bg-red-600`, `.bg-pink-600` | Accent Color |
| `.text-blue-600`, `.text-indigo-600` | Primary Color (text) |

## Best Practices

1. **Use branding classes** instead of hardcoded colors
2. **Test on both admin and website** after changing branding
3. **Keep branding-config.json in sync** with site-config.json
4. **Use semantic color names** (primary/secondary/accent) not specific colors
5. **Choose accessible color combinations** (check contrast ratios)

## Troubleshooting

### Branding not applying?
1. Check browser console for errors
2. Verify `js/branding.js` is loaded
3. Check `/api/branding` returns valid JSON
4. Clear browser cache

### Colors wrong on generated pages?
1. Regenerate pages using site generator
2. Check template placeholders are correct
3. Verify `site-config.json` has branding section

### Font not loading?
1. Check font name is correct (exact match to Google Fonts)
2. Verify internet connection (fonts load from CDN)
3. Check browser console for font loading errors

## Future Enhancements

- [ ] Visual branding editor with color picker
- [ ] Brand asset management (logos, favicons)
- [ ] Multiple brand themes
- [ ] Export/import branding presets
- [ ] Real-time preview of branding changes
- [ ] Accessibility checker for color combinations
