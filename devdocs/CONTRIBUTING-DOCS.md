# Documentation Contribution Guide

Guidelines for maintaining and contributing to ForgeWeb documentation.

## 📁 Documentation Structure

```
forgeweb/
├── README.md              # Main project README (keep in root)
├── LICENSE.md             # License (keep in root)
├── CHANGELOG.md           # Version history (keep in root)
├── devdocs/              # ALL technical documentation goes here
│   ├── README.md         # Documentation index
│   ├── QUICK-REFERENCE.md
│   ├── INSTALL.md
│   ├── ARCHITECTURE.md
│   ├── BRANDING.md
│   ├── STATIC-ASSETS.md
│   ├── DEPLOYMENT.md
│   └── ...
├── assets/README.md       # Assets-specific documentation
└── templates/README.md    # Templates-specific documentation
```

## ✅ Where to Put Documentation

### In `devdocs/`
✅ Installation guides  
✅ Architecture documentation  
✅ Feature documentation  
✅ API documentation  
✅ Deployment guides  
✅ Development guides  
✅ Configuration guides  

### In Root
✅ `README.md` - Main project overview  
✅ `LICENSE.md` - License file  
✅ `CHANGELOG.md` - Version history  
❌ No other `.md` files

### In Subdirectories
✅ `assets/README.md` - Assets-specific info  
✅ `templates/README.md` - Templates-specific info  
✅ Domain-specific documentation only  
❌ No general technical docs

## 📝 Writing Guidelines

### File Naming
- Use **kebab-case**: `static-assets.md`, not `Static_Assets.md`
- Be descriptive: `branding-system.md`, not `branding.md`
- Use `.md` extension for all documentation

### File Structure
```markdown
# Title (H1 - only one per file)

> **Note/Warning if needed**

Brief introduction (1-2 sentences)

## Section 1 (H2)

Content...

### Subsection (H3)

Content...

## See Also

- [Related Doc](other-doc.md)
```

### Content Style
- **Clear and concise** - Get to the point quickly
- **Examples** - Show, don't just tell
- **Code blocks** - Use proper syntax highlighting
- **Screenshots** - When helpful (store in `assets/images/docs/`)
- **Links** - Cross-reference related documentation
- **Updated dates** - Add "Last Updated: YYYY-MM-DD" at bottom

### Markdown Best Practices
```markdown
# Use ATX-style headers (not Setext)
## Not underlined headers

# Code blocks with language
```python
def example():
    pass
```

# Not just triple backticks
```

# Bullet lists
- Item one
- Item two
  - Sub-item (2 spaces)

# Not
* Mixed
- Styles

# Links
[Descriptive Text](path/to/file.md)

# Not
[Click here](file.md)

# Emphasis
**bold** for important
*italic* for emphasis
`code` for inline code

# Tables when needed
| Column 1 | Column 2 |
|----------|----------|
| Data     | Data     |
```

## 🔄 Updating Documentation

### When to Update
- ✅ Feature added/changed
- ✅ Configuration changed
- ✅ Commands changed
- ✅ File structure changed
- ✅ Workflow changed
- ✅ Bug fix affects docs

### Update Process
1. **Make code changes**
2. **Update relevant docs** in `devdocs/`
3. **Update CHANGELOG.md** with version bump
4. **Check cross-references** - fix broken links
5. **Test instructions** - verify they work
6. **Update "Last Updated" date**
7. **Commit together** with code changes

### Commit Messages
```bash
# Good
git commit -m "feat: Add branding system
- Implemented CSS variable system
- Updated devdocs/BRANDING.md with new features
- Added devdocs/STATIC-ASSETS.md"

# Bad  
git commit -m "Updated docs"
```

## 📋 Checklist for New Documentation

- [ ] File in correct location (`devdocs/` for technical docs)
- [ ] Descriptive filename (kebab-case)
- [ ] Clear title (H1)
- [ ] Introduction paragraph
- [ ] Proper heading hierarchy (H2, H3, H4)
- [ ] Code examples with syntax highlighting
- [ ] Cross-references to related docs
- [ ] Added to `devdocs/README.md` index
- [ ] "Last Updated" date at bottom
- [ ] Tested all commands/examples
- [ ] Spell-checked
- [ ] Previewed in Markdown viewer

## 🔍 Review Checklist

Before submitting documentation changes:

- [ ] **Accuracy** - All information is correct
- [ ] **Completeness** - Covers the topic thoroughly
- [ ] **Clarity** - Easy to understand
- [ ] **Examples** - Working code examples included
- [ ] **Links** - All links work
- [ ] **Formatting** - Proper Markdown syntax
- [ ] **Organization** - Logical flow
- [ ] **Index** - Added to devdocs/README.md
- [ ] **Date** - Updated "Last Updated" field

## 🚫 Common Mistakes to Avoid

❌ **Don't** put technical docs in root directory  
✅ **Do** put them in `devdocs/`

❌ **Don't** duplicate information  
✅ **Do** link to existing docs

❌ **Don't** use vague headings ("Setup", "Usage")  
✅ **Do** be specific ("Install Python Dependencies", "Deploy to GitHub Pages")

❌ **Don't** write walls of text  
✅ **Do** use headings, lists, and code blocks

❌ **Don't** forget to update cross-references  
✅ **Do** check for broken links

❌ **Don't** include outdated screenshots  
✅ **Do** update or remove outdated images

## 📸 Images and Screenshots

### Storage
```
assets/images/docs/
├── installation/
│   ├── step1-download.png
│   └── step2-setup.png
├── admin/
│   ├── dashboard.png
│   └── editor.png
└── deployment/
    └── github-pages.png
```

### Usage
```markdown
![Alt text](../assets/images/docs/category/image.png)
```

### Guidelines
- Use PNG for screenshots
- Use SVG for diagrams
- Keep file size < 500KB
- Use descriptive filenames
- Include alt text
- Update when UI changes

## 🔧 Tools

### Recommended
- **VS Code** with Markdown extensions
- **markdownlint** for linting
- **Markdown Preview Enhanced** for previewing
- **Grammarly** for spell/grammar check

### Validation
```bash
# Lint markdown files
npx markdownlint '**/*.md'

# Check for broken links
npx markdown-link-check devdocs/**/*.md
```

## 📊 Documentation Metrics

### Quality Indicators
- All code examples work
- No broken links
- Clear table of contents
- Logical organization
- Up-to-date with code
- Easy to find information

### Review Process
1. Self-review against checklist
2. Test all commands/examples
3. Check cross-references
4. Submit PR
5. Address review comments
6. Update as needed

## 🎯 Goals

Good documentation should:
- ✅ Help users succeed quickly
- ✅ Answer common questions
- ✅ Provide working examples
- ✅ Stay synchronized with code
- ✅ Be easy to maintain
- ✅ Be easy to find

## 📞 Questions?

- Open an issue for clarification
- Tag with `documentation` label
- Suggest improvements welcome!

---

**Last Updated:** November 21, 2025
