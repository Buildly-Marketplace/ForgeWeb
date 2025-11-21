/**
 * ForgeWeb Branding Utility
 * Applies branding configuration universally across all admin pages
 */

class BrandingManager {
    constructor() {
        this.branding = null;
        this.defaultBranding = {
            primaryColor: '#1b5fa3',
            secondaryColor: '#144a84',
            accentColor: '#f9943b',
            darkColor: '#1F2937',
            lightColor: '#F3F4F6',
            font: 'Inter'
        };
    }

    /**
     * Load branding configuration from server
     */
    async loadBranding() {
        try {
            const response = await fetch('/api/branding');
            if (response.ok) {
                this.branding = await response.json();
                console.log('✓ Branding loaded:', this.branding);
                return this.branding;
            } else {
                console.warn('Could not load branding from API, using defaults');
                this.branding = { ...this.defaultBranding };
                return this.branding;
            }
        } catch (error) {
            console.warn('Error loading branding:', error);
            this.branding = { ...this.defaultBranding };
            return this.branding;
        }
    }

    /**
     * Apply branding to the current page
     */
    async applyBranding() {
        if (!this.branding) {
            await this.loadBranding();
        }

        // Apply CSS custom properties
        this.applyCSSVariables();

        // Apply font
        this.applyFont();

        // Override Tailwind/hardcoded colors
        this.applyColorOverrides();

        console.log('✓ Branding applied to page');
    }

    /**
     * Apply CSS custom properties for branding colors
     */
    applyCSSVariables() {
        const root = document.documentElement;
        root.style.setProperty('--color-primary', this.branding.primaryColor);
        root.style.setProperty('--color-secondary', this.branding.secondaryColor);
        root.style.setProperty('--color-accent', this.branding.accentColor);
        root.style.setProperty('--color-dark', this.branding.darkColor || this.defaultBranding.darkColor);
        root.style.setProperty('--color-light', this.branding.lightColor || this.defaultBranding.lightColor);
    }

    /**
     * Apply custom font
     */
    applyFont() {
        if (this.branding.font && this.branding.font !== 'Inter') {
            // Load font from Google Fonts
            const fontLink = document.createElement('link');
            fontLink.href = `https://fonts.googleapis.com/css2?family=${this.branding.font.replace(' ', '+')}:wght@300;400;500;600;700&display=swap`;
            fontLink.rel = 'stylesheet';
            document.head.appendChild(fontLink);

            // Apply to body
            document.body.style.fontFamily = `'${this.branding.font}', sans-serif`;
        }
    }

    /**
     * Apply color overrides via dynamic stylesheet
     */
    applyColorOverrides() {
        // Create or update dynamic style element
        let styleEl = document.getElementById('branding-overrides');
        if (!styleEl) {
            styleEl = document.createElement('style');
            styleEl.id = 'branding-overrides';
            document.head.appendChild(styleEl);
        }

        // Generate CSS rules to override hardcoded colors
        styleEl.textContent = `
            /* Branding color overrides */
            :root {
                --color-primary: ${this.branding.primaryColor};
                --color-secondary: ${this.branding.secondaryColor};
                --color-accent: ${this.branding.accentColor};
                --color-dark: ${this.branding.darkColor || this.defaultBranding.darkColor};
                --color-light: ${this.branding.lightColor || this.defaultBranding.lightColor};
            }
            
            /* Override buildly- classes */
            .bg-buildly-primary { background-color: var(--color-primary) !important; }
            .text-buildly-primary { color: var(--color-primary) !important; }
            .border-buildly-primary { border-color: var(--color-primary) !important; }
            .hover\\:bg-buildly-secondary:hover { background-color: var(--color-secondary) !important; }
            .hover\\:text-buildly-secondary:hover { color: var(--color-secondary) !important; }
            .bg-buildly-secondary { background-color: var(--color-secondary) !important; }
            .text-buildly-secondary { color: var(--color-secondary) !important; }
            .bg-buildly-accent { background-color: var(--color-accent) !important; }
            .text-buildly-accent { color: var(--color-accent) !important; }
            .bg-buildly-dark { background-color: var(--color-dark) !important; }
            .text-buildly-dark { color: var(--color-dark) !important; }
            
            /* Override common Tailwind color classes to use branding */
            .bg-purple-600, .bg-blue-600, .bg-indigo-600 { 
                background-color: var(--color-primary) !important; 
            }
            .bg-green-600 { 
                background-color: var(--color-secondary) !important; 
            }
            .bg-yellow-600, .bg-red-600, .bg-pink-600, .bg-orange-600 { 
                background-color: var(--color-accent) !important; 
            }
            .text-blue-600, .text-indigo-600, .text-purple-600 { 
                color: var(--color-primary) !important; 
            }
            .text-green-600 { 
                color: var(--color-secondary) !important; 
            }
            .text-yellow-600, .text-orange-600 { 
                color: var(--color-accent) !important; 
            }
            
            /* Gradients */
            .hero-gradient, .bg-gradient-to-r.from-buildly-primary {
                background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%) !important;
            }
            
            .text-gradient {
                background: linear-gradient(135deg, var(--color-primary), var(--color-accent)) !important;
                -webkit-background-clip: text !important;
                -webkit-text-fill-color: transparent !important;
                background-clip: text !important;
            }
        `;
    }

    /**
     * Get a specific branding value
     */
    getValue(key, defaultValue = null) {
        if (!this.branding) {
            console.warn('Branding not loaded yet');
            return defaultValue || this.defaultBranding[key];
        }
        return this.branding[key] || defaultValue || this.defaultBranding[key];
    }

    /**
     * Update Tailwind config (if present) with branding colors
     */
    updateTailwindConfig() {
        if (window.tailwind && window.tailwind.config) {
            window.tailwind.config = {
                theme: {
                    extend: {
                        colors: {
                            'buildly-primary': this.branding.primaryColor,
                            'buildly-secondary': this.branding.secondaryColor,
                            'buildly-accent': this.branding.accentColor,
                            'buildly-dark': this.branding.darkColor || this.defaultBranding.darkColor,
                            'buildly-light': this.branding.lightColor || this.defaultBranding.lightColor,
                            'primary': this.branding.primaryColor,
                            'secondary': this.branding.secondaryColor,
                            'accent': this.branding.accentColor
                        }
                    }
                }
            };
        }
    }
}

// Create global instance
window.brandingManager = new BrandingManager();

// Auto-apply branding when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.brandingManager.applyBranding();
    });
} else {
    // DOM already loaded
    window.brandingManager.applyBranding();
}
