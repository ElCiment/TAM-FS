import customtkinter as ctk
from tkinter import messagebox
import socket
import sys
import logging
import re
import subprocess
import threading
from config_manager import XMLConfigManager
from validators import DataValidator
from utils import setup_logging, get_com_ports, can_rename_computer, rename_computer_windows
import system_config

logger = setup_logging()

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class XMLConfigWizard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Tamio FS - Assistant de configuration serveur")
        self.geometry("950x700")
        
        self.config_manager = XMLConfigManager()
        self.validator = DataValidator()
        
        self.config_data = self.config_manager.load_config_data()
        self.mev_data = self.config_manager.load_mev_data()
        
        self.is_server = False
        self.config_fields = {}
        self.mev_fields = {}
        self.config_checkboxes = {}
        self.devices_data = self.config_manager.load_devices_data()
        self.printer_type = ctk.StringVar(value="IP")
        self.mev_address_parts = {}
        
        self.pages = []
        self.current_page = 0
        
        self.create_pages()
        self.create_navigation()
        self.show_page(0)
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        logger.info("Application Tamio FS démarrée")

    def create_navigation(self):
        self.nav_frame = ctk.CTkFrame(self)
        self.nav_frame.pack(side="bottom", fill="x", pady=10)
        
        self.prev_button = ctk.CTkButton(
            self.nav_frame, text="◀ Précédent", command=self.prev_page
        )
        self.prev_button.pack(side="left", padx=10)
        
        self.next_button = ctk.CTkButton(
            self.nav_frame, text="Suivant ▶", command=self.next_page
        )
        self.next_button.pack(side="right", padx=10)
        
        self.save_button = ctk.CTkButton(
            self.nav_frame, text="💾 Sauvegarder", command=self.save_all
        )
        self.save_button.pack_forget()

    def create_pages(self):
        self.create_page_general_config()
        self.create_page_mev()
        self.create_page_printer()
        self.create_page_system_config()
        self.create_page_maintenance()
        self.create_page_confirmation()

    def create_page_general_config(self):
        page = ctk.CTkFrame(self)
        
        ctk.CTkLabel(
            page, 
            text="Configuration et paramètres généraux", 
            font=("Arial", 20, "bold")
        ).pack(pady=15)
        
        scrollable = ctk.CTkScrollableFrame(page)
        scrollable.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        container = ctk.CTkFrame(scrollable, fg_color="transparent")
        container.pack(fill="both", expand=True)
        
        left = ctk.CTkFrame(container)
        right = ctk.CTkFrame(container)
        left.pack(side="left", expand=True, fill="both", padx=10)
        right.pack(side="right", expand=True, fill="both", padx=10)
        
        self._create_general_settings_section(left)
        self._create_appearance_section(left)
        self._create_server_section(right)
        self._create_order_modes_section(right)
        
        self.pages.append(page)

    def _create_general_settings_section(self, parent):
        ctk.CTkLabel(parent, text="⚙️ Paramètres généraux", font=("Arial", 16, "bold")).pack(anchor="w", pady=(5, 10))
        
        if can_rename_computer():
            hostname_frame = ctk.CTkFrame(parent)
            hostname_frame.pack(fill="x", pady=(0, 10))
            
            try:
                import platform
                import os
                current_hostname = os.environ.get("COMPUTERNAME", "")
                logger.info(f"[SERVEUR] Nom PC depuis COMPUTERNAME: '{current_hostname}'")
                
                if not current_hostname:
                    logger.warning("[SERVEUR] COMPUTERNAME vide, essai avec socket.gethostname()")
                    current_hostname = socket.gethostname()
                    logger.info(f"[SERVEUR] Nom d'hôte récupéré: '{current_hostname}'")
                
                if not current_hostname:
                    logger.warning("[SERVEUR] Nom vide, essai avec platform.node()")
                    current_hostname = platform.node() or "INCONNU"
                    logger.info(f"[SERVEUR] Utilisation de platform.node(): '{current_hostname}'")
            except Exception as e:
                current_hostname = "INCONNU"
                logger.error(f"[SERVEUR] Impossible d'obtenir le nom du PC: {e}", exc_info=True)
                import traceback
                logger.error(f"[SERVEUR] Traceback complet: {traceback.format_exc()}")
            
            ctk.CTkLabel(hostname_frame, text="Nom de l'ordinateur:", font=("Arial", 12)).pack(side="left", padx=(0, 5))
            
            self.hostname_entry_server = ctk.CTkEntry(
                hostname_frame, 
                width=200,
                height=30,
                font=("Arial", 12)
            )
            self.hostname_entry_server.pack(side="left", padx=(0, 10))
            self.hostname_entry_server.insert(0, current_hostname)
            logger.info(f"[SERVEUR] Nom d'hôte affiché: '{current_hostname}'")
            
            ctk.CTkButton(
                hostname_frame, 
                text="Appliquer",
                command=self.apply_hostname_server,
                height=30,
                font=("Arial", 12)
            ).pack(side="left")
        
        ctk.CTkFrame(parent, height=2, fg_color="gray25").pack(fill="x", pady=10)
        
        general_options = {
            "Auto_Logout": "Déconnexion automatique",
            "Debut_Print": "Afficher impression à l'écran (désactive l'imprimante)"
        }
        
        for key, label in general_options.items():
            var = ctk.BooleanVar(value=self.config_data.get(key, "0") == "1")
            ctk.CTkCheckBox(parent, text=label, variable=var).pack(anchor="w", pady=3)
            self.config_checkboxes[key] = var

    def _create_appearance_section(self, parent):
        ctk.CTkFrame(parent, height=2, fg_color="gray25").pack(fill="x", pady=10)
        ctk.CTkLabel(parent, text="🎨 Apparence", font=("Arial", 16, "bold")).pack(anchor="w", pady=(5, 10))
        
        dark_var = ctk.BooleanVar(value=self.config_data.get("GUI_Dark_Mode", "1") == "1")
        ctk.CTkCheckBox(parent, text="Activer le mode sombre", variable=dark_var).pack(anchor="w", pady=3)
        self.config_checkboxes["GUI_Dark_Mode"] = dark_var
        
        ctk.CTkLabel(parent, text="Taille de police", font=("Arial", 12)).pack(anchor="w", pady=(10, 2))
        font_sizes = [str(x) for x in range(10, 17)]
        current_font = self.config_data.get("GUI_Font_Size", "12") or "12"
        font_dropdown = ctk.CTkComboBox(parent, values=font_sizes, width=100)
        font_dropdown.pack(anchor="w", pady=(0, 5))
        font_dropdown.set(current_font)
        logger.info(f"[SERVEUR] GUI_Font_Size chargé: '{current_font}'")
        self.config_fields["GUI_Font_Size"] = font_dropdown
        
        ctk.CTkLabel(parent, text="Hauteur des lignes", font=("Arial", 12)).pack(anchor="w", pady=(10, 2))
        row_heights = [str(x) for x in range(25, 71, 5)]
        current_height = self.config_data.get("GUI_List_Height", "30") or "30"
        row_dropdown = ctk.CTkComboBox(parent, values=row_heights, width=100)
        row_dropdown.pack(anchor="w", pady=(0, 5))
        row_dropdown.set(current_height)
        logger.info(f"[SERVEUR] GUI_List_Height chargé: '{current_height}'")
        self.config_fields["GUI_List_Height"] = row_dropdown

    def _create_server_section(self, parent):
        ctk.CTkLabel(parent, text="🔗 Configuration serveur", font=("Arial", 16, "bold")).pack(anchor="w", pady=(5, 10))
        
        server_fields = {
            "Server": "Adresse serveur",
            "Database": "Adresse base de données"
        }
        
        for key, label in server_fields.items():
            ctk.CTkLabel(parent, text=label, font=("Arial", 12)).pack(anchor="w", pady=(5, 2))
            entry = ctk.CTkEntry(parent, width=250)
            entry.insert(0, self.config_data.get(key, ""))
            entry.pack(anchor="w", pady=(0, 5))
            self.config_fields[key] = entry
        
        var = ctk.BooleanVar(value=self.config_data.get("Replication", "0") == "1")
        ctk.CTkCheckBox(parent, text="Activer la réplication pour toutes les stations", variable=var).pack(anchor="w", pady=5)
        self.config_checkboxes["Replication"] = var

    def _create_order_modes_section(self, parent):
        ctk.CTkFrame(parent, height=2, fg_color="gray25").pack(fill="x", pady=10)
        ctk.CTkLabel(parent, text="🛒 Modes de commande", font=("Arial", 16, "bold")).pack(anchor="w", pady=(5, 10))
        
        modes = {
            "Use_Floorplan": "Utiliser le plan de table",
            "Use_Retail": "Utiliser le mode retail",
            "Use_Counter": "Vente au comptoir",
            "Use_Pickup": "Ramassage / Pickup",
            "Use_Delivery": "Livraison"
        }
        
        for key, label in modes.items():
            var = ctk.BooleanVar(value=self.config_data.get(key, "1") == "1")
            ctk.CTkCheckBox(parent, text=label, variable=var).pack(anchor="w", pady=3)
            self.config_checkboxes[key] = var

    def create_page_mev(self):
        page = ctk.CTkFrame(self)
        ctk.CTkLabel(page, text="Informations MEV Web", font=("Arial", 20, "bold")).pack(pady=15)
        
        scrollable = ctk.CTkScrollableFrame(page)
        scrollable.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        container = ctk.CTkFrame(scrollable, fg_color="transparent")
        container.pack(fill="both", expand=True)
        
        left = ctk.CTkFrame(container)
        right = ctk.CTkFrame(container)
        left.pack(side="left", expand=True, fill="both", padx=15)
        right.pack(side="right", expand=True, fill="both", padx=15)
        
        labels = {
            "MEV_UserName": "Nom commercial",
            "MEV_Gst": "TPS (9 chiffres)",
            "MEV_Qst": "TVQ (9 chiffres)",
            "MEV_Auth_Code": "Code d'autorisation",
            "MEV_File_Number": "Numéro d'établissement (6 chiffres)",
            "MEV_Address": "Adresse complète",
            "MEV_Zip": "Code postal",
            "MEV_Sector": "Secteur",
            "MEV_Commerce_Name": "Nom usuel du commerce (facultatif)"
        }
        
        keys = list(labels.keys())
        mid = len(keys) // 2
        
        for col, subset in [(left, keys[:mid]), (right, keys[mid:])]:
            for key in subset:
                ctk.CTkLabel(col, text=labels[key], font=("Arial", 12)).pack(anchor="w", pady=(8, 2))
                
                if key == "MEV_Sector":
                    cb = ctk.CTkComboBox(col, values=["RES", "BAR", "CDR"], width=120)
                    cb.set(self.mev_data.get(key, "RES"))
                    cb.pack(anchor="w", pady=(0, 5))
                    self.mev_fields[key] = cb
                
                elif key == "MEV_Address":
                    addr_frame = ctk.CTkFrame(col)
                    addr_frame.pack(pady=(0, 5), fill="x")
                    
                    addr_parts = self.mev_data.get(key, ",,").split(",")
                    num = addr_parts[0].strip() if len(addr_parts) > 0 else ""
                    rue = addr_parts[1].strip() if len(addr_parts) > 1 else ""
                    ville = addr_parts[2].strip() if len(addr_parts) > 2 else ""
                    
                    lbl_frame = ctk.CTkFrame(addr_frame, fg_color="transparent")
                    lbl_frame.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 2))
                    ctk.CTkLabel(lbl_frame, text="#", width=50, anchor="w").grid(row=0, column=0, padx=(0, 5))
                    ctk.CTkLabel(lbl_frame, text="Rue", width=150, anchor="w").grid(row=0, column=1, padx=(0, 5))
                    ctk.CTkLabel(lbl_frame, text="Ville", width=120, anchor="w").grid(row=0, column=2)
                    
                    self.mev_address_parts["num"] = ctk.CTkEntry(addr_frame, width=50)
                    self.mev_address_parts["rue"] = ctk.CTkEntry(addr_frame, width=150)
                    self.mev_address_parts["ville"] = ctk.CTkEntry(addr_frame, width=120)
                    
                    self.mev_address_parts["num"].insert(0, num)
                    self.mev_address_parts["rue"].insert(0, rue)
                    self.mev_address_parts["ville"].insert(0, ville)
                    
                    self.mev_address_parts["num"].grid(row=1, column=0, padx=(0, 5))
                    self.mev_address_parts["rue"].grid(row=1, column=1, padx=(0, 5))
                    self.mev_address_parts["ville"].grid(row=1, column=2)
                    
                    self.mev_fields[key] = self.mev_address_parts
                
                elif key in ["MEV_File_Number", "MEV_Zip"]:
                    e = ctk.CTkEntry(col, width=100)
                    e.insert(0, self.mev_data.get(key, ""))
                    e.pack(anchor="w", pady=(0, 5))
                    self.mev_fields[key] = e
                
                elif key == "MEV_Commerce_Name":
                    e = ctk.CTkEntry(col, width=250, placeholder_text="Ex: Restaurant ABC")
                    e.insert(0, self.mev_data.get(key, ""))
                    e.pack(anchor="w", pady=(0, 5))
                    self.mev_fields[key] = e
                
                else:
                    e = ctk.CTkEntry(col, width=250)
                    e.insert(0, self.mev_data.get(key, ""))
                    e.pack(anchor="w", pady=(0, 5))
                    self.mev_fields[key] = e
        
        self.pages.append(page)

    def create_page_printer(self):
        page = ctk.CTkFrame(self)
        ctk.CTkLabel(page, text="Configuration imprimante reçu (MEV)", font=("Arial", 20, "bold")).pack(pady=30)
        
        ctk.CTkLabel(page, text="Type de connexion :", font=("Arial", 14)).pack(pady=10)
        
        ctk.CTkRadioButton(
            page, text="Imprimante réseau (IP)", 
            variable=self.printer_type, value="IP", 
            command=self.toggle_printer_options
        ).pack(pady=5)
        
        ctk.CTkRadioButton(
            page, text="Imprimante série (COM)", 
            variable=self.printer_type, value="COM", 
            command=self.toggle_printer_options
        ).pack(pady=5)
        
        self.opt_frame = ctk.CTkFrame(page)
        self.opt_frame.pack(pady=20)
        
        self.ip_label = ctk.CTkLabel(self.opt_frame, text="Adresse IP de l'imprimante :", font=("Arial", 12))
        self.ip_entry = ctk.CTkEntry(self.opt_frame, width=200)
        current_ip = self.devices_data.get('ip', '')
        if current_ip:
            self.ip_entry.insert(0, current_ip)
        
        self.com_label = ctk.CTkLabel(self.opt_frame, text="Port COM :", font=("Arial", 12))
        self.com_box = ctk.CTkComboBox(self.opt_frame, values=get_com_ports(), width=200)
        current_com = self.devices_data.get('com', '')
        if current_com:
            self.com_box.set(current_com)
        
        self.baud_label = ctk.CTkLabel(self.opt_frame, text="Baud Rate :", font=("Arial", 12))
        baud_rates = ["1200", "2400", "4800", "9600", "19200", "38400", "57600", "115200"]
        current_baud = self.devices_data.get('baud', '9600')
        self.baud_box = ctk.CTkComboBox(self.opt_frame, values=baud_rates, width=200)
        self.baud_box.set(current_baud)
        logger.info(f"[SERVEUR] Baud Rate chargé: '{current_baud}'")
        
        self.toggle_printer_options()
        self.pages.append(page)

    def toggle_printer_options(self):
        for w in self.opt_frame.winfo_children():
            w.pack_forget()
        
        if self.printer_type.get() == "IP":
            self.ip_label.pack(pady=(0, 5))
            self.ip_entry.pack()
        else:
            self.com_label.pack(pady=(0, 5))
            self.com_box.pack(pady=(0, 10))
            self.baud_label.pack(pady=(10, 5))
            self.baud_box.pack()

    def create_page_system_config(self):
        page = ctk.CTkFrame(self)
        ctk.CTkLabel(page, text="⚙️ Configuration Auto PC", font=("Arial", 20, "bold")).pack(pady=15)
        
        scrollable = ctk.CTkScrollableFrame(page)
        scrollable.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        container = ctk.CTkFrame(scrollable, fg_color="transparent")
        container.pack(fill="both", expand=True)
        
        self.system_config_vars = {}
        
        ctk.CTkLabel(container, text="Cochez les options à appliquer, puis cliquez sur 'Exécuter'", 
                    font=("Arial", 12), text_color="gray").pack(pady=(0, 15))
        
        left_col = ctk.CTkFrame(container, fg_color="transparent")
        right_col = ctk.CTkFrame(container, fg_color="transparent")
        left_col.pack(side="left", expand=True, fill="both", padx=10)
        right_col.pack(side="right", expand=True, fill="both", padx=10)
        
        options_left = [
            ("taskbar", "Optimiser la barre des tâches"),
            ("notifications", "Désactiver les notifications Windows"),
            ("disable_uac", "Désactiver le contrôle UAC"),
            ("disable_network_sleep", "Désactiver veille des cartes réseau"),
            ("network_private", "Mettre carte réseau en mode Privé"),
            ("timezone_sync", "Fuseau horaire Toronto + sync NTP"),
            ("best_performance", "Meilleures performances visuelles"),
        ]
        
        options_right = [
            ("power_options", "Mode alimentation performance"),
            ("restore_context_menu", "Rétablir menu contextuel classique"),
        ]
        
        for key, label in options_left:
            var = ctk.BooleanVar()
            cb = ctk.CTkCheckBox(left_col, text=label, variable=var)
            cb.pack(anchor="w", pady=5)
            self.system_config_vars[key] = var
        
        for key, label in options_right:
            var = ctk.BooleanVar()
            cb = ctk.CTkCheckBox(right_col, text=label, variable=var)
            cb.pack(anchor="w", pady=5)
            self.system_config_vars[key] = var
        
        password_share_frame = ctk.CTkFrame(right_col)
        password_share_frame.pack(anchor="w", pady=10, fill="x")
        
        self.system_config_vars['enable_password_sharing_config'] = ctk.BooleanVar()
        ctk.CTkCheckBox(password_share_frame, text="Partage protégé par mot de passe:", 
                       variable=self.system_config_vars['enable_password_sharing_config']).pack(anchor="w")
        
        self.system_config_vars['password_sharing_action'] = ctk.StringVar(value="Désactiver protection")
        action_menu = ctk.CTkComboBox(password_share_frame, 
                                     values=["Activer protection", "Désactiver protection"],
                                     variable=self.system_config_vars['password_sharing_action'],
                                     width=200)
        action_menu.pack(anchor="w", padx=20, pady=5)
        
        active_hours_frame = ctk.CTkFrame(right_col)
        active_hours_frame.pack(anchor="w", pady=10, fill="x")
        
        self.system_config_vars['active_hours'] = ctk.BooleanVar()
        ctk.CTkCheckBox(active_hours_frame, text="Heures actives (pas de redémarrage auto):", 
                       variable=self.system_config_vars['active_hours']).pack(anchor="w")
        
        hours_selector = ctk.CTkFrame(active_hours_frame, fg_color="transparent")
        hours_selector.pack(anchor="w", padx=20, pady=5)
        
        current_start, current_end = system_config.get_active_hours()
        
        ctk.CTkLabel(hours_selector, text="De:").pack(side="left")
        self.system_config_vars['active_hours_start'] = ctk.StringVar(value=current_start)
        ctk.CTkEntry(hours_selector, textvariable=self.system_config_vars['active_hours_start'], width=50).pack(side="left", padx=5)
        ctk.CTkLabel(hours_selector, text="h à:").pack(side="left")
        self.system_config_vars['active_hours_end'] = ctk.StringVar(value=current_end)
        ctk.CTkEntry(hours_selector, textvariable=self.system_config_vars['active_hours_end'], width=50).pack(side="left", padx=5)
        ctk.CTkLabel(hours_selector, text="h").pack(side="left")
        
        execute_btn = ctk.CTkButton(container, text="▶ Exécuter la configuration",
                                   command=self.execute_system_config,
                                   font=("Arial", 14, "bold"),
                                   height=40,
                                   fg_color="#2ecc71",
                                   hover_color="#27ae60")
        execute_btn.pack(pady=20)
        
        self.pages.append(page)

    def execute_system_config(self):
        log_window = ctk.CTkToplevel(self)
        log_window.title("Exécution de la configuration")
        log_window.geometry("700x500")
        log_window.transient(self)
        log_window.grab_set()
        
        ctk.CTkLabel(log_window, text="Configuration automatique du PC en cours...",
                    font=("Arial", 16, "bold")).pack(pady=10)
        
        log_text = ctk.CTkTextbox(log_window, font=("Courier", 10))
        log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        close_btn = ctk.CTkButton(log_window, text="Fermer", command=log_window.destroy)
        close_btn.pack(pady=10)
        close_btn.configure(state="disabled")
        
        def log_msg(msg):
            log_text.insert("end", f"{msg}\n")
            log_text.see("end")
            log_window.update()
        
        def worker():
            try:
                log_msg("===== AUTO SETUP: CONFIG PC =====")
                
                steps = []
                if self.system_config_vars['taskbar'].get():
                    steps.append(("Tweak barre des tâches", lambda: system_config.tweak_taskbar(log_msg)))
                if self.system_config_vars['notifications'].get():
                    steps.append(("Désactivation notifications", lambda: system_config.disable_windows_notifications(log_msg)))
                if self.system_config_vars['disable_uac'].get():
                    steps.append(("Désactivation UAC", lambda: system_config.disable_uac(log_msg)))
                if self.system_config_vars['disable_network_sleep'].get():
                    steps.append(("Désactivation veille réseau", lambda: system_config.disable_network_sleep(log_msg)))
                if self.system_config_vars['network_private'].get():
                    steps.append(("Carte réseau en mode Privé", lambda: system_config.set_network_private(log_msg)))
                if self.system_config_vars['timezone_sync'].get():
                    steps.append(("Fuseau horaire + sync", lambda: system_config.set_timezone_and_sync(log_msg)))
                if self.system_config_vars['best_performance'].get():
                    steps.append(("Meilleures performances", lambda: system_config.set_best_performance(log_msg)))
                if self.system_config_vars['power_options'].get():
                    steps.append(("Mode alimentation performance", lambda: system_config.set_power_performance(log_msg)))
                
                if self.system_config_vars['enable_password_sharing_config'].get():
                    pw_action = self.system_config_vars['password_sharing_action'].get()
                    if pw_action == "Activer protection":
                        steps.append(("Activation partage protégé", lambda: system_config.enable_password_protected_sharing(log_msg)))
                    elif pw_action == "Désactiver protection":
                        steps.append(("Désactivation partage protégé", lambda: system_config.disable_password_protected_sharing(log_msg)))
                
                if self.system_config_vars['active_hours'].get():
                    start_h = self.system_config_vars['active_hours_start'].get()
                    end_h = self.system_config_vars['active_hours_end'].get()
                    steps.append(("Configuration heures actives", 
                                 lambda sh=start_h, eh=end_h: system_config.set_active_hours(log_msg, sh, eh)))
                
                if self.system_config_vars['restore_context_menu'].get():
                    steps.append(("Rétablir menu contextuel classique", lambda: system_config.restore_context_menu(log_msg)))
                
                if not steps:
                    log_msg("❌ Aucune option sélectionnée!")
                    close_btn.configure(state="normal")
                    return
                
                log_msg(f"\n📋 {len(steps)} étape(s) à exécuter\n")
                
                for i, (name, func) in enumerate(steps, 1):
                    log_msg(f"\n[{i}/{len(steps)}] {name}")
                    log_msg("-" * 50)
                    try:
                        func()
                    except Exception as e:
                        log_msg(f"❌ Erreur: {e}")
                    log_msg("")
                
                log_msg("=" * 50)
                log_msg("✅ Configuration terminée!")
                log_msg("\n⚠️ IMPORTANT: Redémarrez l'ordinateur pour appliquer tous les changements")
                log_msg("=" * 50)
                
            except Exception as e:
                log_msg(f"\n❌ ERREUR CRITIQUE: {e}")
            finally:
                close_btn.configure(state="normal")
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def create_page_maintenance(self):
        page = ctk.CTkFrame(self)
        ctk.CTkLabel(page, text="🛠️ Maintenance système", font=("Arial", 20, "bold")).pack(pady=15)
        
        scrollable = ctk.CTkScrollableFrame(page)
        scrollable.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        container = ctk.CTkFrame(scrollable, fg_color="transparent")
        container.pack(fill="both", expand=True)
        
        uninstall_section = ctk.CTkFrame(container)
        uninstall_section.pack(fill="x", padx=15, pady=(0, 20))
        
        ctk.CTkLabel(uninstall_section, text="⚠️ Désinstallation de logiciels", font=("Arial", 16, "bold")).pack(anchor="w", pady=(5, 10))
        
        uninstall_apps = {
            "Splashtop Streamer": "{B7C5EA94-B96A-41F5-BE95-25D78B486678}",
            "Paymentree": "{7691B95A-0DCC-423E-A583-C2B8AE7DE260}",
            "OpenVPN 2.4.6-I602 (x64)": "{DF3B9B17-6183-47D9-8C7F-DA6C4B9512E9}",
            "TAP-Windows 9.21.2": "{F3C4B17F-3A6F-4E4B-97B2-6DBDDFE6F200}"
        }
        
        self.uninstall_ids = {}
        for app_name, default_id in uninstall_apps.items():
            app_frame = ctk.CTkFrame(uninstall_section)
            app_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(app_frame, text=app_name, font=("Arial", 11), width=180, anchor="w").pack(side="left", padx=(0, 10))
            
            id_entry = ctk.CTkEntry(app_frame, width=280, state="readonly")
            id_entry.pack(side="left", padx=(0, 10))
            if default_id:
                id_entry.configure(state="normal")
                id_entry.insert(0, default_id)
                id_entry.configure(state="readonly")
            self.uninstall_ids[app_name] = id_entry
            
            ctk.CTkButton(
                app_frame,
                text="Désinstaller",
                width=120,
                command=lambda name=app_name: self.uninstall_software(name)
            ).pack(side="left")
        
        ctk.CTkLabel(uninstall_section, text="💡 Les GUID sont fixes et correspondent aux logiciels POS standard", 
                    font=("Arial", 10), text_color="gray", wraplength=400, justify="left").pack(anchor="w", pady=(10, 0))
        
        services_section = ctk.CTkFrame(container)
        services_section.pack(fill="x", padx=15, pady=(10, 20))
        
        ctk.CTkLabel(services_section, text="⚙️ Gestion des services", font=("Arial", 16, "bold")).pack(anchor="w", pady=(10, 10))
        
        services = [
            ("POS Daemon Service", "POSDaemonService"),
            ("MySQL-POS", "MySQL-POS")
        ]
        
        for service_name, service_id in services:
            service_frame = ctk.CTkFrame(services_section)
            service_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(service_frame, text=service_name, font=("Arial", 12), width=180, anchor="w").pack(side="left", padx=(0, 10))
            
            ctk.CTkButton(
                service_frame,
                text="Arrêter",
                width=100,
                command=lambda sid=service_id: self.stop_service(sid)
            ).pack(side="left", padx=(0, 5))
            
            ctk.CTkButton(
                service_frame,
                text="Désactiver",
                width=100,
                command=lambda sid=service_id: self.disable_service(sid)
            ).pack(side="left")
        
        self.pages.append(page)

    def uninstall_software(self, app_name: str):
        product_id = self.uninstall_ids[app_name].get().strip()
        
        if not product_id:
            messagebox.showwarning("ID manquant", f"Veuillez entrer l'ID du produit pour {app_name}")
            return
        
        if not re.match(r'^[{]?[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}[}]?$', product_id):
            messagebox.showerror("ID invalide", "L'ID du produit doit être au format GUID.\n\nExemple: {12345678-1234-1234-1234-123456789ABC}")
            return
        
        confirm = messagebox.askyesno(
            "Confirmation", 
            f"Êtes-vous sûr de vouloir désinstaller '{app_name}'?\n\nID: {product_id}\n\nCette action est irréversible."
        )
        
        if not confirm:
            return
        
        try:
            logger.info(f"Tentative de désinstallation de {app_name} (ID: {product_id})")
            
            result = subprocess.run(
                ['msiexec', '/x', product_id, '/qn', '/norestart'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                messagebox.showinfo("Succès", f"{app_name} a été désinstallé avec succès.")
                logger.info(f"✅ {app_name} désinstallé avec succès")
            else:
                messagebox.showerror("Erreur", f"Échec de la désinstallation.\n\nCode d'erreur: {result.returncode}\n{result.stderr}")
                logger.error(f"❌ Échec désinstallation {app_name}: {result.stderr}")
        
        except subprocess.TimeoutExpired:
            messagebox.showerror("Erreur", "La désinstallation a pris trop de temps (timeout 5min)")
            logger.error(f"Timeout désinstallation {app_name}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la désinstallation: {str(e)}")
            logger.error(f"Erreur désinstallation {app_name}: {e}", exc_info=True)

    def stop_service(self, service_name: str):
        try:
            logger.info(f"Tentative d'arrêt du service: {service_name}")
            
            result = subprocess.run(
                ['net', 'stop', service_name],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                messagebox.showinfo("Succès", f"Le service '{service_name}' a été arrêté.")
                logger.info(f"✅ Service {service_name} arrêté")
            else:
                messagebox.showerror("Erreur", f"Impossible d'arrêter le service.\n\n{result.stderr}")
                logger.error(f"❌ Échec arrêt service {service_name}: {result.stderr}")
        
        except subprocess.TimeoutExpired:
            messagebox.showerror("Erreur", "L'arrêt du service a pris trop de temps (timeout 60s)")
            logger.error(f"Timeout arrêt service {service_name}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {str(e)}")
            logger.error(f"Erreur arrêt service {service_name}: {e}", exc_info=True)

    def disable_service(self, service_name: str):
        confirm = messagebox.askyesno(
            "Confirmation", 
            f"Êtes-vous sûr de vouloir DÉSACTIVER le service '{service_name}'?\n\nLe service ne démarrera plus automatiquement."
        )
        
        if not confirm:
            return
        
        try:
            logger.info(f"Tentative de désactivation du service: {service_name}")
            
            result = subprocess.run(
                ['sc', 'config', service_name, 'start=', 'disabled'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                messagebox.showinfo("Succès", f"Le service '{service_name}' a été désactivé.")
                logger.info(f"✅ Service {service_name} désactivé")
            else:
                messagebox.showerror("Erreur", f"Impossible de désactiver le service.\n\n{result.stderr}")
                logger.error(f"❌ Échec désactivation service {service_name}: {result.stderr}")
        
        except subprocess.TimeoutExpired:
            messagebox.showerror("Erreur", "La désactivation du service a pris trop de temps (timeout 30s)")
            logger.error(f"Timeout désactivation service {service_name}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {str(e)}")
            logger.error(f"Erreur désactivation service {service_name}: {e}", exc_info=True)

    def create_page_confirmation(self):
        page = ctk.CTkFrame(self)
        ctk.CTkLabel(page, text="✅ Configuration terminée", font=("Arial", 24, "bold")).pack(pady=50)
        ctk.CTkLabel(
            page, 
            text="Cliquez sur 'Sauvegarder' pour enregistrer\ntoutes vos modifications.", 
            font=("Arial", 14)
        ).pack(pady=20)
        self.pages.append(page)

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
        if self._validate_current_page():
            if self.current_page < len(self.pages) - 1:
                self.show_page(self.current_page + 1)

    def prev_page(self):
        if self.current_page > 0:
            self.show_page(self.current_page - 1)

    def _validate_current_page(self) -> bool:
        if self.current_page == 1:
            zip_field = self.mev_fields.get("MEV_Zip")
            if zip_field and zip_field.get():
                is_valid, formatted = self.validator.validate_postal_code(zip_field.get())
                if not is_valid:
                    messagebox.showwarning("Validation", f"Code postal : {formatted}")
                    return False
        
        return True

    def save_all(self):
        try:
            data_to_save = {}
            
            for key, widget in self.config_fields.items():
                if isinstance(widget, (ctk.StringVar, ctk.CTkEntry, ctk.CTkComboBox)):
                    value = widget.get() if hasattr(widget, 'get') else str(widget)
                    data_to_save[key] = value
            
            for key, var in self.config_checkboxes.items():
                data_to_save[key] = "1" if var.get() else "0"
            
            address_num = ""
            address_street = ""
            address_city = ""
            
            for key, widget in self.mev_fields.items():
                if key == "MEV_Address":
                    parts = self.mev_address_parts
                    num = parts["num"].get().strip()
                    rue = parts["rue"].get().strip()
                    ville = parts["ville"].get().strip()
                    data_to_save[key] = f"{num}, {rue}, {ville}"
                    
                    address_num = num
                    address_street = rue
                    address_city = ville
                else:
                    value = widget.get() if hasattr(widget, 'get') else str(widget)
                    data_to_save[key] = value
            
            protocol_value = "Web Network Printer" if self.printer_type.get() == "IP" else "Web"
            
            devices_to_save = {
                'ip': self.ip_entry.get().strip(),
                'com': self.com_box.get().strip(),
                'baud': self.baud_box.get().strip(),
                'protocol': protocol_value
            }
            
            config_saved = self.config_manager.save_config_data(data_to_save)
            devices_saved = self.config_manager.save_devices_data(devices_to_save)
            
            if config_saved:
                logger.info("Configuration sauvegardée dans config.xml avec succès")
                
                commerce_name = data_to_save.get("MEV_Commerce_Name", "")
                postal_code = data_to_save.get("MEV_Zip", "")
                
                layout_updated = self.config_manager.update_layout_header(
                    commerce_name=commerce_name,
                    address_num=address_num,
                    address_street=address_street,
                    city=address_city,
                    postal_code=postal_code
                )
                
                menu_updated = self.config_manager.ensure_receipt_printer_in_menu()
                
                if devices_saved:
                    logger.info(f"Devices.xml sauvegardé avec succès : IP={devices_to_save['ip']}, COM={devices_to_save['com']}, Baud={devices_to_save['baud']}")
                
                if layout_updated and devices_saved and menu_updated:
                    messagebox.showinfo("Succès", "Tous les fichiers sauvegardés avec succès!\n(config.xml, devices.xml, layout.xml, menu.xml)")
                    logger.info("Tous les fichiers mis à jour avec succès")
                elif devices_saved:
                    files_ok = ["config.xml", "devices.xml"]
                    files_ko = []
                    if not layout_updated:
                        files_ko.append("layout.xml")
                    if not menu_updated:
                        files_ko.append("menu.xml")
                    
                    msg = f"Fichiers sauvegardés : {', '.join(files_ok)}"
                    if files_ko:
                        msg += f"\n\nFichiers non mis à jour : {', '.join(files_ko)}"
                    messagebox.showinfo("Succès partiel", msg)
                    logger.warning(f"Certains fichiers non mis à jour : {files_ko}")
                else:
                    messagebox.showinfo("Succès partiel", "Configuration sauvegardée mais certains fichiers XML non mis à jour.")
                    logger.warning("Certains fichiers XML non mis à jour")
            else:
                messagebox.showerror("Erreur", "Échec de la sauvegarde de la configuration")
                logger.error("Échec de la sauvegarde")
        
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde : {e}")
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde : {e}")
    
    def apply_hostname_server(self):
        new_name = self.hostname_entry_server.get().strip()
        logger.info(f"[SERVEUR] Tentative de changement de nom: '{new_name}'")
        
        is_valid, message = self.validator.validate_hostname(new_name)
        if not is_valid:
            messagebox.showwarning("Nom invalide", message)
            return
        
        success, result_message = rename_computer_windows(new_name)
        if success:
            messagebox.showinfo("Succès", result_message)
            logger.info(f"[SERVEUR] Nom d'ordinateur changé: {new_name}")
        else:
            messagebox.showerror("Erreur", result_message)
            logger.error(f"[SERVEUR] Échec changement de nom: {result_message}")
    
    def on_closing(self):
        logger.info("Fermeture de l'application serveur")
        self.destroy()
        sys.exit(0)


if __name__ == "__main__":
    try:
        app = XMLConfigWizard()
        app.mainloop()
    except Exception as e:
        logger.critical(f"Erreur fatale : {e}", exc_info=True)
        raise
    finally:
        sys.exit(0)
