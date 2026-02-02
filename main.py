import subprocess
from pathlib import Path
import re
from typing import Dict

MAINLOGO_MARKER = "$MAINLOGO$"


class FileIO:
    def __init__(self, path: str | Path):
        self.conf = Path(path)

        self.CSS_FILE = Path("/opt/custom_assets/custom-theme.css")

        self.VARS_BEGIN = ">>> TB_CUSTOM_THEME_VARS_BEGIN"
        self.VARS_END = "<<< TB_CUSTOM_THEME_VARS_END"

    def read_file(self) -> str:
        """Return config file contents."""
        try:
            return self.conf.read_text(encoding="utf-8")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"[X] Config file not present: {self.conf}") from e

    def write_file(self, data: str) -> None:
        """Write config file contents."""
        try:
            self.conf.write_text(data, encoding="utf-8")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"[X] Config file not present: {self.conf}") from e

    def insert_block(self, marker: str, data: str) -> bool:
        """Insert a block into the config once, right after marker."""
        text = self.read_file()

        if marker not in text:
            raise ValueError(f"[X] Marker not found: {marker}")

        insertion = f"{marker}\n{data}"

        # Prevent duplicates
        if insertion in text:
            return False

        updated = text.replace(marker, insertion, 1)
        self.write_file(updated)
        return True

    def override_css_value(self, var_block: str, css_selectors: Dict[str, str]) -> str:
        """
        Replace values of CSS vars inside var_block only.
        css_selectors example: {"--tb-logo-w":"150px", "--tb-topbar-bg":"#ffd900"}
        """
        block = var_block

        for sel, new_val in css_selectors.items():
            new_val = str(new_val).strip()

            # Match lines like:   --tb-logo-w:   150px;
            m = re.search(
                rf"(?m)^(?P<prefix>\s*{re.escape(sel)}\s*:\s*)(?P<val>[^;]+?)(?P<suffix>\s*;)",
                block,
            )
            if not m:
                # Skip silently (or raise if you want strict mode)
                continue

            block = (
                block[: m.start()]
                + f"{m.group('prefix')}{new_val}{m.group('suffix')}"
                + block[m.end() :]
            )

        return block


class TBOverride:
    def __init__(self, path: str):
        self.fileio = FileIO(path)

        self.ROOT = Path("/etc/nginx/sites-available")
        self.CUSTOM_ASSETS = Path("/opt/custom_assets")
        self.FILE_MAIN_LOGO = Path("logo_title_white.svg")

        self.MARKER_MAIN_LOGO = "$MAIN_LOGO$"

    def override_main_logo(self) -> None:
        """Override the main logo in TB."""
        exist = (self.CUSTOM_ASSETS / self.FILE_MAIN_LOGO).is_file()
        if not exist:
            raise FileNotFoundError(f"[X] {self.FILE_MAIN_LOGO} not found in {self.CUSTOM_ASSETS}!")

        OVERRIDE = (
            f"    location = /assets/{self.FILE_MAIN_LOGO} {{\n"
            f"        alias {self.CUSTOM_ASSETS / self.FILE_MAIN_LOGO};\n"
            f'        add_header Cache-Control "no-store";\n'
            f"    }}\n"
        )

        print("[+] Overriding default main logo on ThingsBoard!")
        inserted = self.fileio.insert_block(marker=self.MARKER_MAIN_LOGO, data=OVERRIDE)
        if inserted:
            print("[+] Logo location block inserted.")
        else:
            print("[=] Logo location block already present (skipped).")

    def override_theme(self, elements: Dict[str, str]) -> None:
        """Replace vars inside the TB_CUSTOM_THEME_VARS block in the CSS file."""
        css_path = self.fileio.CSS_FILE
        old_full_text = css_path.read_text(encoding="utf-8")

        b = old_full_text.find(self.fileio.VARS_BEGIN)
        e = old_full_text.find(self.fileio.VARS_END)
        if b == -1 or e == -1 or e <= b:
            raise ValueError("[X] Vars block markers not found or out of order in CSS.")

        var_block = old_full_text[b:e]
        new_var_block = self.fileio.override_css_value(var_block, elements)

        new_full_text = old_full_text[:b] + new_var_block + old_full_text[e:]
        css_path.write_text(new_full_text, encoding="utf-8")

        print("[+] Theme variables updated in CSS.")

    def main(self) -> None:
        theme_vars = {
            "--tb-logo-w": "150px",
            "--tb-logo-h": "36px",
            "--tb-topbar-bg": "#282828",
            "--tb-sidebar-bg": "#424040",
            "--tb-main-bg": "#0a1320",
            "--tb-text": "#e5e7eb",
        }

        self.override_main_logo()
        self.override_theme(elements=theme_vars)

        # Check + reload nginx
        subprocess.check_call(["sudo", "nginx", "-t"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[+] NGINX Tests Passed!")
        subprocess.check_call(["sudo", "systemctl", "reload", "nginx"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[+] Reloaded NGINX.")


TBOverride(path="/etc/nginx/sites-available/tb-proxy").main()
