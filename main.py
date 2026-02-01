import subprocess
from pathlib import Path
import os

MAINLOGO_MARKER = "$MAINLOGO$"

class FileIO:
    def __init__(self, path: str | Path):
        self.conf = Path(path)
    
    def read_file(self) -> str:
        '''Return a file's contents'''
        
        try:
            return self.conf.read_text(encoding="utf-8")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"[X] Config file not present: {self.conf}") from e
        
    def write_file(self, data: str) -> str:
        '''Return a file's contents'''
        
        try:
            self.conf.write_text(data, encoding="utf-8")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"[X] Config file not present: {self.conf}") from e
    
    def insert_block(self, marker: str, data: str) -> bool:
        '''Insert a block into the config'''
        
        text = self.read_file()
        
        if marker not in text:
            raise ValueError(f"[X] Marker not found: {marker}")
        
        insertion = f"{marker}\n{data}"
        
        # Prevent duplicates
        if insertion in text:
            return False
        
        updated = text.replace(marker, insertion, 1)
        
        self.write_file(updated)
    
    
class TBOverride:
    def __init__(self, path: str):
        
        self.fileio = FileIO(path)
        
        self.ROOT = Path("/etc/nginx/sites-available")
        self.CUSTOM_ASSETS = Path("/opt/custom_assets")
        self.FILE_MAIN_LOGO = Path("logo_title_white.svg")
        
        self.MARKER_MAIN_LOGO = "$MAIN_LOGO$"
    
    def override_main_logo(self):
        '''Override the main logo in TB'''
        
        exist = (self.CUSTOM_ASSETS / self.FILE_MAIN_LOGO).is_file()
        
        if exist is False:
            raise FileNotFoundError(f"[X] {self.FILE_MAIN_LOGO} not found in {self.CUSTOM_ASSETS}!")
        
        OVERRIDE = (
            f"    location = /assets/{self.FILE_MAIN_LOGO} {{\n"
            f"        alias {self.CUSTOM_ASSETS / self.FILE_MAIN_LOGO};\n"
            f'        add_header Cache-Control "no-store";\n'
            f"    }}\n"
        )

        print(f"[+] Overriding defualt main logo on thingsboard!")
        
        self.fileio.insert_block(marker=self.MARKER_MAIN_LOGO, data=OVERRIDE)
    
    def main(self):
        
        self.override_main_logo()
        
        # Check configuration
        result = subprocess.check_call(["sudo", "nginx", "-t"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result == 0:
            print(f"[+] NGINX Tests Passed!")
            print(f"[+] Reloading NGINX")
            reload = subprocess.check_call(["sudo", "systemctl", "reload", "nginx"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            print(f"[X] NGINX Tests Failed!")
        
        
TBOverride(path="/etc/nginx/sites-available/tb-proxy").main()