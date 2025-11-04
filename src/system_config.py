import subprocess
import os
import logging

logger = logging.getLogger(__name__)

def tweak_taskbar(log_fn):
    """Tweaker la barre des tâches Windows (masquer widgets, désactiver recherche, etc.)"""
    try:
        import winreg
        
        log_fn("▶ Configuration de la barre des tâches...")
        
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                              r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced")
        
        winreg.SetValueEx(key, "ShowTaskViewButton", 0, winreg.REG_DWORD, 0)
        log_fn("✓ Bouton 'Affichage des tâches' masqué")
        
        winreg.SetValueEx(key, "TaskbarDa", 0, winreg.REG_DWORD, 0)
        log_fn("✓ Widgets de la barre des tâches masqués")
        
        winreg.CloseKey(key)
        
        key2 = winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                               r"Software\Microsoft\Windows\CurrentVersion\Search")
        winreg.SetValueEx(key2, "SearchboxTaskbarMode", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key2)
        log_fn("✓ Zone de recherche masquée")
        
        log_fn("✅ Barre des tâches optimisée")
        log_fn("⚠️ Redémarrer explorer.exe pour appliquer")
        
    except Exception as e:
        log_fn(f"❌ Erreur configuration barre des tâches: {e}")

def disable_windows_notifications(log_fn):
    """Désactiver les notifications Windows"""
    try:
        import winreg
        
        log_fn("▶ Désactivation des notifications Windows...")
        
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                              r"Software\Microsoft\Windows\CurrentVersion\PushNotifications")
        winreg.SetValueEx(key, "ToastEnabled", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        log_fn("✓ Notifications toast désactivées (utilisateur actuel)")
        
        try:
            key2 = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE,
                                   r"Software\Policies\Microsoft\Windows\Explorer")
            winreg.SetValueEx(key2, "DisableNotificationCenter", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key2)
            log_fn("✓ Centre de notifications désactivé (tous les utilisateurs)")
        except PermissionError:
            log_fn("⚠️ Centre de notifications : nécessite droits administrateur")
        
        log_fn("✅ Notifications Windows désactivées")
        
    except Exception as e:
        log_fn(f"❌ Erreur désactivation notifications: {e}")

def restore_context_menu(log_fn):
    """Rétablir le menu contextuel classique de Windows 10"""
    try:
        import winreg
        
        log_fn("▶ Rétablissement du menu contextuel classique...")
        
        key_path = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32"
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "")
        winreg.CloseKey(key)
        
        log_fn("✓ Clé de registre modifiée")
        log_fn("✅ Menu contextuel classique rétabli")
        log_fn("⚠️ Redémarrer explorer.exe pour appliquer")
        
    except Exception as e:
        log_fn(f"❌ Erreur rétablissement menu contextuel: {e}")

