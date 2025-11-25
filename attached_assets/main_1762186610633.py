import customtkinter as ctk
from tkinter import messagebox
import xml.etree.ElementTree as ET
import serial.tools.list_ports
import os
import re
import socket
import sys
import subprocess
import win32api
import time

# --- CONFIG DE BASE ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class XMLConfigWizard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Assistant de configuration XML")
        self.geometry("900x650")

        # Fichiers XML (chemins à adapter si besoin)
        self.config_path = r"c:\pos\xml\config.xml"
        self.devices_path = r"c:\pos\xml\devices.xml"

        # Données
        self.config_data = self.load_config_data()
        self.mev_data = self.load_mev_data()

        # Variables
        self.is_server = False
        self.config_fields = {}
        self.mev_fields = {}
        self.config_checkboxes = {}
        self.printer_entries = {}
        self.printer_type = ctk.StringVar(value="IP")

        # Pages
        self.pages = []
        self.current_page = 0

        self.create_pages()

        # Navigation
        self.nav_frame = ctk.CTkFrame(self)
        self.nav_frame.pack(side="bottom", fill="x", pady=10)
        self.prev_button = ctk.CTkButton(self.nav_frame, text="Précédent", command=self.prev_page)
        self.prev_button.pack(side="left", padx=10)
        self.next_button = ctk.CTkButton(self.nav_frame, text="Suivant", command=self.next_page)
        self.next_button.pack(side="right", padx=10)
        self.save_button = ctk.CTkButton(self.nav_frame, text="Sauvegarder", command=self.save_all)
        self.save_button.pack_forget()

        self.show_page(0)

    # --- CHARGEMENT DONNÉES XML ---
    def load_config_data(self):
        data = {}
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding="utf-8") as f:
                content = f.read()
                keys = ["Database", "Server", "Replication", "Auto_Logout", "GUI_Dark_Mode",
                        "Debut_Print", "Auto_Print", "Use_Floorplan", "Use_Retail",
                        "Use_Counter", "Use_Pickup", "Use_Delivery"]
                for key in keys:
                    m = re.search(rf'{key}="([^"]*)"', content)
                    if m:
                        data[key] = m.group(1)
        return data

    def load_mev_data(self):
        data = {}
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding="utf-8") as f:
                content = f.read()
                keys = ["MEV_UserName", "MEV_Gst", "MEV_Qst", "MEV_Auth_Code",
                        "MEV_File_Number", "MEV_Address", "MEV_Zip", "MEV_Sector"]
                for key in keys:
                    m = re.search(rf'{key}="([^"]*)"', content)
                    if m:
                        data[key] = m.group(1)
        return data

    # --- PAGES ---
    def create_pages(self):
        # 1️⃣ Type
        page1 = ctk.CTkFrame(self)
        ctk.CTkLabel(page1, text="Est-ce un serveur ou une station ?", font=("Arial", 18, "bold")).pack(pady=30)

        # Bouton Station → ferme ce programme et lance station.py
        def launch_station():
            try:
                # ferme l'app actuelle
                self.destroy()
                # lance station.py dans un nouveau processus
                subprocess.Popen([sys.executable, "station.py"])
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de lancer station : {e}")

        ctk.CTkButton(page1, text="Station", command=launch_station).pack(pady=10)

        # Bouton Serveur → passe à la page 2
        ctk.CTkButton(page1, text="Serveur", command=lambda: self.show_page(1)).pack(pady=10)

        self.pages.append(page1)


        # 🧩 PAGE — Serveur + Paramètres généraux / Modes / Apparence
        page2 = ctk.CTkFrame(self)

        # --- Titre général ---
        ctk.CTkLabel(page2, text="Configuration et paramètres généraux", font=("Arial", 18, "bold")).pack(pady=10)

        # --- Conteneur principal pour 2 colonnes ---
        container = ctk.CTkFrame(page2)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        left = ctk.CTkFrame(container)
        right = ctk.CTkFrame(container)
        left.pack(side="left", expand=True, fill="both", padx=10)
        right.pack(side="right", expand=True, fill="both", padx=10)

        # 🟢 SECTION CONFIGURATION GÉNÉRALE (colonne gauche)
        ctk.CTkLabel(left, text="⚙️ Paramètres généraux", font=("Arial", 14, "bold")).pack(anchor="w", pady=(5, 8))

        # --- Frame pour le nom de l'ordinateur ---
        hostname_frame = ctk.CTkFrame(left)
        hostname_frame.pack(fill="x", pady=(0, 10))

        modify_var = ctk.BooleanVar(value=False)

        def toggle_hostname_entry():
            if modify_var.get():
                hostname_entry.configure(state="normal")
                apply_btn.configure(state="normal")
            else:
                hostname_entry.configure(state="disabled")
                apply_btn.configure(state="disabled")

        # Case à cocher
        ctk.CTkCheckBox(hostname_frame, text="Modifier le nom de l'ordinateur", variable=modify_var,
                        command=toggle_hostname_entry).pack(side="left", padx=(0, 10))

        # Champ texte
        current_hostname = socket.gethostname()
        hostname_var = ctk.StringVar(value=current_hostname)
        hostname_entry = ctk.CTkEntry(hostname_frame, textvariable=hostname_var, width=150, state="disabled")
        hostname_entry.pack(side="left", padx=(0, 5))

        # Bouton appliquer
        def apply_hostname():
            new_name = hostname_var.get().strip()
            if not new_name:
                messagebox.showwarning("Nom invalide", "Le nom de l'ordinateur ne peut pas être vide.")
                return
            try:
                subprocess.run(["wmic", "computersystem", "where", "name='%s'" % current_hostname,
                                "rename", new_name], check=True)
                messagebox.showinfo("Succès", f"Nom de l'ordinateur changé en '{new_name}'.\nRedémarrage nécessaire.")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de changer le nom : {e}")

        apply_btn = ctk.CTkButton(hostname_frame, text="Appliquer", command=apply_hostname, state="disabled")
        apply_btn.pack(side="left")

        # --- Ligne de séparation ---
        separator1 = ctk.CTkFrame(left, height=2, fg_color="gray25")
        separator1.pack(fill="x", pady=(10, 10))

        # --- Options générales existantes ---
        general_labels = {
            "Auto_Logout": "Déconnexion automatique",
            "Debut_Print": "Afficher Impression à l’écran (désactive l’imprimante)"
        }

        for key, label in general_labels.items():
            var = ctk.BooleanVar(value=self.config_data.get(key, "0") == "1")
            chk = ctk.CTkCheckBox(left, text=label, variable=var)
            chk.pack(anchor="w", pady=3)
            self.config_checkboxes[key] = var

        # 🎨 SECTION APPARENCE (Mode sombre, colonne gauche)
        separator_left = ctk.CTkFrame(left, height=2, fg_color="gray25")
        separator_left.pack(fill="x", pady=10)
        ctk.CTkLabel(left, text="🎨 Apparence", font=("Arial", 14, "bold")).pack(anchor="w", pady=(5, 8))

        # --- Case à cocher Mode sombre ---
        dark_var = ctk.BooleanVar(value=self.config_data.get("GUI_Dark_Mode", "1") == "1")
        chk_dark = ctk.CTkCheckBox(left, text="Activer le mode sombre", variable=dark_var)
        chk_dark.pack(anchor="w", pady=3)
        self.config_checkboxes["GUI_Dark_Mode"] = dark_var

        # --- Menu déroulant Font Size ---
        ctk.CTkLabel(left, text="Taille de police", font=("Arial", 12)).pack(anchor="w", pady=(10, 2))
        font_sizes = [str(x) for x in [10, 11, 12, 13, 14]]
        font_var = ctk.StringVar(value=self.config_data.get("GUI_Font_Size", "12"))
        font_dropdown = ctk.CTkComboBox(left, values=font_sizes, variable=font_var, width=80)
        font_dropdown.pack(anchor="w", pady=(0, 5))
        font_dropdown.set(font_var.get())  # <-- force l'affichage de la valeur actuelle
        self.config_fields["GUI_Font_Size"] = font_var

        # --- Menu déroulant Row Height ---
        ctk.CTkLabel(left, text="Hauteur des lignes", font=("Arial", 12)).pack(anchor="w", pady=(10, 2))
        row_heights = [str(x) for x in [25,28,30,32,35,38,40,42,45,48,49,50,51,52,53,54,55,60,65,70]]
        row_var = ctk.StringVar(value=self.config_data.get("GUI_List_Height", "30"))
        row_dropdown = ctk.CTkComboBox(left, values=row_heights, variable=row_var, width=80)
        row_dropdown.pack(anchor="w", pady=(0, 5))
        row_dropdown.set(row_var.get())  # <-- force l'affichage de la valeur actuelle
        self.config_fields["GUI_List_Height"] = row_var




        # 🔗 SECTION SERVEUR (colonne droite, en haut)
        ctk.CTkLabel(right, text="🔗 Serveur", font=("Arial", 14, "bold")).pack(anchor="w", pady=(5, 8))

        serveur_labels = {
            "Server": "Adresse: serveur",
            "Database": "Adresse: base de données",
            "Replication": "Activer Pour tout les Stations"
        }

        for key, label in serveur_labels.items():
            ctk.CTkLabel(right, text=label).pack(anchor="w", pady=(2, 0))
            if key == "Replication":
                var = ctk.BooleanVar(value=self.config_data.get(key, "0") == "1")
                chk = ctk.CTkCheckBox(right, text="Oui", variable=var)
                chk.pack(anchor="w", pady=(0, 5))
                self.config_checkboxes[key] = var
            else:
                entry = ctk.CTkEntry(right)
                entry.insert(0, self.config_data.get(key, ""))
                entry.pack(anchor="w", pady=(0, 5))
                self.config_fields[key] = entry

        # 🟣 SECTION MODES DE COMMANDE (colonne droite, sous Serveur)
        ctk.CTkLabel(right, text="🛒 Modes de commande", font=("Arial", 14, "bold")).pack(anchor="w", pady=(10, 8))

        mode_labels = {
            "Use_Floorplan": "Utiliser le plan de table",
            "Use_Retail": "Utiliser le mode retail",
            "Use_Counter": "Vente au comptoir",
            "Use_Pickup": "Ramasse / Pickup",
            "Use_Delivery": "Livraison"
        }

        for key, label in mode_labels.items():
            var = ctk.BooleanVar(value=self.config_data.get(key, "1") == "1")
            chk = ctk.CTkCheckBox(right, text=label, variable=var)
            chk.pack(anchor="w", pady=3)
            self.config_checkboxes[key] = var

        self.pages.append(page2)




        # 4️⃣ MEV Web (2 colonnes ajustées et harmonieuses)
        page3 = ctk.CTkFrame(self)
        ctk.CTkLabel(page3, text="Informations MEV Web", font=("Arial", 18, "bold")).pack(pady=10)

        container = ctk.CTkFrame(page3)
        container.pack(pady=10, fill="x", expand=True)

        # Colonnes gauche/droite
        left = ctk.CTkFrame(container)
        right = ctk.CTkFrame(container)
        left.pack(side="left", expand=True, fill="both", padx=15)
        right.pack(side="right", expand=True, fill="both", padx=15)

        labels = {
            "MEV_UserName": "Nom commercial",
            "MEV_Gst": "TPS",
            "MEV_Qst": "TVQ",
            "MEV_Auth_Code": "Code d’autorisation",
            "MEV_File_Number": "Numéro d’établissement",
            "MEV_Address": "Adresse complète",
            "MEV_Zip": "Code postal",
            "MEV_Sector": "Secteur (RES/BAR/CDR)"
        }

        keys = list(labels.keys())
        mid = len(keys)//2

        self.mev_address_parts = {}

        for col, subset in [(left, keys[:mid]), (right, keys[mid:])]:
            for key in subset:
                ctk.CTkLabel(col, text=labels[key]).pack(anchor="w", pady=(3, 0))

                # --- Menu déroulant du secteur ---
                if key == "MEV_Sector":
                    cb = ctk.CTkComboBox(col, values=["RES", "BAR", "CDR"], width=100)
                    cb.set(self.mev_data.get(key, ""))
                    cb.pack(anchor="w", pady=(0, 5))
                    self.mev_fields[key] = cb

                # --- Adresse complète en 3 champs ---
                elif key == "MEV_Address":
                    addr_frame = ctk.CTkFrame(col)
                    addr_frame.pack(pady=(0, 5), fill="x")

                    addr_parts = (self.mev_data.get(key, "").split(",") if self.mev_data.get(key) else ["", "", ""])
                    num = addr_parts[0].strip() if len(addr_parts) > 0 else ""
                    rue = addr_parts[1].strip() if len(addr_parts) > 1 else ""
                    ville = addr_parts[2].strip() if len(addr_parts) > 2 else ""

                    # 🔹 Labels au-dessus de chaque champ (parfaitement alignés)
                    lbl_frame = ctk.CTkFrame(addr_frame, fg_color="transparent")
                    lbl_frame.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 2))
                    ctk.CTkLabel(lbl_frame, text="#", width=50, anchor="w").grid(row=0, column=0, padx=(0, 5))
                    ctk.CTkLabel(lbl_frame, text="Rue", width=150, anchor="w").grid(row=0, column=1, padx=(0, 5))
                    ctk.CTkLabel(lbl_frame, text="Ville", width=120, anchor="w").grid(row=0, column=2, padx=(0, 5))

                    # 🔹 Champs alignés sous leurs labels
                    self.mev_address_parts["num"] = ctk.CTkEntry(addr_frame, width=50)
                    self.mev_address_parts["rue"] = ctk.CTkEntry(addr_frame, width=150)
                    self.mev_address_parts["ville"] = ctk.CTkEntry(addr_frame, width=120)

                    self.mev_address_parts["num"].insert(0, num)
                    self.mev_address_parts["rue"].insert(0, rue)
                    self.mev_address_parts["ville"].insert(0, ville)

                    self.mev_address_parts["num"].grid(row=1, column=0, padx=(0, 5))
                    self.mev_address_parts["rue"].grid(row=1, column=1, padx=(0, 5))
                    self.mev_address_parts["ville"].grid(row=1, column=2, padx=(0, 5))

                    self.mev_fields[key] = self.mev_address_parts


                # --- Numéro d’établissement : petit champ (6 caractères) ---
                elif key == "MEV_File_Number":
                    e = ctk.CTkEntry(col, width=80)
                    e.insert(0, self.mev_data.get(key, ""))
                    e.pack(anchor="w", pady=(0, 5))
                    self.mev_fields[key] = e

                # --- Code postal : petit champ (6 caractères) ---
                elif key == "MEV_Zip":
                    e = ctk.CTkEntry(col, width=80)
                    e.insert(0, self.mev_data.get(key, ""))
                    e.pack(anchor="w", pady=(0, 5))
                    self.mev_fields[key] = e

                # --- Champs standard ---
                else:
                    e = ctk.CTkEntry(col, width=220)
                    e.insert(0, self.mev_data.get(key, ""))
                    e.pack(anchor="w", pady=(0, 5))
                    self.mev_fields[key] = e

        self.pages.append(page3)



        # 5️⃣ Type imprimante
        page4 = ctk.CTkFrame(self)
        ctk.CTkLabel(page4, text="Type d’imprimante Recu (MEV)", font=("Arial", 18, "bold")).pack(pady=10)
        ctk.CTkRadioButton(page4, text="IP", variable=self.printer_type, value="IP", command=self.toggle_printer_options).pack(pady=5)
        ctk.CTkRadioButton(page4, text="COM", variable=self.printer_type, value="COM", command=self.toggle_printer_options).pack(pady=5)
        self.opt_frame = ctk.CTkFrame(page4)
        self.opt_frame.pack(pady=10)
        self.ip_label = ctk.CTkLabel(self.opt_frame, text="Adresse IP :")
        self.ip_entry = ctk.CTkEntry(self.opt_frame)
        self.com_label = ctk.CTkLabel(self.opt_frame, text="Port COM :")
        self.com_box = ctk.CTkComboBox(self.opt_frame, values=self.get_com_ports())
        self.toggle_printer_options()
        self.pages.append(page4)



        # 9️⃣ Confirmation
        page5 = ctk.CTkFrame(self)
        ctk.CTkLabel(page5, text="✅ Configuration terminée", font=("Arial", 18, "bold")).pack(pady=30)
        self.pages.append(page5)

    # --- NAVIGATION ---
    def show_page(self, i):
        for p in self.pages:
            p.pack_forget()
        self.pages[i].pack(fill="both", expand=True)
        self.current_page = i
        self.prev_button.configure(state="normal" if i > 0 else "disabled")
        if i == len(self.pages) - 1:
            self.next_button.pack_forget()
            self.save_button.pack(side="right", padx=10)
        else:
            self.save_button.pack_forget()
            self.next_button.pack(side="right", padx=10)


    def next_page(self):
        if self.current_page < len(self.pages) - 1:
           self.show_page(self.current_page + 1)

    def prev_page(self):
        if self.current_page > 0:
            self.show_page(self.current_page - 1)

        def set_type(self, server):
            self.is_server = server
            self.show_page(1)

        # --- MÉTHODE À L'INTÉRIEUR DE LA CLASSE ---
    def toggle_printer_options(self):
        for w in self.opt_frame.winfo_children():
            w.pack_forget()
        if self.printer_type.get() == "IP":
            self.ip_label.pack()
            self.ip_entry.pack()
        else:
            self.com_label.pack()
            self.com_box.pack()



        # --- SAUVEGARDE ---
    def save_all(self):
        self.save_config()
        self.save_mev()
        messagebox.showinfo("Sauvegarde", "Toutes les modifications ont été enregistrées avec succès.")


    def save_config(self):
        """Sauvegarde des paramètres généraux et apparence"""
        if not os.path.exists(self.config_path):
            return

        with open(self.config_path, 'r', encoding="utf-8") as f:
            content = f.read()

        # 🔹 Champs texte et ComboBox (StringVar)
        for key, widget in self.config_fields.items():
            if isinstance(widget, ctk.StringVar):
                value = widget.get()
            elif isinstance(widget, ctk.CTkEntry):
                value = widget.get()
            elif isinstance(widget, ctk.CTkComboBox):
                value = widget.get()
            else:
                value = str(widget)  # sécurité
            content = re.sub(rf'{key}="[^"]*"', f'{key}="{value}"', content)

        # 🔹 Cases à cocher (BooleanVar)
        for key, var in self.config_checkboxes.items():
            val = "1" if var.get() else "0"
            content = re.sub(rf'{key}="[^"]*"', f'{key}="{val}"', content)

        # 🔹 Écriture dans le fichier XML
        with open(self.config_path, 'w', encoding="utf-8") as f:
            f.write(content)



    def save_mev(self):
        """Sauvegarde des paramètres MEV Web"""
        if not os.path.exists(self.config_path):
            return

        with open(self.config_path, 'r', encoding="utf-8") as f:
            content = f.read()

        for key, widget in self.mev_fields.items():
            # 🔸 Cas spécial : adresse composée
            if key == "MEV_Address":
                parts = self.mev_address_parts
                num = parts["num"].get().strip()
                rue = parts["rue"].get().strip()
                ville = parts["ville"].get().strip()
                val = f"{num}, {rue}, {ville}"

            # 🔸 ComboBox (secteur)
            elif isinstance(widget, ctk.CTkComboBox):
                val = widget.get().strip()

            # 🔸 Champ normal
            else:
                val = widget.get().strip()

            content = re.sub(rf'{key}="[^"]*"', f'{key}="{val}"', content)

        with open(self.config_path, 'w', encoding="utf-8") as f:
            f.write(content)

    # --- UTILITAIRES ---
    def get_com_ports(self):
        return [p.device for p in serial.tools.list_ports.comports()] or ["Aucun"]

# --- LANCEMENT ---
if __name__ == "__main__":
    app = XMLConfigWizard()
    app.mainloop()
