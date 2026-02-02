from pathlib import Path
from variables import *
import rich
import questionary

class Selection:
    def __init__(self):
        self.categories = fetch_categories()
        self.categories.append("back")
        
    def select_menu(self) -> str:
        '''Present a list of options'''
        
        options = [
            "Edit Theme Variables",
            "Logo Change",
            "Review Changes",
            "Apply Changes",
            "Exit"
        ]
        
        choice = questionary.select(
            "What do you want to do?",
            choices=[
                questionary.Choice(title=c.capitalize(), value=c)
                for c in options
                ],
        ).ask()
        
        return choice
    
    def select_category(self) -> str:
        '''Select a category of theme variables'''
        options = self.categories
        
        
        choice = questionary.select(
            "Select a category",
            choices=[
                questionary.Choice(title=c.capitalize(), value=c)
                for c in options
                ],
        ).ask()
        
        return choice
    
    def select_var(self, category: str):
        options = fetch_items(category)  # dict: selector -> meta (must include "description")

        NAME_W = 22     # tweak
        DESC_W = 60     # tweak (keep < terminal width)

        def fmt(selector: str, meta: dict) -> str:
            '''Create a padded string'''
            desc = meta.get("description", "")
            
            if len(desc) > DESC_W:
                desc = desc[:DESC_W-1] + "..."
            
            return f"{selector:<{NAME_W-1}}"+desc
        
        choices = [
            questionary.Choice(
                title=fmt(selector, meta),
                value=selector,   # return the original selector
            )
            for selector, meta in options.items()
        ]

        var_name =  questionary.select(
            "Select a variable",
            choices=choices,
        ).ask()
        
        return fetch_var(category, var_name)
    
    def select_action(self) -> str:
        '''Select a variable to change'''
        options = [
            "Set new value",
            "Reset to default",
            "Back"
        ]
        
        choice = questionary.select(
            "Select a category",
            choices=[
                questionary.Choice(title=c.capitalize(), value=c)
                for c in options
                ],
        ).ask()
        
        return choice
    
    def logo_path(self):
        '''Ask for path to logo'''
        path = Path(
            questionary.path(
                "Enter path to logo"
            ).ask()
        )
        
        return path
    
    def enter_input(self, var: dict) -> str:
        '''Enter a value for the variable'''
        value_type = list(var.values())[0]["type"]
        
        if value_type == "px":
            value = questionary.text("Enter a value").ask()
            
        elif value_type == "hex":
            print("Visit https://www.google.com/search?q=google+color+picker\nPick a color and paste it here!")
            value = questionary.text("Enter the hexcode").ask()
            return None if not value.startswith("#") or len(value.replace("#", "")) != 6 else value
        else:
            value = questionary.text(f"Enter a value")
        
        return value

if __name__ == "__main__":
    s = Selection()
    # menu = s.select_menu()
    # s.select_action()
    s.prompt()
    
    