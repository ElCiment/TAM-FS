import customtkinter as ctk
from tkinter import messagebox
import socket
import subprocess
import shutil
import os
import xml.etree.ElementTree as ET

class StationApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Station POS")
        self.geometry("500x400")

        # Nom de l'ordinateur
        ctk.CTkLabel(self, text="Nom de l'ordinateur").pack(pady=(20, 5))
        self.hostname_var = ctk.StringVar(value=socket.gethostname())
        self.hostname_entry = ctk.CTkEntry(self, textvariable=self.hostname_var, width=200)
        self.hostname_entry.pack(pady=(0,5))
        ctk.CTkButton(self, text="Appliquer", command=self.apply_hostname).pack(pady=(0,10))

        # Adresse IP du serveur
        ctk.CTkLabel(self, text="Adresse IP du serveur").pack(pady=(10, 5))
        self.server_ip_var = ctk.StringVar()
        self.server_ip_entry = ctk.CTkEntry(self, textvariable=self.server_ip_var, width=200)
        self.server_ip_entry.pack(pady=(0,5))
        ctk.CTkButton(self, text="Appliquer IP et copier fichiers", command=self.apply_ip_and_copy).pack(pady=(0,10))

    def apply_hostname(self):
        new_name = self.hostname_var.get().strip()
        if not new_name:
            messagebox.showwarning("Nom invalide", "Le nom de l'ordinateur ne peut pas être vide.")
            return
        try:
            subprocess.run(["wmic", "computersystem", "where", "name='%s'" % socket.gethostname(),
                            "rename", new_name], check=True)
            messagebox.showinfo("Succès", f"Nom de l'ordinateur changé en '{new_name}'. Redémarrage nécessaire.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de changer le nom : {e}")

    def apply_ip_and_copy(self):
        ip = self.server_ip_var.get().strip()
        if not ip:
            messagebox.showwarning("IP invalide", "Veuillez entrer l'adresse IP du serveur.")
            return

        # Copier les fichiers depuis le serveur
        try:
            files = ["config.xml", "menu.xml", "Floor.xml", "layout.xml"]
            dest_folder = r"C:\pos\xml"
            os.makedirs(dest_folder, exist_ok=True)
            for f in files:
                src = f"\\\\{ip}\\xml\\{f}"
                dst = os.path.join(dest_folder, f)
                shutil.copy2(src, dst)
            
            # Modifier les champs 'Server' et 'Database' dans config.xml
            config_path = os.path.join(dest_folder, "config.xml")
            tree = ET.parse(config_path)
            root = tree.getroot()
            # Supposons que les champs sont <Server> et <Database>
            server_elem = root.find("Server")
            if server_elem is not None:
                server_elem.text = ip
            database_elem = root.find("Database")
            if database_elem is not None:
                database_elem.text = "NomDeLaBase"  # ou garder la valeur actuelle
            tree.write(config_path)
            
            messagebox.showinfo("Succès", "Fichiers copiés et config mise à jour.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de copier les fichiers : {e}")


if __name__ == "__main__":
    app = StationApp()
    app.mainloop()
