/**
 * Admin Navigation Component
 * Collapsible sidebar with hamburger menu for all admin pages
 */

class AdminNav {
    constructor(containerId = 'admin-nav') {
        this.containerId = containerId;
        this.isCollapsed = localStorage.getItem('admin-nav-collapsed') === 'true';
        this.init();
    }

    init() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.warn(`Admin nav container #${this.containerId} not found`);
            return;
        }

        container.innerHTML = this.getNavHTML();
        this.bindEvents();
        this.setActiveLink();
        
        // Apply collapsed state
        if (this.isCollapsed) {
            this.collapse();
        }
    }

    getNavHTML() {
        return `
            <!-- Hamburger Toggle -->
            <button id="nav-toggle" class="p-3 hover:bg-gray-100 transition-colors lg:hidden">
                <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
                </svg>
            </button>

            <!-- Sidebar Navigation -->
            <div id="nav-sidebar" class="bg-gradient-to-b from-buildly-primary to-buildly-secondary text-white flex flex-col transition-all duration-300">
                <!-- Header -->
                <div class="p-4 border-b border-white border-opacity-20">
                    <div class="flex items-center justify-between">
                        <div class="nav-content">
                            <div class="text-lg font-bold">🚀 ForgeWeb</div>
                            <div class="text-xs opacity-80">Admin Dashboard</div>
                        </div>
                        <button id="nav-close" class="lg:hidden p-1 hover:bg-white hover:bg-opacity-20 rounded">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                            </svg>
                        </button>
                    </div>
                </div>

                <!-- Navigation Links -->
                <nav class="flex-1 overflow-y-auto p-3">
                    <div class="nav-section">
                        <div class="nav-section-title">Main</div>
                        <a href="index.html" class="nav-item" data-page="index">
                            <span class="nav-icon">📊</span>
                            <span class="nav-label">Dashboard</span>
                        </a>
                    </div>

                    <div class="nav-section">
                        <div class="nav-section-title">Content</div>
                        <a href="editor.html" class="nav-item" data-page="editor">
                            <span class="nav-icon">✍️</span>
                            <span class="nav-label">Article Editor</span>
                        </a>
                        <a href="page-editor.html" class="nav-item" data-page="page-editor">
                            <span class="nav-icon">📄</span>
                            <span class="nav-label">Page Editor</span>
                        </a>
                        <a href="articles-manager.html" class="nav-item" data-page="articles-manager">
                            <span class="nav-icon">📚</span>
                            <span class="nav-label">Articles Manager</span>
                        </a>
                    </div>

                    <div class="nav-section">
                        <div class="nav-section-title">Design</div>
                        <a href="branding-manager.html" class="nav-item" data-page="branding-manager">
                            <span class="nav-icon">🎨</span>
                            <span class="nav-label">Branding</span>
                        </a>
                        <a href="navigation-manager.html" class="nav-item" data-page="navigation-manager">
                            <span class="nav-icon">🧭</span>
                            <span class="nav-label">Navigation</span>
                        </a>
                    </div>

                    <div class="nav-section">
                        <div class="nav-section-title">Tools</div>
                        <a href="social.html" class="nav-item" data-page="social">
                            <span class="nav-icon">📱</span>
                            <span class="nav-label">Social Media</span>
                        </a>
                        <a href="html-import.html" class="nav-item" data-page="html-import">
                            <span class="nav-icon">📥</span>
                            <span class="nav-label">Import HTML</span>
                        </a>
                    </div>

                    <div class="nav-section">
                        <div class="nav-section-title">Configuration</div>
                        <a href="site-setup.html" class="nav-item" data-page="site-setup">
                            <span class="nav-icon">⚙️</span>
                            <span class="nav-label">Site Setup</span>
                        </a>
                        <a href="settings.html" class="nav-item" data-page="settings">
                            <span class="nav-icon">🔧</span>
                            <span class="nav-label">Settings</span>
                        </a>
                    </div>

                    <div class="nav-section">
                        <a href="/" class="nav-item" target="_blank">
                            <span class="nav-icon">🌐</span>
                            <span class="nav-label">View Site</span>
                        </a>
                    </div>
                </nav>

                <!-- Footer -->
                <div class="p-3 border-t border-white border-opacity-20 text-xs opacity-70 nav-content">
                    <div>Press ESC to toggle menu</div>
                </div>
            </div>

            <!-- Overlay for mobile -->
            <div id="nav-overlay" class="fixed inset-0 bg-black bg-opacity-50 z-40 hidden lg:hidden"></div>

            <style>
                #nav-sidebar {
                    position: fixed;
                    left: 0;
                    top: 0;
                    bottom: 0;
                    width: 260px;
                    z-index: 50;
                    transform: translateX(0);
                }

                #nav-sidebar.collapsed {
                    transform: translateX(-100%);
                }

                @media (max-width: 1024px) {
                    #nav-sidebar.collapsed {
                        transform: translateX(-100%);
                    }
                }

                .nav-section {
                    margin-bottom: 1.5rem;
                }

                .nav-section-title {
                    font-size: 0.75rem;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    opacity: 0.7;
                    margin-bottom: 0.5rem;
                    padding: 0 0.5rem;
                }

                .nav-item {
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                    padding: 0.75rem;
                    margin-bottom: 0.25rem;
                    border-radius: 0.5rem;
                    color: rgba(255, 255, 255, 0.9);
                    text-decoration: none;
                    transition: all 0.2s;
                }

                .nav-item:hover {
                    background: rgba(255, 255, 255, 0.15);
                    color: white;
                }

                .nav-item.active {
                    background: rgba(255, 255, 255, 0.2);
                    color: white;
                    font-weight: 500;
                }

                .nav-icon {
                    font-size: 1.25rem;
                    flex-shrink: 0;
                }

                #nav-toggle {
                    position: fixed;
                    top: 1rem;
                    left: 1rem;
                    z-index: 30;
                    background: white;
                    border-radius: 0.5rem;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                }

                #nav-overlay.visible {
                    display: block;
                }
            </style>
        `;
    }

    bindEvents() {
        const toggle = document.getElementById('nav-toggle');
        const close = document.getElementById('nav-close');
        const overlay = document.getElementById('nav-overlay');
        const sidebar = document.getElementById('nav-sidebar');

        if (toggle) {
            toggle.addEventListener('click', () => this.toggle());
        }

        if (close) {
            close.addEventListener('click', () => this.collapse());
        }

        if (overlay) {
            overlay.addEventListener('click', () => this.collapse());
        }

        // ESC key to toggle
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !this.isCollapsed) {
                this.collapse();
            }
        });

        // Handle window resize
        window.addEventListener('resize', () => {
            if (window.innerWidth >= 1024) {
                // Desktop - always show sidebar
                this.expand();
            }
        });
    }

    setActiveLink() {
        const currentPage = document.body.dataset.page;
        if (!currentPage) return;

        const links = document.querySelectorAll('.nav-item[data-page]');
        links.forEach(link => {
            if (link.dataset.page === currentPage) {
                link.classList.add('active');
            }
        });
    }

    toggle() {
        if (this.isCollapsed) {
            this.expand();
        } else {
            this.collapse();
        }
    }

    expand() {
        const sidebar = document.getElementById('nav-sidebar');
        const overlay = document.getElementById('nav-overlay');
        
        if (sidebar) {
            sidebar.classList.remove('collapsed');
        }
        if (overlay && window.innerWidth < 1024) {
            overlay.classList.add('visible');
        }
        
        this.isCollapsed = false;
        localStorage.setItem('admin-nav-collapsed', 'false');
    }

    collapse() {
        const sidebar = document.getElementById('nav-sidebar');
        const overlay = document.getElementById('nav-overlay');
        
        if (sidebar) {
            sidebar.classList.add('collapsed');
        }
        if (overlay) {
            overlay.classList.remove('visible');
        }
        
        this.isCollapsed = true;
        localStorage.setItem('admin-nav-collapsed', 'true');
    }
}

// Auto-initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    new AdminNav();
});
