import customtkinter as ctk
from tkinter import messagebox
import socket
import shutil
import os
import sys
import logging
import re
import subprocess
import threading
import xml.etree.ElementTree as ET
from validators import DataValidator
from config_manager import XMLConfigManager
from utils import setup_logging, can_rename_computer, rename_computer_windows
import system_config

logger = setup_logging()

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class StationApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Tamio FS - Configuration Station POS")
        self.geometry("600x400")
        
        self.validator = DataValidator()
        self.config_manager = XMLConfigManager()
        
        self.config_data = self.config_manager.load_config_data([
            "GUI_Font_Size", "GUI_List_Height", "GUI_Dark_Mode"
        ])
        
        self.create_ui()
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        logger.info("Application Station POS démarrée")

    def create_ui(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            main_frame, 
            text="Configuration Station POS", 
            font=("Arial", 24, "bold")
        ).pack(pady=(0, 20))
        
        top_row = ctk.CTkFrame(main_frame, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 10))
        
        bottom_row = ctk.CTkFrame(main_frame, fg_color="transparent")
        bottom_row.pack(fill="x", pady=(0, 10))
        
        has_hostname = can_rename_computer()
        
        if has_hostname:
            self._create_hostname_section(top_row, side="left")
            self._create_server_section(top_row, side="right")
        else:
            self._create_server_section(top_row, side="top")
        
        self._create_database_section(bottom_row, side="left")
        
        buttons_frame = ctk.CTkFrame(bottom_row)
        buttons_frame.pack(side="right", expand=True, fill="both", padx=10)
        
        self._create_maintenance_button(buttons_frame)
        self._create_system_config_button(buttons_frame)

    def _create_hostname_section(self, parent, side="left"):
        hostname_frame = ctk.CTkFrame(parent)
        hostname_frame.pack(side=side, expand=True, fill="both", padx=10)
        
        ctk.CTkLabel(
            hostname_frame, 
            text="Nom de l'ordinateur", 
            font=("Arial", 16, "bold")
        ).pack(pady=(10, 5))
        
        try:
            import platform
            import os
            current_hostname = os.environ.get("COMPUTERNAME", "")
            logger.info(f"[STATION] Nom PC depuis COMPUTERNAME: '{current_hostname}'")
            
            if not current_hostname:
                logger.warning("[STATION] COMPUTERNAME vide, essai avec socket.gethostname()")
                current_hostname = socket.gethostname()
                logger.info(f"[STATION] Nom d'hôte récupéré: '{current_hostname}'")
            
            if not current_hostname:
                logger.warning("[STATION] Nom vide, essai avec platform.node()")
                current_hostname = platform.node() or "INCONNU"
                logger.info(f"[STATION] Utilisation de platform.node(): '{current_hostname}'")
        except Exception as e:
            current_hostname = "INCONNU"
            logger.error(f"[STATION] Impossible d'obtenir le nom du PC: {e}", exc_info=True)
            import traceback
            logger.error(f"[STATION] Traceback complet: {traceback.format_exc()}")
        
        self.hostname_entry = ctk.CTkEntry(
            hostname_frame, 
            width=300,
            height=35,
            font=("Arial", 14)
        )
        self.hostname_entry.pack(pady=(0, 10))
        self.hostname_entry.insert(0, current_hostname)
        logger.info(f"[STATION] Nom d'hôte affiché: '{current_hostname}'")
        
        ctk.CTkButton(
            hostname_frame, 
            text="Appliquer le nom d'ordinateur",
            command=self.apply_hostname,
            height=35,
            font=("Arial", 14)
        ).pack(pady=(0, 10))

    def _create_server_section(self, parent, side="left"):
        server_frame = ctk.CTkFrame(parent)
        if side == "top":
            server_frame.pack(fill="x", padx=10)
        else:
            server_frame.pack(side=side, expand=True, fill="both", padx=10)
        
        ctk.CTkLabel(
            server_frame, 
            text="Adresse IP du serveur", 
            font=("Arial", 16, "bold")
        ).pack(pady=(10, 5))
        
        self.server_ip_var = ctk.StringVar()
        self.server_entry = ctk.CTkEntry(
            server_frame, 
            textvariable=self.server_ip_var, 
            width=300,
            height=35,
            font=("Arial", 14),
            placeholder_text="Ex: 192.168.1.100"
        )
        self.server_entry.pack(pady=(0, 10))
        
        ctk.CTkButton(
            server_frame, 
            text="Copier les fichiers de configuration",
            command=self.apply_ip_and_copy,
            height=35,
            font=("Arial", 14)
        ).pack(pady=(0, 10))
    
    def _create_database_section(self, parent, side="left"):
        db_frame = ctk.CTkFrame(parent)
        db_frame.pack(side=side, expand=True, fill="both", padx=10)
        
        ctk.CTkLabel(
            db_frame, 
            text="Gestion base de données", 
            font=("Arial", 16, "bold")
        ).pack(pady=(10, 5))
        
        ctk.CTkButton(
            db_frame, 
            text="🗑️ Supprimer le dossier MySQL",
            command=self.delete_mysql_folder,
            height=35,
            font=("Arial", 14),
            fg_color="#d32f2f",
            hover_color="#9a0007"
        ).pack(pady=(0, 10))

    def delete_mysql_folder(self):
        mysql_path = r"c:\pos\mysql"
        
        confirm = messagebox.askyesno(
            "⚠️ Confirmation requise", 
            f"Êtes-vous sûr de vouloir SUPPRIMER DÉFINITIVEMENT le dossier:\n\n{mysql_path}\n\n"
            "⚠️ Cette action est IRRÉVERSIBLE!\n"
            "Toutes les données de la base de données seront PERDUES."
        )
        
        if not confirm:
            logger.info("[STATION] Suppression MySQL annulée par l'utilisateur")
            return
        
        second_confirm = messagebox.askyesno(
            "⚠️ Dernière confirmation", 
            "ATTENTION : Confirmez-vous vraiment la suppression?\n\n"
            "Cette action supprimera toute la base de données MySQL!"
        )
        
        if not second_confirm:
            logger.info("[STATION] Suppression MySQL annulée (2e confirmation)")
            return
        
        try:
            if os.path.exists(mysql_path):
                logger.info(f"[STATION] Suppression du dossier MySQL: {mysql_path}")
                shutil.rmtree(mysql_path)
                messagebox.showinfo("Succès", f"Le dossier {mysql_path} a été supprimé avec succès.")
                logger.info(f"✅ [STATION] Dossier MySQL supprimé: {mysql_path}")
            else:
                messagebox.showwarning("Dossier introuvable", f"Le dossier {mysql_path} n'existe pas.")
                logger.warning(f"[STATION] Dossier MySQL introuvable: {mysql_path}")
        
        except PermissionError:
            messagebox.showerror("Erreur de permissions", "Accès refusé. Exécutez l'application en tant qu'administrateur.")
            logger.error(f"[STATION] Accès refusé lors de la suppression de {mysql_path}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression:\n{str(e)}")
            logger.error(f"[STATION] Erreur suppression MySQL: {e}", exc_info=True)
    
    def _create_maintenance_button(self, parent):
        ctk.CTkButton(
            parent, 
            text="🛠️ Maintenance",
            command=self.open_maintenance_window,
            height=35,
            font=("Arial", 13, "bold"),
            fg_color="#1976d2",
            hover_color="#1565c0"
        ).pack(fill="x", pady=(10, 5), padx=5)
    
    def _create_system_config_button(self, parent):
        ctk.CTkButton(
            parent, 
            text="⚙️ Config Auto PC",
            command=self.open_system_config_window,
            height=35,
            font=("Arial", 13, "bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60"
        ).pack(fill="x", pady=(5, 10), padx=5)
    
    def open_maintenance_window(self):
        maint_win = ctk.CTkToplevel(self)
        maint_win.title("Maintenance système")
        maint_win.geometry("900x600")
        maint_win.grab_set()
        
        ctk.CTkLabel(maint_win, text="🛠️ Maintenance système", font=("Arial", 20, "bold")).pack(pady=15)
        
        scrollable = ctk.CTkScrollableFrame(maint_win)
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
        
        uninstall_ids = {}
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
            uninstall_ids[app_name] = id_entry
            
            ctk.CTkButton(
                app_frame,
                text="Désinstaller",
                width=120,
                command=lambda name=app_name, ids=uninstall_ids: self.uninstall_software_station(name, ids)
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
                command=lambda sid=service_id: self.stop_service_station(sid)
            ).pack(side="left", padx=(0, 5))
            
            ctk.CTkButton(
                service_frame,
                text="Désactiver",
                width=100,
                command=lambda sid=service_id: self.disable_service_station(sid)
            ).pack(side="left")
    
    def uninstall_software_station(self, app_name: str, uninstall_ids: dict):
        product_id = uninstall_ids[app_name].get().strip()
        
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
            logger.info(f"[STATION] Tentative de désinstallation de {app_name} (ID: {product_id})")
            
            result = subprocess.run(
                ['msiexec', '/x', product_id, '/qn', '/norestart'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                messagebox.showinfo("Succès", f"{app_name} a été désinstallé avec succès.")
                logger.info(f"✅ [STATION] {app_name} désinstallé avec succès")
            else:
                messagebox.showerror("Erreur", f"Échec de la désinstallation.\n\nCode d'erreur: {result.returncode}\n{result.stderr}")
                logger.error(f"❌ [STATION] Échec désinstallation {app_name}: {result.stderr}")
        
        except subprocess.TimeoutExpired:
            messagebox.showerror("Erreur", "La désinstallation a pris trop de temps (timeout 5min)")
            logger.error(f"[STATION] Timeout désinstallation {app_name}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la désinstallation: {str(e)}")
            logger.error(f"[STATION] Erreur désinstallation {app_name}: {e}", exc_info=True)
    
    def stop_service_station(self, service_name: str):
        try:
            logger.info(f"[STATION] Tentative d'arrêt du service: {service_name}")
            
            result = subprocess.run(
                ['net', 'stop', service_name],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                messagebox.showinfo("Succès", f"Le service '{service_name}' a été arrêté.")
                logger.info(f"✅ [STATION] Service {service_name} arrêté")
            else:
                messagebox.showerror("Erreur", f"Impossible d'arrêter le service.\n\n{result.stderr}")
                logger.error(f"❌ [STATION] Échec arrêt service {service_name}: {result.stderr}")
        
        except subprocess.TimeoutExpired:
            messagebox.showerror("Erreur", "L'arrêt du service a pris trop de temps (timeout 60s)")
            logger.error(f"[STATION] Timeout arrêt service {service_name}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {str(e)}")
            logger.error(f"[STATION] Erreur arrêt service {service_name}: {e}", exc_info=True)
    
    def disable_service_station(self, service_name: str):
        confirm = messagebox.askyesno(
            "Confirmation", 
            f"Êtes-vous sûr de vouloir DÉSACTIVER le service '{service_name}'?\n\nLe service ne démarrera plus automatiquement."
        )
        
        if not confirm:
            return
        
        try:
            logger.info(f"[STATION] Tentative de désactivation du service: {service_name}")
            
            result = subprocess.run(
                ['sc', 'config', service_name, 'start=', 'disabled'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                messagebox.showinfo("Succès", f"Le service '{service_name}' a été désactivé.")
                logger.info(f"✅ [STATION] Service {service_name} désactivé")
            else:
                messagebox.showerror("Erreur", f"Impossible de désactiver le service.\n\n{result.stderr}")
                logger.error(f"❌ [STATION] Échec désactivation service {service_name}: {result.stderr}")
        
        except subprocess.TimeoutExpired:
            messagebox.showerror("Erreur", "La désactivation du service a pris trop de temps (timeout 30s)")
            logger.error(f"[STATION] Timeout désactivation service {service_name}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {str(e)}")
            logger.error(f"[STATION] Erreur désactivation service {service_name}: {e}", exc_info=True)

    def apply_hostname(self):
        new_name = self.hostname_entry.get().strip()
        logger.info(f"[STATION] Tentative de changement de nom: '{new_name}'")
        
        is_valid, message = self.validator.validate_hostname(new_name)
        if not is_valid:
            messagebox.showwarning("Nom invalide", message)
            return
        
        success, result_message = rename_computer_windows(new_name)
        if success:
            messagebox.showinfo("Succès", result_message)
            logger.info(f"[STATION] Nom d'ordinateur changé: {new_name}")
        else:
            messagebox.showerror("Erreur", result_message)
            logger.error(f"[STATION] Échec changement de nom: {result_message}")

    def apply_ip_and_copy(self):
        ip = self.server_entry.get().strip()
        logger.info(f"[STATION] IP récupérée: '{ip}'")
        
        if not ip:
            messagebox.showwarning("Adresse vide", "Veuillez entrer une adresse IP ou un nom de serveur.")
            return
        
        files_to_copy = ["config.xml", "menu.xml", "Floor.xml", "layout.xml"]
        dest_folder = r"C:\pos\xml"
        
        try:
            logger.info(f"📁 Création du dossier de destination: {dest_folder}")
            os.makedirs(dest_folder, exist_ok=True)
            
            successful_copies = 0
            failed_copies = []
            
            for filename in files_to_copy:
                src = f"\\\\{ip}\\xml\\{filename}"
                dst = os.path.join(dest_folder, filename)
                
                try:
                    logger.info(f"📥 Copie de {filename}...")
                    shutil.copy2(src, dst)
                    successful_copies += 1
                    logger.info(f"  ✅ {filename} copié avec succès")
                except FileNotFoundError:
                    failed_copies.append(f"{filename} (fichier introuvable sur le serveur)")
                    logger.warning(f"  ⚠️ {filename} introuvable")
                except PermissionError:
                    failed_copies.append(f"{filename} (accès refusé)")
                    logger.error(f"  ❌ {filename} - accès refusé")
                except Exception as e:
                    failed_copies.append(f"{filename} ({str(e)})")
                    logger.error(f"  ❌ {filename} - erreur: {e}")
            
            if successful_copies > 0:
                logger.info(f"🔧 Mise à jour de la configuration...")
                self._update_config_file(dest_folder, ip)
            
            summary = f"✅ {successful_copies} fichiers copiés avec succès"
            if failed_copies:
                summary += f"\n⚠️ {len(failed_copies)} échecs:\n  - " + "\n  - ".join(failed_copies)
            
            logger.info(f"{summary}")
            
            if successful_copies == len(files_to_copy):
                messagebox.showinfo("Succès complet", "Tous les fichiers ont été copiés et configurés!")
            elif successful_copies > 0:
                messagebox.showwarning(
                    "Succès partiel", 
                    f"{successful_copies}/{len(files_to_copy)} fichiers copiés.\n\n"
                    f"Fichiers échoués:\n" + "\n".join(failed_copies)
                )
            else:
                messagebox.showerror(
                    "Échec", 
                    "Aucun fichier n'a pu être copié.\n\n"
                    "Vérifiez que:\n"
                    "1. Le serveur est accessible\n"
                    "2. Le partage \\xml existe\n"
                    "3. Vous avez les permissions nécessaires"
                )
        
        except Exception as e:
            error_msg = f"Erreur lors de la copie: {str(e)}"
            logger.error(error_msg, exc_info=True)
            messagebox.showerror("Erreur", error_msg)

    def _update_config_file(self, dest_folder: str, server_ip: str):
        config_path = os.path.join(dest_folder, "config.xml")
        
        if not os.path.exists(config_path):
            logger.warning("  ⚠️ config.xml introuvable - pas de mise à jour")
            return
        
        try:
            tree = ET.parse(config_path)
            root = tree.getroot()
            
            updated = False
            
            server_elem = root.find("Server")
            if server_elem is not None:
                server_elem.text = server_ip
                updated = True
                logger.info(f"  ✅ Adresse serveur mise à jour: {server_ip}")
            
            database_elem = root.find("Database")
            if database_elem is not None:
                database_elem.text = server_ip
                updated = True
                logger.info(f"  ✅ Adresse base de données mise à jour: {server_ip}")
            
            font_size = self.config_data.get("GUI_Font_Size")
            if font_size:
                font_elem = root.find("GUI_Font_Size")
                if font_elem is not None:
                    font_elem.text = font_size
                    updated = True
                    logger.info(f"  ✅ Taille de police mise à jour: {font_size}")
            
            list_height = self.config_data.get("GUI_List_Height")
            if list_height:
                height_elem = root.find("GUI_List_Height")
                if height_elem is not None:
                    height_elem.text = list_height
                    updated = True
                    logger.info(f"  ✅ Hauteur de liste mise à jour: {list_height}")
            
            if updated:
                tree.write(config_path, encoding="utf-8", xml_declaration=True)
                logger.info("  💾 config.xml sauvegardé")
            else:
                logger.warning("  ⚠️ Aucun élément Server/Database trouvé dans config.xml")
        
        except ET.ParseError as e:
            logger.error(f"  ❌ Erreur de lecture XML: {e}")
        except Exception as e:
            logger.error(f"  ❌ Erreur lors de la mise à jour: {e}")
    
    def open_system_config_window(self):
        config_win = ctk.CTkToplevel(self)
        config_win.title("Configuration Auto PC")
        config_win.geometry("900x700")
        config_win.grab_set()
        
        ctk.CTkLabel(config_win, text="⚙️ Configuration Auto PC", font=("Arial", 20, "bold")).pack(pady=15)
        
        scrollable = ctk.CTkScrollableFrame(config_win)
        scrollable.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        container = ctk.CTkFrame(scrollable, fg_color="transparent")
        container.pack(fill="both", expand=True)
        
        system_config_vars = {}
        
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
            system_config_vars[key] = var
        
        for key, label in options_right:
            var = ctk.BooleanVar()
            cb = ctk.CTkCheckBox(right_col, text=label, variable=var)
            cb.pack(anchor="w", pady=5)
            system_config_vars[key] = var
        
        password_share_frame = ctk.CTkFrame(right_col)
        password_share_frame.pack(anchor="w", pady=10, fill="x")
        
        system_config_vars['enable_password_sharing_config'] = ctk.BooleanVar()
        ctk.CTkCheckBox(password_share_frame, text="Partage protégé par mot de passe:", 
                       variable=system_config_vars['enable_password_sharing_config']).pack(anchor="w")
        
        system_config_vars['password_sharing_action'] = ctk.StringVar(value="Désactiver protection")
        action_menu = ctk.CTkComboBox(password_share_frame, 
                                     values=["Activer protection", "Désactiver protection"],
                                     variable=system_config_vars['password_sharing_action'],
                                     width=200)
        action_menu.pack(anchor="w", padx=20, pady=5)
        
        active_hours_frame = ctk.CTkFrame(right_col)
        active_hours_frame.pack(anchor="w", pady=10, fill="x")
        
        system_config_vars['active_hours'] = ctk.BooleanVar()
        ctk.CTkCheckBox(active_hours_frame, text="Heures actives (pas de redémarrage auto):", 
                       variable=system_config_vars['active_hours']).pack(anchor="w")
        
        hours_selector = ctk.CTkFrame(active_hours_frame, fg_color="transparent")
        hours_selector.pack(anchor="w", padx=20, pady=5)
        
        current_start, current_end = system_config.get_active_hours()
        
        ctk.CTkLabel(hours_selector, text="De:").pack(side="left")
        system_config_vars['active_hours_start'] = ctk.StringVar(value=current_start)
        ctk.CTkEntry(hours_selector, textvariable=system_config_vars['active_hours_start'], width=50).pack(side="left", padx=5)
        ctk.CTkLabel(hours_selector, text="h à:").pack(side="left")
        system_config_vars['active_hours_end'] = ctk.StringVar(value=current_end)
        ctk.CTkEntry(hours_selector, textvariable=system_config_vars['active_hours_end'], width=50).pack(side="left", padx=5)
        ctk.CTkLabel(hours_selector, text="h").pack(side="left")
        
        def execute_config():
            log_window = ctk.CTkToplevel(config_win)
            log_window.title("Exécution de la configuration")
            log_window.geometry("700x500")
            log_window.transient(config_win)
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
                    if system_config_vars['taskbar'].get():
                        steps.append(("Tweak barre des tâches", lambda: system_config.tweak_taskbar(log_msg)))
                    if system_config_vars['notifications'].get():
                        steps.append(("Désactivation notifications", lambda: system_config.disable_windows_notifications(log_msg)))
                    if system_config_vars['disable_uac'].get():
                        steps.append(("Désactivation UAC", lambda: system_config.disable_uac(log_msg)))
                    if system_config_vars['disable_network_sleep'].get():
                        steps.append(("Désactivation veille réseau", lambda: system_config.disable_network_sleep(log_msg)))
                    if system_config_vars['network_private'].get():
                        steps.append(("Carte réseau en mode Privé", lambda: system_config.set_network_private(log_msg)))
                    if system_config_vars['timezone_sync'].get():
                        steps.append(("Fuseau horaire + sync", lambda: system_config.set_timezone_and_sync(log_msg)))
                    if system_config_vars['best_performance'].get():
                        steps.append(("Meilleures performances", lambda: system_config.set_best_performance(log_msg)))
                    if system_config_vars['power_options'].get():
                        steps.append(("Mode alimentation performance", lambda: system_config.set_power_performance(log_msg)))
                    
                    if system_config_vars['enable_password_sharing_config'].get():
                        pw_action = system_config_vars['password_sharing_action'].get()
                        if pw_action == "Activer protection":
                            steps.append(("Activation partage protégé", lambda: system_config.enable_password_protected_sharing(log_msg)))
                        elif pw_action == "Désactiver protection":
                            steps.append(("Désactivation partage protégé", lambda: system_config.disable_password_protected_sharing(log_msg)))
                    
                    if system_config_vars['active_hours'].get():
                        start_h = system_config_vars['active_hours_start'].get()
                        end_h = system_config_vars['active_hours_end'].get()
                        steps.append(("Configuration heures actives", 
                                     lambda sh=start_h, eh=end_h: system_config.set_active_hours(log_msg, sh, eh)))
                    
                    if system_config_vars['restore_context_menu'].get():
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
        
        execute_btn = ctk.CTkButton(container, text="▶ Exécuter la configuration",
                                   command=execute_config,
                                   font=("Arial", 14, "bold"),
                                   height=40,
                                   fg_color="#2ecc71",
                                   hover_color="#27ae60")
        execute_btn.pack(pady=20)
    
    def on_closing(self):
        logger.info("Fermeture de l'application station")
        self.destroy()
        sys.exit(0)


if __name__ == "__main__":
    try:
        app = StationApp()
        app.mainloop()
    except Exception as e:
        logger.critical(f"Erreur fatale : {e}", exc_info=True)
        raise
    finally:
        sys.exit(0)
