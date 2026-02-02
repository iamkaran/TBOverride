
def fetch_categories() -> list:
    '''Return a list of categories'''
    return list(TB_THEME_VARS_BY_CATEGORY.keys())

def fetch_items(category: str) -> dict:
    '''Return vars belonging to a category'''
    
    return TB_THEME_VARS_BY_CATEGORY[category]

def fetch_var(category: str, var_name: str) -> dict:
    '''Return the variable dict'''
    return {var_name:TB_THEME_VARS_BY_CATEGORY[category][var_name]}

TB_THEME_VARS_BY_CATEGORY: dict[str, dict[str, dict[str, str]]] = {
    "surfaces": {
        "--tb-topbar-bg": {
            "default": "#181818",
            "type": "hex",
            "description": "Top toolbar / header background.",
        },
        "--tb-sidebar-bg": {
            "default": "#121212",
            "type": "hex",
            "description": "Sidebar background color.",
        },
        "--tb-main-bg": {
            "default": "#0f1115",
            "type": "hex",
            "description": "Main content background (page body).",
        },
    },

    "logo": {
        "--tb-logo-w": {
            "default": "156px",
            "type": "px",
            "description": "Sidebar logo width.",
        },
        "--tb-logo-h": {
            "default": "50px",
            "type": "px",
            "description": "Sidebar logo height.",
        },
        "--tb-logo-pad-x": {
            "default": "12px",
            "type": "px",
            "description": "Horizontal padding around sidebar logo container.",
        },
        "--tb-logo-pad-y": {
            "default": "10px",
            "type": "px",
            "description": "Vertical padding around sidebar logo container.",
        },
        "--tb-logo-align": {
            "default": "flex-start",
            "type": "enum",
            "description": "Logo container alignment: flex-start | center | flex-end.",
        },
    },

    "text": {
        "--tb-text": {
            "default": "#e5e7eb",
            "type": "hex",
            "description": "Primary text color across UI.",
        },
        "--tb-text-muted": {
            "default": "#9ca3af",
            "type": "hex",
            "description": "Muted/secondary text (subtitles, hints).",
        },
        "--tb-text-invert": {
            "default": "#0b0f16",
            "type": "hex",
            "description": "Text color used on bright brand-colored surfaces (buttons).",
        },
    },

    "brand": {
        "--tb-brand": {
            "default": "#ff7a00",
            "type": "hex",
            "description": "Primary brand color used for buttons, links, accents.",
        },
        "--tb-brand-2": {
            "default": "#ffd900",
            "type": "hex",
            "description": "Secondary accent color (optional highlight color).",
        },
        "--tb-accent": {
            "default": "#22c55e",
            "type": "hex",
            "description": "Accent color for success-ish highlights.",
        },
        "--tb-link": {
            "default": "var(--tb-brand)",
            "type": "css",
            "description": "Link color. Can be hex or another CSS var reference.",
        },
    },

    "buttons": {
        "--tb-btn-bg": {
            "default": "var(--tb-brand)",
            "type": "css",
            "description": "Primary button background.",
        },
        "--tb-btn-text": {
            "default": "var(--tb-text-invert)",
            "type": "css",
            "description": "Primary button text color.",
        },
        "--tb-btn-radius": {
            "default": "10px",
            "type": "px",
            "description": "Button corner radius.",
        },
        "--tb-btn-padding-y": {
            "default": "8px",
            "type": "px",
            "description": "Button vertical padding (best-effort).",
        },
        "--tb-btn-padding-x": {
            "default": "14px",
            "type": "px",
            "description": "Button horizontal padding (best-effort).",
        },
    },

    "inputs": {
        "--tb-input-bg": {
            "default": "#0e1117",
            "type": "hex",
            "description": "Input background color.",
        },
        "--tb-input-text": {
            "default": "var(--tb-text)",
            "type": "css",
            "description": "Input text color.",
        },
        "--tb-input-border": {
            "default": "var(--tb-border)",
            "type": "css",
            "description": "Input border color.",
        },
        "--tb-input-radius": {
            "default": "10px",
            "type": "px",
            "description": "Input corner radius.",
        },
        "--tb-input-focus": {
            "default": "var(--tb-brand)",
            "type": "css",
            "description": "Focus outline/accent for inputs (best-effort).",
        },
    },

    "cards": {
        "--tb-card-bg": {
            "default": "#151821",
            "type": "hex",
            "description": "Card/widget background color.",
        },
        "--tb-card-bg-hover": {
            "default": "#1a1f2b",
            "type": "hex",
            "description": "Card/widget hover background color.",
        },
        "--tb-card-radius": {
            "default": "12px",
            "type": "px",
            "description": "Card corner radius.",
        },
        "--tb-card-padding": {
            "default": "12px",
            "type": "px",
            "description": "Default padding for card-like components (best-effort).",
        },
    },

    "interactions": {
        "--tb-hover-bg": {
            "default": "rgba(255,122,0,.12)",
            "type": "css",
            "description": "Hover background for sidebar rows, table rows, etc.",
        },
        "--tb-selected-bg": {
            "default": "rgba(255,122,0,.18)",
            "type": "css",
            "description": "Selected/active background for sidebar items (best-effort).",
        },
    },

    "borders": {
        "--tb-border": {
            "default": "#262b36",
            "type": "hex",
            "description": "Default border color for cards/inputs.",
        },
        "--tb-border-strong": {
            "default": "#343b4a",
            "type": "hex",
            "description": "Stronger border color for emphasis/separation.",
        },
        "--tb-divider": {
            "default": "rgba(229,231,235,.08)",
            "type": "css",
            "description": "Divider lines (toolbar bottom, sidebar right, table row separators).",
        },
    },

    "status": {
        "--tb-success": {
            "default": "#22c55e",
            "type": "hex",
            "description": "Success color (chips, highlights, etc.).",
        },
        "--tb-warning": {
            "default": "#f59e0b",
            "type": "hex",
            "description": "Warning color.",
        },
        "--tb-danger": {
            "default": "#ef4444",
            "type": "hex",
            "description": "Danger/error color.",
        },
        "--tb-info": {
            "default": "#3b82f6",
            "type": "hex",
            "description": "Info color.",
        },
    },

    "shadows": {
        "--tb-shadow": {
            "default": "0 8px 24px rgba(0,0,0,.35)",
            "type": "css",
            "description": "Stronger shadow preset for raised surfaces.",
        },
        "--tb-shadow-soft": {
            "default": "0 6px 18px rgba(0,0,0,.22)",
            "type": "css",
            "description": "Softer shadow preset for cards.",
        },
    },
}
