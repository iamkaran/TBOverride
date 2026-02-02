import subprocess
from pathlib import Path
import re
import os
import sys
from typing import Dict

class FileIO:
    def __init__(self, conf_path: str | Path, css_path: str | Path):
        self.CONF = Path(conf_path)

        self.CSS_FILE = Path(css_path)

        self.VARS_BEGIN = ">>> TB_CUSTOM_THEME_VARS_BEGIN"
        self.VARS_END = "<<< TB_CUSTOM_THEME_VARS_END"

    def read_file(self) -> str:
        """Return config file contents."""
        try:
            return self.CONF.read_text(encoding="utf-8")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"[X] Config file not present: {self.CONF}") from e

    def write_file(self, data: str) -> None:
        """Write config file contents."""
        try:
            self.CONF.write_text(data, encoding="utf-8")
        except OSError as e:
            raise OSError(f"[X] Failed to write config: {self.CONF}") from e

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

    def override_css_value(self, old_file: str, css_selectors: Dict[str, str]) -> str:
        """
        Replace values of CSS vars inside var_block only.
        css_selectors example: {"--tb-logo-w":"150px", "--tb-topbar-bg":"#ffd900"}
        """
        # Find index of the VARS bloc
        start = old_file.find(self.VARS_BEGIN)
        end = old_file.find(self.VARS_END)
        
        if start == -1 or end == -1 or end <= start:
            raise ValueError("[X] Vars block markers not found or out of order in CSS.")
        
        # VARS Block as string
        vars_block = old_file[start:end]
        
        if len(vars_block) == 0:
            raise ValueError("[X] VARS Block not present")
        
        new_vars_block = vars_block
        
        for selector, new_value in css_selectors.items():
            _value_regex = rf"(?m)^(?!\s*/\*)\s*(?P<line>{re.escape(selector)}\s*:\s*#?(?P<val>.+?)(?:px)?;)"
            m = re.search(_value_regex, new_vars_block)
            
            if m:
                old_full_line = m.group("line")
                old_value = m.group("val")
            else:
                raise ValueError(f"[X] Regex failed to find variable: {selector}")
            
            # Append a unit if needed
            if f"#{old_value}" in old_full_line:
                old_value = f"#{old_value}"
                new_value = f"#{new_value}" if "#" not in new_value else new_value
            elif f"{old_value}px" in old_full_line:
                old_value = f"{old_value}px"
                new_value = f"{new_value}px" if "px" not in new_value else new_value
            
            if old_value != new_value:
                print(f"Overriding: {old_value} -> {new_value}")
                
                # Apply the replacement value
                new_full_line = old_full_line.replace(old_value, new_value, 1)
                
                new_vars_block = new_vars_block.replace(old_full_line, new_full_line, 1)
            else:
                continue
        
        return new_vars_block
            

class TBOverride:
    def __init__(self, conf_path: str, css_path: str):
        self.fileio = FileIO(conf_path=conf_path, css_path=css_path)

        self.CUSTOM_ASSETS = Path("/opt/custom_assets")
        self.FILE_MAIN_LOGO = Path("logo_title_white.svg")

        self.MARKER_MAIN_LOGO = "$MAIN_LOGO$"
    
    def check_sudo(self):
        '''Check if the script is running as sudo'''
        
        if os.geteuid() == 0:
            return True
        else:
            return False
    
    def override_main_logo(self, path: str | Path) -> None:
        """Override the main logo in TB."""
        print("[+] Overriding Default TB Logo")
        if not path:
            exist = (self.CUSTOM_ASSETS / self.FILE_MAIN_LOGO).is_file()
        else:
            print(path)
            exist = Path(path).is_file()
        
        if not exist:
            raise FileNotFoundError(f"[X] {self.FILE_MAIN_LOGO} not found in {self.CUSTOM_ASSETS}!")
        
        print(f"- Found logo: {self.CUSTOM_ASSETS / self.FILE_MAIN_LOGO}")

        OVERRIDE = (
            f"    location = /assets/{self.FILE_MAIN_LOGO} {{\n"
            f"        alias {self.CUSTOM_ASSETS / self.FILE_MAIN_LOGO};\n"
            f'        add_header Cache-Control "no-store";\n'
            f"    }}\n"
        )

        inserted = self.fileio.insert_block(marker=self.MARKER_MAIN_LOGO, data=OVERRIDE)
        if inserted:
            print("- Logo location block inserted.")
        else:
            print("- Logo location block already present (skipped).")

    def override_theme(self, elements: Dict[str, str]) -> None:
        """Replace vars inside the TB_CUSTOM_THEME_VARS block in the CSS file."""
        print(f"[+] Overriding Default TB Theme...")
        
        css_path = self.fileio.CSS_FILE
        old_full_text = css_path.read_text(encoding="utf-8")
        
        if len(old_full_text) == 0:
            raise ValueError("[X] CSS File Empty")
        
        print(f"- Found CSS File: {css_path}")
        
        b = old_full_text.find(self.fileio.VARS_BEGIN)
        e = old_full_text.find(self.fileio.VARS_END)
        
        if b == -1 or e == -1 or e <= b:
            raise ValueError("[X] Vars block markers not found or out of order in CSS.")

        new_var_block = self.fileio.override_css_value(old_file=old_full_text, css_selectors=elements)

        new_full_text = old_full_text[:b] + new_var_block + old_full_text[e:]
        
        css_path.write_text(new_full_text, encoding="utf-8")
        print("[+] Theme variables updated in CSS.")

def update_tb(conf_path: str, css_path: str, overrides: dict) -> None:
    '''Run the program'''
    
    tbov = TBOverride(conf_path=conf_path, css_path=css_path)
    
    # Check sudo
    
    if not tbov.check_sudo():
        print(f"Run script as sudo!")
        sys.exit(1)
    
    # Overrides
    
    # print("\n")
    # tbov.override_main_logo()
    print("\n")
    tbov.override_theme(elements=overrides)
    print("\n")
    
    # Check + reload nginx
    
    subprocess.run(["nginx", "-t"], capture_output=True, text=True, check=True)
    print("[+] NGINX Tests Passed!")
    subprocess.run(["systemctl", "reload", "nginx"], capture_output=True, text=True, check=True)
    print("[+] Reloaded NGINX.")

if __name__ == "__main__":
    conf_path = Path("/etc/nginx/sites-available/tb-proxy")
    css_path = Path("/opt/custom_assets/custom-theme.css")
    
    selectors = {
        "--tb-logo-w": "156px",
        "--tb-logo-h": "50px",
        "--tb-topbar-bg": "#181818"
    }
    
    update_tb(conf_path=conf_path, css_path=css_path, overrides=selectors)
