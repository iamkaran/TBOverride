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
    def __init__(self):
        self.root = Path("/etc/nginx/sites-available")
        self.custom_assets = Path("/opt/custom_assets")
        self.main_logo = Path("logo_title_white.svg")
    
    def override_main_logo(self):
        '''Override the main logo in TB'''
        
        exist = (self.root / self.main_logo).is_file()
        
        if exist is False:
            raise FileNotFoundError(f"[X] {self.main_logo} not found in {self.root}!")
        
        OVERRIDE = f"""\
            location = /assets/{self.main_logo} {{
                alias {self.custom_assets / self.main_logo};
                add_header Cache-Control "no-store";
            }}
        """
        
        print(OVERRIDE)

TBOverride().override_main_logo()

# CONF = r"tb-ce-wl\tb-proxyfasfas"

# MARKER = "$MAIN_LOGO$"
# LOCATION_BLOCK = """\
#     location = /assets/logo_title_white.svg {
#         alias /opt/custom/logo_title_white.svg;
#         add_header Cache-Control "no-store";
#     }

# """

# TBOverride(path=CONF).append_block(marker=MARKER, data=LOCATION_BLOCK)
# # TBOverride(path=CONF).append_block(marker=MARKER, data=LOCATION_BLOCK)