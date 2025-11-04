import customtkinter as ctk
from typing import Callable, Optional, List, Dict, Any


class SectionHeader(ctk.CTkFrame):
    def __init__(self, parent, text: str, icon: str = "", **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(fg_color="transparent")
        
        label_text = f"{icon} {text}" if icon else text
        ctk.CTkLabel(
            self, 
            text=label_text, 
            font=("Arial", 16, "bold")
        ).pack(anchor="w", pady=(5, 10))


class SectionSeparator(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, height=2, fg_color="gray25", **kwargs)


class LabeledEntry(ctk.CTkFrame):
    def __init__(self, parent, label_text: str, entry_width: int = 250, 
                 placeholder: str = "", **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(fg_color="transparent")
        
        ctk.CTkLabel(
            self, 
            text=label_text, 
            font=("Arial", 12)
        ).pack(anchor="w", pady=(5, 2))
        
        self.entry = ctk.CTkEntry(
            self, 
            width=entry_width,
            placeholder_text=placeholder
        )
        self.entry.pack(anchor="w", pady=(0, 5))
    
    def get(self) -> str:
        return self.entry.get()
    
    def set(self, value: str):
        self.entry.delete(0, "end")
        self.entry.insert(0, value)
    
    def configure_entry(self, **kwargs):
        self.entry.configure(**kwargs)


class LabeledCheckbox(ctk.CTkFrame):
    def __init__(self, parent, label_text: str, variable: Optional[ctk.BooleanVar] = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(fg_color="transparent")
        
        if variable is None:
            variable = ctk.BooleanVar(value=False)
        
        self.variable = variable
        self.checkbox = ctk.CTkCheckBox(
            self, 
            text=label_text, 
            variable=self.variable
        )
        self.checkbox.pack(anchor="w", pady=3)
    
    def get(self) -> bool:
        return self.variable.get()
    
    def set(self, value: bool):
        self.variable.set(value)


class LabeledComboBox(ctk.CTkFrame):
    def __init__(self, parent, label_text: str, values: List[str], 
                 default_value: str = "", width: int = 200, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(fg_color="transparent")
        
        ctk.CTkLabel(
            self, 
            text=label_text, 
            font=("Arial", 12)
        ).pack(anchor="w", pady=(10, 2))
        
        self.variable = ctk.StringVar(value=default_value)
        self.combobox = ctk.CTkComboBox(
            self, 
            values=values, 
            variable=self.variable, 
            width=width
        )
        self.combobox.pack(anchor="w", pady=(0, 5))
        
        if default_value:
            self.combobox.set(default_value)
    
    def get(self) -> str:
        return self.variable.get()
    
    def set(self, value: str):
        self.combobox.set(value)


class ActionButton(ctk.CTkButton):
    def __init__(self, parent, text: str, command: Callable, 
                 icon: str = "", **kwargs):
        button_text = f"{icon} {text}" if icon else text
        
        default_kwargs = {
            "text": button_text,
            "command": command,
            "height": 35,
            "font": ("Arial", 14)
        }
        default_kwargs.update(kwargs)
        
        super().__init__(parent, **default_kwargs)


class TwoColumnLayout(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(fg_color="transparent")
        
        self.left = ctk.CTkFrame(self)
        self.right = ctk.CTkFrame(self)
        
        self.left.pack(side="left", expand=True, fill="both", padx=10)
        self.right.pack(side="right", expand=True, fill="both", padx=10)


class LogTextbox(ctk.CTkTextbox):
    def __init__(self, parent, height: int = 150, **kwargs):
        default_kwargs = {
            "height": height,
            "font": ("Consolas", 11),
            "wrap": "word"
        }
        default_kwargs.update(kwargs)
        
        super().__init__(parent, **default_kwargs)
        self.configure(state="disabled")
    
    def log(self, message: str, tag: Optional[str] = None):
        self.configure(state="normal")
        self.insert("end", f"{message}\n", tag)
        self.see("end")
        self.configure(state="disabled")
    
    def clear(self):
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")


class AddressInputGroup(ctk.CTkFrame):
    def __init__(self, parent, initial_address: str = "", **kwargs):
        super().__init__(parent, **kwargs)
        
        addr_parts = initial_address.split(",") if initial_address else ["", "", ""]
        num = addr_parts[0].strip() if len(addr_parts) > 0 else ""
        rue = addr_parts[1].strip() if len(addr_parts) > 1 else ""
        ville = addr_parts[2].strip() if len(addr_parts) > 2 else ""
        
        lbl_frame = ctk.CTkFrame(self, fg_color="transparent")
        lbl_frame.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 2))
        
        ctk.CTkLabel(lbl_frame, text="#", width=50, anchor="w").grid(row=0, column=0, padx=(0, 5))
        ctk.CTkLabel(lbl_frame, text="Rue", width=150, anchor="w").grid(row=0, column=1, padx=(0, 5))
        ctk.CTkLabel(lbl_frame, text="Ville", width=120, anchor="w").grid(row=0, column=2)
        
        self.num_entry = ctk.CTkEntry(self, width=50)
        self.rue_entry = ctk.CTkEntry(self, width=150)
        self.ville_entry = ctk.CTkEntry(self, width=120)
        
        self.num_entry.insert(0, num)
        self.rue_entry.insert(0, rue)
        self.ville_entry.insert(0, ville)
        
        self.num_entry.grid(row=1, column=0, padx=(0, 5))
        self.rue_entry.grid(row=1, column=1, padx=(0, 5))
        self.ville_entry.grid(row=1, column=2)
    
    def get(self) -> str:
        num = self.num_entry.get().strip()
        rue = self.rue_entry.get().strip()
        ville = self.ville_entry.get().strip()
        return f"{num}, {rue}, {ville}"
    
    def get_parts(self) -> Dict[str, str]:
        return {
            "num": self.num_entry.get().strip(),
            "rue": self.rue_entry.get().strip(),
            "ville": self.ville_entry.get().strip()
        }


class PageNavigator(ctk.CTkFrame):
    def __init__(self, parent, prev_command: Callable, next_command: Callable, 
                 save_command: Callable, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.prev_button = ctk.CTkButton(
            self, 
            text="◀ Précédent", 
            command=prev_command
        )
        self.prev_button.pack(side="left", padx=10)
        
        self.next_button = ctk.CTkButton(
            self, 
            text="Suivant ▶", 
            command=next_command
        )
        self.next_button.pack(side="right", padx=10)
        
        self.save_button = ctk.CTkButton(
            self, 
            text="💾 Sauvegarder", 
            command=save_command
        )
    
    def show_save_button(self):
        self.next_button.pack_forget()
        self.save_button.pack(side="right", padx=10)
    
    def show_next_button(self):
        self.save_button.pack_forget()
        self.next_button.pack(side="right", padx=10)
    
    def set_prev_state(self, enabled: bool):
        self.prev_button.configure(state="normal" if enabled else "disabled")


def create_titled_page(parent, title: str) -> tuple[ctk.CTkFrame, ctk.CTkScrollableFrame]:
    page = ctk.CTkFrame(parent)
    
    ctk.CTkLabel(
        page, 
        text=title, 
        font=("Arial", 20, "bold")
    ).pack(pady=15)
    
    scrollable = ctk.CTkScrollableFrame(page)
    scrollable.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    return page, scrollable
