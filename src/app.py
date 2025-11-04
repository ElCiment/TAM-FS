#!/usr/bin/env python3
import customtkinter as ctk
import sys
import os

class TamioFSLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Tamio FS - Sélection du mode")
        self.geometry("500x350")
        self.resizable(False, False)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.create_widgets()
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_widgets(self):
        title_label = ctk.CTkLabel(
            self,
            text="Tamio FS",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack(pady=30)
        
        subtitle_label = ctk.CTkLabel(
            self,
            text="Système de configuration POS",
            font=ctk.CTkFont(size=14)
        )
        subtitle_label.pack(pady=5)
        
        info_label = ctk.CTkLabel(
            self,
            text="Sélectionnez le mode de démarrage :",
            font=ctk.CTkFont(size=12)
        )
        info_label.pack(pady=20)
        
        server_button = ctk.CTkButton(
            self,
            text="🖥️  MODE SERVEUR",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            width=300,
            command=self.launch_server
        )
        server_button.pack(pady=10)
        
        server_desc = ctk.CTkLabel(
            self,
            text="Configuration centrale, paramètres système, MEV",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        server_desc.pack(pady=2)
        
        station_button = ctk.CTkButton(
            self,
            text="💻  MODE STATION",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            width=300,
            command=self.launch_station
        )
        station_button.pack(pady=10)
        
        station_desc = ctk.CTkLabel(
            self,
            text="Configuration poste client, connexion au serveur",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        station_desc.pack(pady=2)
        
    def launch_server(self):
        self.withdraw()
        try:
            from main import XMLConfigWizard
            app = XMLConfigWizard()
            app.mainloop()
        except Exception as e:
            print(f"Erreur lors du lancement du serveur: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.destroy()
            sys.exit(0)
    
    def launch_station(self):
        self.withdraw()
        try:
            from station import StationApp
            app = StationApp()
            app.mainloop()
        except Exception as e:
            print(f"Erreur lors du lancement de la station: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.destroy()
            sys.exit(0)
    
    def on_closing(self):
        self.destroy()
        sys.exit(0)

if __name__ == "__main__":
    app = TamioFSLauncher()
    app.mainloop()
