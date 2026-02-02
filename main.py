from pathlib import Path
from tb_override import update_tb, TBOverride
from selection import Selection

banner = r"""
████████╗██████╗        ██████╗ ██╗   ██╗███████╗██████╗ ██████╗ ██╗██████╗ ███████╗
╚══██╔══╝██╔══██╗      ██╔═══██╗██║   ██║██╔════╝██╔══██╗██╔══██╗██║██╔══██╗██╔════╝
   ██║   ██████╔╝█████╗██║   ██║██║   ██║█████╗  ██████╔╝██████╔╝██║██║  ██║█████╗  
   ██║   ██╔══██╗╚════╝██║   ██║╚██╗ ██╔╝██╔══╝  ██╔══██╗██╔══██╗██║██║  ██║██╔══╝  
   ██║   ██████╔╝      ╚██████╔╝ ╚████╔╝ ███████╗██║  ██║██║  ██║██║██████╔╝███████╗
   ╚═╝   ╚═════╝        ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═════╝ ╚══════╝
                                                                                    
"""

class Menu:
    def __init__(self, conf_path: str, css_path: str):
        self.s = Selection()
        self.t = TBOverride(conf_path, css_path)
    
    def prompt(self):
        '''Main prompt'''
        pending_changes = {}
        
        while True:
            menu = self.s.select_menu()
            
            if menu == "Exit":
                break
            
            elif menu == "Edit Theme Variables":
                category = self.s.select_category()
                
                if category == "back":
                    continue
                
                var = self.s.select_var(category)
                
                while True:
                    action = self.s.select_action()
                    
                    if action == "Back":
                        break
                    
                    elif action == "Set new value":
                        value = self.s.enter_input(var)
                        # print(list(var.keys())[0], value)
                        pending_changes[list(var.keys())[0]] = value
                    
                    elif action == "Reset to default":
                        value = list(var.values())[0]
                        pending_changes[list(var.keys())[0]] = value
                
            elif menu == "Logo Change":
                path = self.s.logo_path()
                pending_changes["logo_path"] = path
        return pending_changes
    
def main():
    '''Run the program'''
    print(banner)
    conf_path = Path("/etc/nginx/sites-available/tb-proxy")
    css_path = Path("/opt/custom_assets/custom-theme.css")
    menu = Menu(conf_path, css_path)
    overrides = menu.prompt()
    if "logo_path" not in list(overrides.keys()):
        update_tb(conf_path, css_path, overrides)
    else:
        print(overrides)
        menu.t.override_main_logo(overrides["logo_path"])
        
if __name__ == "__main__":
    main()