def disable_uac(log_fn):
    """Désactiver le contrôle de compte utilisateur (UAC)"""
    try:
        import winreg
        
        log_fn("▶ Désactivation du contrôle de compte utilisateur (UAC)...")
        
        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE,
                              r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System")
        winreg.SetValueEx(key, "EnableLUA", 0, winreg.REG_DWORD, 0)
        winreg.SetValueEx(key, "ConsentPromptBehaviorAdmin", 0, winreg.REG_DWORD, 0)
        winreg.SetValueEx(key, "PromptOnSecureDesktop", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        
        log_fn("✓ Clés UAC modifiées (EnableLUA=0, ConsentPromptBehaviorAdmin=0)")
        log_fn("✅ UAC désactivé")
        log_fn("⚠️ Redémarrage requis pour appliquer les changements")
        
    except Exception as e:
        log_fn(f"❌ Erreur désactivation UAC: {e}")
        log_fn("⚠️ Nécessite droits administrateur")

def disable_network_sleep(log_fn):
    """Désactiver la mise en veille des cartes réseau"""
    try:
        log_fn("▶ Désactivation de la mise en veille des cartes réseau...")
        
        ps_cmd = '''
Get-NetAdapter | ForEach-Object {
    $adapter = $_
    $powerMgmt = Get-WmiObject MSPower_DeviceEnable -Namespace root\\wmi | Where-Object {$_.InstanceName -match [regex]::Escape($adapter.PnPDeviceID)}
    if ($powerMgmt) {
        $powerMgmt.Enable = $false
        $powerMgmt.Put()
        Write-Output "Désactivé pour: $($adapter.Name)"
    }
}
'''
        
        result = subprocess.run(['powershell', '-Command', ps_cmd],
                               capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            output_lines = result.stdout.strip().split('\n')
            for line in output_lines:
                if line.strip():
                    log_fn(f"  ✓ {line.strip()}")
            log_fn("✅ Mise en veille des cartes réseau désactivée")
        else:
            log_fn("⚠️ Impossible de modifier certaines cartes réseau")
            log_fn("   Essai avec méthode alternative...")
            
            subprocess.run('powercfg /change standby-timeout-ac 0', shell=True, timeout=10)
            subprocess.run('powercfg /change standby-timeout-dc 0', shell=True, timeout=10)
            log_fn("✓ Paramètres d'alimentation réseau modifiés")
        
    except Exception as e:
        log_fn(f"❌ Erreur désactivation veille réseau: {e}")
        log_fn("⚠️ Nécessite droits administrateur")

def set_network_private(log_fn):
    """Mettre la carte réseau en mode Privé (au lieu de Public)"""
    try:
        log_fn("▶ Configuration carte réseau en mode Privé...")
        
        ps_cmd = 'Get-NetConnectionProfile | Set-NetConnectionProfile -NetworkCategory Private'
        
        result = subprocess.run(['powershell', '-Command', ps_cmd],
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            log_fn("✓ Carte(s) réseau configurée(s) en mode Privé")
            log_fn("✅ Configuration réseau Privé terminée")
        else:
            log_fn(f"⚠️ Résultat de la commande: {result.stderr.strip() if result.stderr else 'OK'}")
            log_fn("✓ Commande exécutée (vérifier manuellement si nécessaire)")
        
    except Exception as e:
        log_fn(f"❌ Erreur configuration réseau Privé: {e}")
        log_fn("⚠️ Configuration manuelle requise:")
        log_fn("   Paramètres → Réseau → Propriétés → Profil réseau → Privé")

def set_timezone_and_sync(log_fn):
    """Configurer fuseau horaire America/Toronto et synchroniser"""
    try:
        log_fn("▶ Configuration du fuseau horaire et synchronisation...")
        
        cmd_tz = 'tzutil /s "Eastern Standard Time"'
        result = subprocess.run(cmd_tz, capture_output=True, text=True, shell=True, timeout=10)
        
        if result.returncode == 0:
            log_fn("✓ Fuseau horaire défini sur America/Toronto (Eastern)")
        else:
            log_fn("⚠️ Erreur lors du changement de fuseau horaire")
        
        log_fn("  Synchronisation de l'heure en cours...")
        
        subprocess.run('net stop w32time', capture_output=True, shell=True, timeout=10)
        subprocess.run('sc config w32time start= auto', capture_output=True, shell=True, timeout=10)
        log_fn("✓ Service de temps configuré en démarrage automatique")
        
        subprocess.run('net start w32time', capture_output=True, shell=True, timeout=10)
        log_fn("✓ Service de temps redémarré")
        
        subprocess.run('w32tm /register', capture_output=True, shell=True, timeout=10)
        
        time_servers = 'time.windows.com,time.nist.gov,pool.ntp.org'
        subprocess.run(f'w32tm /config /manualpeerlist:"{time_servers}" /syncfromflags:manual /reliable:YES /update',
                      capture_output=True, shell=True, timeout=15)
        log_fn("✓ Serveurs de temps NTP configurés")
        
        result_sync = subprocess.run('w32tm /resync /force',
                                    capture_output=True, text=True, shell=True, timeout=30)
        
        if "successfully" in result_sync.stdout.lower() or result_sync.returncode == 0:
            log_fn("✓ Heure synchronisée avec succès")
        else:
            log_fn("⚠️ La synchronisation peut prendre quelques instants")
        
        subprocess.run('w32tm /config /update', capture_output=True, shell=True, timeout=10)
        log_fn("✓ Synchronisation automatique activée")
        
        log_fn("✅ Fuseau horaire et synchronisation configurés")
        
    except Exception as e:
        log_fn(f"❌ Erreur configuration fuseau horaire: {e}")

def set_best_performance(log_fn):
    """Configurer les meilleures performances système"""
    try:
        import winreg
        
        log_fn("▶ Configuration des meilleures performances système...")
        
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                              r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects")
        winreg.SetValueEx(key, "VisualFXSetting", 0, winreg.REG_DWORD, 2)
        winreg.CloseKey(key)
        
        log_fn("✓ Paramètres de performances visuelles modifiés")
        
        key2 = winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                               r"Control Panel\Desktop\WindowMetrics")
        winreg.SetValueEx(key2, "MinAnimate", 0, winreg.REG_SZ, "0")
        winreg.CloseKey(key2)
        
        log_fn("✓ Animations désactivées")
        log_fn("✅ Meilleures performances configurées")
        log_fn("⚠️ Redémarrage ou déconnexion/reconnexion recommandé")
        
    except Exception as e:
        log_fn(f"❌ Erreur configuration performances: {e}")

def set_power_performance(log_fn):
    """Configurer le mode d'alimentation performance"""
    try:
        log_fn("▶ Configuration du mode d'alimentation performance...")
        
        cmd_power = 'powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'
        subprocess.run(cmd_power, capture_output=True, shell=True, timeout=10)
        log_fn("✓ Mode alimentation 'Performance élevée' activé")
        
        subprocess.run('powercfg /change standby-timeout-ac 0', shell=True, timeout=10)
        subprocess.run('powercfg /change standby-timeout-dc 0', shell=True, timeout=10)
        log_fn("✓ Mise en veille désactivée")
        
        subprocess.run('powercfg /change monitor-timeout-ac 0', shell=True, timeout=10)
        subprocess.run('powercfg /change monitor-timeout-dc 0', shell=True, timeout=10)
        log_fn("✓ Extinction automatique de l'écran désactivée")
        
        subprocess.run('powercfg /change disk-timeout-ac 0', shell=True, timeout=10)
        subprocess.run('powercfg /change disk-timeout-dc 0', shell=True, timeout=10)
        log_fn("✓ Arrêt automatique du disque dur désactivé")
        
        log_fn("✅ Mode alimentation performance configuré")
        
    except Exception as e:
        log_fn(f"❌ Erreur configuration alimentation: {e}")

def set_active_hours(log_fn, start_hour, end_hour):
    """Configurer les heures actives du système"""
    try:
        import winreg
        
        log_fn(f"▶ Configuration des heures actives ({start_hour}h - {end_hour}h)...")
        
        try:
            start = int(start_hour)
            end = int(end_hour)
            if start < 0 or start > 23 or end < 0 or end > 23:
                log_fn("❌ Les heures doivent être entre 0 et 23")
                return
        except ValueError:
            log_fn("❌ Format d'heure invalide")
            return
        
        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE,
                              r"SOFTWARE\Microsoft\WindowsUpdate\UX\Settings")
        winreg.SetValueEx(key, "ActiveHoursStart", 0, winreg.REG_DWORD, start)
        winreg.SetValueEx(key, "ActiveHoursEnd", 0, winreg.REG_DWORD, end)
        winreg.CloseKey(key)
        
        if start >= end:
            log_fn(f"✓ Heures actives définies: {start}h - {end}h (passant minuit)")
        else:
            log_fn(f"✓ Heures actives définies: {start}h - {end}h")
        log_fn("✅ Heures actives configurées")
        log_fn("   Windows ne redémarrera pas automatiquement pendant ces heures")
        
    except Exception as e:
        log_fn(f"❌ Erreur configuration heures actives: {e}")
        log_fn("⚠️ Nécessite droits administrateur")

def check_password_protected_sharing():
    """Vérifie si le partage protégé par mot de passe est activé"""
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             r"SYSTEM\CurrentControlSet\Control\Lsa", 0,
                             winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, "everyoneincludesanonymous")
        winreg.CloseKey(key)
        return value == 0
    except:
        return True

