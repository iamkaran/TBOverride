import subprocess
from pathlib import Path
import re
from typing import Dict

MAINLOGO_MARKER = "$MAINLOGO$"


class FileIO:
    def __init__(self, conf_path: str | Path, css_path: str | Path):
        self.conf = Path(conf_path)

        self.CSS_FILE = Path(css_path)

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

    def override_css_value(self, old_file: str, css_selectors: Dict[str, str]) -> str:
        """
        Replace values of CSS vars inside var_block only.
        css_selectors example: {"--tb-logo-w":"150px", "--tb-topbar-bg":"#ffd900"}
        """
        # Find index of the VARS bloc
        start = old_file.find(self.VARS_BEGIN)
        end = old_file.find(self.VARS_END)
        
        # VARS Block as string
        vars_block = old_file[start:end]
        new_vars_block = vars_block
        
        print(css_selectors)
        
        for selector, new_value in css_selectors.items():
            
            # Find the full line and value of the variable
            _value_regex = fr"{selector}:\s*[#]?([^px]+)(?:px)?;"
            _full_line_regex = fr"({selector}:\s*[#]?([^px]+)(?:px)?;)"
            
            match_value = re.search(_value_regex, vars_block)
            match_line = re.search(_full_line_regex, vars_block)
            
            old_full_line = match_line.group(1)
            old_value = match_value.group(1)
            
            # Append a unit if needed
            if "#" in old_full_line:
                old_value = f"#{old_value}"
                new_value = f"#{new_value}" if "#" not in new_value else new_value
                print(old_value, new_value)
            elif "px" in old_full_line:
                old_value = f"{old_value}px"
                new_value = f"{new_value}px" if "px" not in new_value else new_value
                print(old_value, new_value)
            # Apply the replacement value
            new_full_line = old_full_line.replace(old_value, new_value)
            
            new_vars_block = new_vars_block.replace(old_full_line, new_full_line)
        
        return new_vars_block
            

class TBOverride:
    def __init__(self, conf_path: str, css_path: str):
        self.fileio = FileIO(conf_path=conf_path, css_path=css_path)

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

        new_var_block = self.fileio.override_css_value(old_file=old_full_text, css_selectors=elements)
        # print(new_var_block)

        new_full_text = old_full_text[:b] + new_var_block + old_full_text[e:]
        css_path.write_text(new_full_text, encoding="utf-8")
        print("[+] Theme variables updated in CSS.")

def main(conf_path: str, css_path: str, overrides: dict) -> None:
    
    tbov = TBOverride(conf_path=conf_path, css_path=css_path)
    
    tbov.override_main_logo()
    tbov.override_theme(elements=overrides)

    # Check + reload nginx
    subprocess.check_call(["sudo", "nginx", "-t"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("[+] NGINX Tests Passed!")
    subprocess.check_call(["sudo", "systemctl", "reload", "nginx"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("[+] Reloaded NGINX.")

if __name__ == "__main__":
    conf_path = Path("/etc/nginx/sites-available/tb-proxy")
    css_path = Path("/opt/custom_assets/custom-theme.css")
    # conf_path = Path("tests/example_tb_proxy")
    # css_file = Path("tests/example_css.css")
    
    old_file = css_path.read_text(encoding="utf-8")
    
    selectors = {
        "--tb-logo-w": "156px",
        "--tb-logo-h": "50px",
        "--tb-topbar-bg": "#1F1F1F"
    }
    
    main(conf_path=conf_path, css_path=css_path, overrides=selectors)
