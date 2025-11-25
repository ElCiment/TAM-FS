#!/usr/bin/env python3
import customtkinter as ctk
import sys
import os
import urllib.request
import threading
import subprocess
from tkinter import messagebox
from PIL import Image, ImageTk


def resource_path(relative_path):
    """Retourne le chemin absolu vers une ressource, que l'application soit executee
    depuis Python ou depuis un exe PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)


def get_real_executable_path():
    """Retourne le vrai chemin de l'executable (pas le dossier temporaire PyInstaller)"""
    if getattr(sys, 'frozen', False):
        return os.path.abspath(sys.argv[0])
    else:
        return os.path.abspath(__file__)


def get_app_dir():
    """Retourne le repertoire de l'executable ou du script"""
    return os.path.dirname(get_real_executable_path())


def get_config_file_path(filename):
    """Cherche un fichier de configuration d'abord dans le repertoire de l'exe, puis dans les ressources"""
    app_dir_path = os.path.join(get_app_dir(), filename)
    if os.path.exists(app_dir_path):
        return app_dir_path
    return resource_path(filename)


def get_local_version():
    """Lit le numero de version depuis versions.txt"""
    try:
        version_path = get_config_file_path("versions.txt")
        with open(version_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception:
        return "0.0.0"


def get_download_config():
    """Lit la configuration de telechargement depuis download.txt"""
    config = {
        'actual_version_url': '',
        'download_url': ''
    }
    try:
        download_path = get_config_file_path("download.txt")
        with open(download_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    except Exception:
        pass
    return config


def get_remote_version(url):
    """Recupere le numero de version depuis l'URL distante"""
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.read().decode('utf-8').strip()
    except Exception:
        return None


def compare_versions(local, remote):
    """Compare deux numeros de version. Retourne True si remote > local"""
    try:
        local_parts = [int(x) for x in local.split('.')]
        remote_parts = [int(x) for x in remote.split('.')]
        
        for i in range(max(len(local_parts), len(remote_parts))):
            l = local_parts[i] if i < len(local_parts) else 0
            r = remote_parts[i] if i < len(remote_parts) else 0
            if r > l:
                return True
            elif r < l:
                return False
        return False
    except Exception:
        return False


class UpdateDownloader:
    """Classe pour gerer le telechargement avec progression"""
    
    def __init__(self, url, dest_path, progress_callback=None, complete_callback=None):
        self.url = url
        self.dest_path = dest_path
        self.progress_callback = progress_callback
        self.complete_callback = complete_callback
        self.cancelled = False
    
    def download(self):
        """Telecharge le fichier avec suivi de progression"""
        try:
            with urllib.request.urlopen(self.url, timeout=30) as response:
                total_size = int(response.headers.get('Content-Length', 0))
                downloaded = 0
                block_size = 8192
                
                with open(self.dest_path, 'wb') as f:
                    while not self.cancelled:
                        buffer = response.read(block_size)
                        if not buffer:
                            break
                        f.write(buffer)
                        downloaded += len(buffer)
                        
                        if self.progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            self.progress_callback(progress, downloaded, total_size)
                
                if self.cancelled:
                    if os.path.exists(self.dest_path):
                        os.remove(self.dest_path)
                    return False
                
                if self.complete_callback:
                    self.complete_callback(True)
                return True
                
        except Exception as e:
            if self.complete_callback:
                self.complete_callback(False, str(e))
            return False
    
    def cancel(self):
        self.cancelled = True


class UpdateDialog(ctk.CTkToplevel):
    """Fenetre de dialogue pour la mise a jour"""
    
    def __init__(self, parent, local_version, remote_version, download_url):
        super().__init__(parent)
        
        self.title("Mise a jour disponible")
        self.geometry("400x200")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.download_url = download_url
        self.downloader = None
        self.result = False
        
        ctk.CTkLabel(
            self,
            text="Nouvelle version disponible !",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=15)
        
        ctk.CTkLabel(
            self,
            text=f"Version actuelle : {local_version}\nNouvelle version : {remote_version}",
            font=ctk.CTkFont(size=12)
        ).pack(pady=5)
        
        ctk.CTkLabel(
            self,
            text="Voulez-vous telecharger la mise a jour ?",
            font=ctk.CTkFont(size=12)
        ).pack(pady=10)
        
        self.progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=300)
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="", font=ctk.CTkFont(size=10))
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)
        
        self.yes_btn = ctk.CTkButton(
            btn_frame,
            text="Oui",
            width=100,
            command=self.start_download
        )
        self.yes_btn.pack(side="left", padx=10)
        
        self.no_btn = ctk.CTkButton(
            btn_frame,
            text="Non",
            width=100,
            fg_color="gray",
            command=self.cancel
        )
        self.no_btn.pack(side="left", padx=10)
        
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        
        self.center_window(parent)
    
    def center_window(self, parent):
        """Centre la fenetre par rapport au parent"""
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
    
    def start_download(self):
        """Demarre le telechargement"""
        self.yes_btn.configure(state="disabled")
        self.no_btn.configure(text="Annuler", command=self.cancel_download)
        
        self.progress_frame.pack(pady=5)
        self.progress_bar.pack()
        self.progress_bar.set(0)
        self.progress_label.pack()
        
        import tempfile
        temp_dir = tempfile.gettempdir()
        self.new_exe_path = os.path.join(temp_dir, "Tamio_Config_update.exe")
        self.original_exe_path = get_real_executable_path()
        
        self.downloader = UpdateDownloader(
            self.download_url,
            self.new_exe_path,
            progress_callback=self.update_progress,
            complete_callback=self.download_complete
        )
        
        thread = threading.Thread(target=self.downloader.download, daemon=True)
        thread.start()
    
    def update_progress(self, percent, downloaded, total):
        """Met a jour la barre de progression"""
        def update():
            self.progress_bar.set(percent / 100)
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total / (1024 * 1024)
            self.progress_label.configure(text=f"{mb_downloaded:.1f} Mo / {mb_total:.1f} Mo ({percent:.0f}%)")
        self.after(0, update)
    
    def download_complete(self, success, error=None):
        """Callback quand le telechargement est termine"""
        def complete():
            if success:
                self.result = True
                self.execute_update()
            else:
                messagebox.showerror("Erreur", f"Echec du telechargement :\n{error if error else 'Erreur inconnue'}")
                self.destroy()
        self.after(0, complete)
    
    def execute_update(self):
        """Execute la mise a jour via un script cache dans TEMP"""
        try:
            if not getattr(sys, 'frozen', False):
                messagebox.showinfo("Info", "Mise a jour telechargee.\nEn mode developpement, le remplacement automatique n'est pas disponible.")
                self.destroy()
                return
            
            import tempfile
            temp_dir = tempfile.gettempdir()
            batch_path = os.path.join(temp_dir, "_tamio_updater.bat")
            
            original_exe = self.original_exe_path
            new_exe = self.new_exe_path
            exe_name = os.path.basename(original_exe)
            exe_dir = os.path.dirname(original_exe)
            
            batch_content = f'''@echo off
echo Mise a jour en cours...
start "" "{new_exe}"
timeout /t 5 /nobreak >nul
taskkill /F /IM "{exe_name}" >nul 2>&1
:waitloop
tasklist /FI "IMAGENAME eq {exe_name}" 2>NUL | find /I "{exe_name}" >nul
if "%ERRORLEVEL%"=="0" (
    timeout /t 1 /nobreak >nul
    goto waitloop
)
copy /Y "{new_exe}" "{original_exe}" >nul
del "{new_exe}" >nul 2>&1
del /F /Q "%~f0"
'''
            
            with open(batch_path, 'w', encoding='utf-8') as f:
                f.write(batch_content)
            
            subprocess.Popen(batch_path, shell=True)
            
            self.destroy()
            self.master.destroy()
            sys.exit(0)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la mise a jour :\n{e}")
            self.destroy()
    
    def cancel_download(self):
        """Annule le telechargement en cours"""
        if self.downloader:
            self.downloader.cancel()
        self.destroy()
    
    def cancel(self):
        """Ferme le dialogue sans telecharger"""
        self.result = False
        self.destroy()


class TamioFSLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Tamio Config")
        self.geometry("500x360")
        self.resizable(False, False)
        
        ico_path = resource_path("tamio.ico")
        try:
            self.iconbitmap(ico_path)
        except Exception as e:
            print(f"Impossible de charger l'icone : {e}")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.local_version = get_local_version()
        
        self.create_widgets()
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.after(500, self.check_for_updates)

    def create_widgets(self):
        
        try:
            logo_path = resource_path("tamio.ico")
            img = Image.open(logo_path)
            img = img.resize((85, 85), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            logo_label = ctk.CTkLabel(self, image=photo, text="")
            logo_label.image = photo
            logo_label.pack(pady=5)
        except Exception as e:
            print(f"Impossible de charger le logo : {e}")
        
        version_label = ctk.CTkLabel(
            self,
            text=f"v{self.local_version}",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        version_label.pack(pady=(0, 5))
        
        server_button = ctk.CTkButton(
            self,
            text="SETUP SERVEUR",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            width=300,
            command=self.launch_server
        )
        server_button.pack(pady=5)
        
        station_button = ctk.CTkButton(
            self,
            text="SETUP STATION",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            width=300,
            command=self.launch_station
        )
        station_button.pack(pady=5)
        
        separator = ctk.CTkFrame(self, height=2, fg_color="gray")
        separator.pack(fill="x", pady=(10, 5))
        
        bottom_frame = ctk.CTkFrame(self, fg_color=None)
        bottom_frame.pack(pady=10)
        
        convert_button = ctk.CTkButton(
            bottom_frame,
            text="Convertir EXML",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#c6860d",
            hover_color="#e0b90d",
            height=50,
            width=145,
            command=self.convert_exml
        )
        convert_button.pack(side="left", padx=5)
        
        flush_button = ctk.CTkButton(
            bottom_frame,
            text="Remise a 0",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#c6860d",
            hover_color="#e0b90d",
            height=50,
            width=145,
            command=self.run_flush
        )
        flush_button.pack(side="left", padx=5)

    def check_for_updates(self):
        """Verifie si une mise a jour est disponible"""
        def check():
            config = get_download_config()
            if not config['actual_version_url'] or not config['download_url']:
                return
            
            remote_version = get_remote_version(config['actual_version_url'])
            if remote_version and compare_versions(self.local_version, remote_version):
                self.after(0, lambda: self.show_update_dialog(remote_version, config['download_url']))
        
        thread = threading.Thread(target=check, daemon=True)
        thread.start()
    
    def show_update_dialog(self, remote_version, download_url):
        """Affiche le dialogue de mise a jour"""
        UpdateDialog(self, self.local_version, remote_version, download_url)

    def convert_exml(self):
        import tempfile
        import shutil
        import subprocess
        import psutil
        from tkinter import filedialog, messagebox
        import time
        import os

        try:
            exml_path = filedialog.askopenfilename(
                title="Selectionner le fichier EXML a convertir",
                filetypes=[("EXML files", "*.exml"), ("All files", "*.*")]
            )
            if not exml_path:
                return

            temp_dir = tempfile.mkdtemp()

            exe_path = resource_path("xml_extractor.exe")
            if not os.path.exists(exe_path):
                messagebox.showerror("Erreur", "Impossible de trouver xml_extractor.exe")
                return

            shutil.copy(exe_path, temp_dir)

            temp_exml = os.path.join(temp_dir, "menu_local.exml")
            shutil.copy(exml_path, temp_exml)

            if os.name == "nt":
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                si.wShowWindow = 2
            else:
                si = None

            proc = subprocess.Popen(
                [os.path.join(temp_dir, "xml_extractor.exe")],
                cwd=temp_dir,
                startupinfo=si
            )

            xml_output = filedialog.asksaveasfilename(
                title="Enregistrer le fichier XML converti",
                defaultextension=".xml",
                initialfile="menu_local.xml",
                filetypes=[("XML files", "*.xml")]
            )
            if not xml_output:
                if proc.poll() is None:
                    try:
                        proc.terminate()
                        proc.wait(timeout=2)
                    except Exception:
                        try:
                            proc.kill()
                        except Exception:
                            pass
                shutil.rmtree(temp_dir, ignore_errors=True)
                return

            temp_xml = os.path.join(temp_dir, "menu_local.xml")
            timeout = 5
            waited = 0
            while not os.path.exists(temp_xml) and waited < timeout:
                time.sleep(0.2)
                waited += 0.2

            if os.path.exists(temp_xml):
                shutil.copy(temp_xml, xml_output)
                messagebox.showinfo("Succes", f"Fichier XML enregistre ici:\n{xml_output}")
            else:
                messagebox.showerror("Erreur", "Le fichier XML n'a pas ete genere a temps.")

            if proc.poll() is None:
                try:
                    proc.terminate()
                    proc.wait(timeout=2)
                except Exception:
                    try:
                        proc.kill()
                    except Exception:
                        pass

            shutil.rmtree(temp_dir, ignore_errors=True)

        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue:\n{e}")
            import traceback
            traceback.print_exc()

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

    def run_flush(self):
        import subprocess
        import os
        from tkinter import messagebox

        try:
            exe_path = resource_path("flush.exe")

            if not os.path.exists(exe_path):
                messagebox.showerror("Erreur", "Impossible de trouver flush.exe")
                return

            subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path))

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de lancer flush.exe:\n{e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    app = TamioFSLauncher()
    app.mainloop()