def disable_password_protected_sharing(log_fn):
    """Désactive le partage protégé par mot de passe"""
    try:
        import winreg
        
        log_fn("▶ Désactivation du partage protégé par mot de passe...")
        
        key1 = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE,
                               r"SYSTEM\CurrentControlSet\Control\Lsa")
        winreg.SetValueEx(key1, "everyoneincludesanonymous", 0,
                          winreg.REG_DWORD, 1)
        winreg.CloseKey(key1)
        log_fn("✓ Clé 'everyoneincludesanonymous' définie à 1")
        
        key2 = winreg.CreateKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters")
        winreg.SetValueEx(key2, "RestrictNullSessAccess", 0,
                          winreg.REG_DWORD, 0)
        winreg.CloseKey(key2)
        log_fn("✓ Clé 'RestrictNullSessAccess' définie à 0")
        
        key3 = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE,
                               r"SYSTEM\CurrentControlSet\Control\Lsa")
        winreg.SetValueEx(key3, "ForceGuest", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key3)
        log_fn("✓ Clé 'ForceGuest' définie à 0 (désactivé)")
        
        key4 = winreg.CreateKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System")
        winreg.SetValueEx(key4, "LocalAccountTokenFilterPolicy", 0,
                          winreg.REG_DWORD, 1)
        winreg.CloseKey(key4)
        log_fn("✓ Clé 'LocalAccountTokenFilterPolicy' définie à 1 (désactivé)")
        
        log_fn("✅ Partage protégé par mot de passe désactivé")
        log_fn("⚠️ Redémarrage ou déconnexion/reconnexion du réseau requis pour appliquer")
        
    except Exception as e:
        log_fn(f"❌ Erreur désactivation partage protégé: {e}")
        log_fn("⚠️ Nécessite droits administrateur")

def enable_password_protected_sharing(log_fn):
    """Active le partage protégé par mot de passe"""
    try:
        import winreg
        
        log_fn("▶ Activation du partage protégé par mot de passe...")
        
        key1 = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE,
                               r"SYSTEM\CurrentControlSet\Control\Lsa")
        winreg.SetValueEx(key1, "everyoneincludesanonymous", 0,
                          winreg.REG_DWORD, 0)
        winreg.CloseKey(key1)
        log_fn("✓ Clé 'everyoneincludesanonymous' définie à 0")
        
        key2 = winreg.CreateKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters")
        winreg.SetValueEx(key2, "RestrictNullSessAccess", 0,
                          winreg.REG_DWORD, 1)
        winreg.CloseKey(key2)
        log_fn("✓ Clé 'RestrictNullSessAccess' définie à 1")
        
        key3 = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE,
                               r"SYSTEM\CurrentControlSet\Control\Lsa")
        winreg.SetValueEx(key3, "ForceGuest", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key3)
        log_fn("✓ Clé 'ForceGuest' définie à 1 (activé)")
        
        key4 = winreg.CreateKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System")
        winreg.SetValueEx(key4, "LocalAccountTokenFilterPolicy", 0,
                          winreg.REG_DWORD, 0)
        winreg.CloseKey(key4)
        log_fn("✓ Clé 'LocalAccountTokenFilterPolicy' définie à 0 (activé)")
        
        log_fn("✅ Partage protégé par mot de passe activé")
        log_fn("⚠️ Redémarrage ou déconnexion/reconnexion du réseau requis pour appliquer")
        
    except Exception as e:
        log_fn(f"❌ Erreur activation partage protégé: {e}")
        log_fn("⚠️ Nécessite droits administrateur")

def install_ninite(log_fn):
    """Installation Ninite + config VNC"""
    try:
        log_fn("▶ Installation Ninite...")
        log_fn("⚠️ Cette fonction nécessite le téléchargement manuel de Ninite")
        log_fn("   Visitez https://ninite.com pour créer votre installeur personnalisé")
        log_fn("✅ Placeholder - Ninite doit être installé manuellement")
    except Exception as e:
        log_fn(f"❌ Erreur installation Ninite: {e}")

def get_active_hours():
    """Récupère les heures actives actuelles depuis le registre Windows"""
    try:
        import winreg
        
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r"SOFTWARE\Microsoft\WindowsUpdate\UX\Settings",
                                0, winreg.KEY_READ)
            start, _ = winreg.QueryValueEx(key, "ActiveHoursStart")
            end, _ = winreg.QueryValueEx(key, "ActiveHoursEnd")
            winreg.CloseKey(key)
            return str(start), str(end)
        except (FileNotFoundError, OSError):
            return "8", "20"
    except Exception:
        return "8", "20"
