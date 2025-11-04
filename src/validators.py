import re
import socket
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class DataValidator:
    @staticmethod
    def validate_ip_address(ip: str) -> Tuple[bool, str]:
        ip = ip.strip()
        if not ip:
            return False, "L'adresse IP ne peut pas être vide"
        
        pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
        match = re.match(pattern, ip)
        
        if not match:
            return False, "Format d'adresse IP invalide"
        
        for octet in match.groups():
            if int(octet) > 255:
                return False, "Les octets doivent être entre 0 et 255"
        
        return True, "Adresse IP valide"

    @staticmethod
    def validate_postal_code(postal_code: str) -> Tuple[bool, str]:
        postal_code = postal_code.strip().upper().replace(" ", "")
        
        pattern = r'^[A-Z]\d[A-Z]\d[A-Z]\d$'
        
        if re.match(pattern, postal_code):
            formatted = f"{postal_code[:3]} {postal_code[3:]}"
            return True, formatted
        else:
            return False, "Format de code postal invalide (ex: H1A 2B3)"

    @staticmethod
    def validate_tax_number(tax_number: str, field_name: str = "Numéro de taxe") -> Tuple[bool, str]:
        tax_number = tax_number.strip()
        
        if not tax_number:
            return False, f"{field_name} ne peut pas être vide"
        
        if not re.match(r'^\d{9}$', tax_number):
            return False, f"{field_name} doit contenir 9 chiffres"
        
        return True, tax_number

    @staticmethod
    def validate_establishment_number(number: str) -> Tuple[bool, str]:
        number = number.strip()
        
        if not number:
            return False, "Le numéro d'établissement ne peut pas être vide"
        
        if not re.match(r'^\d{6}$', number):
            return False, "Le numéro d'établissement doit contenir 6 chiffres"
        
        return True, number

    @staticmethod
    def validate_hostname(hostname: str) -> Tuple[bool, str]:
        hostname = hostname.strip()
        
        if not hostname:
            return False, "Le nom d'ordinateur ne peut pas être vide"
        
        if len(hostname) > 15:
            return False, "Le nom d'ordinateur ne peut pas dépasser 15 caractères"
        
        if not re.match(r'^[a-zA-Z0-9\-]+$', hostname):
            return False, "Le nom d'ordinateur ne peut contenir que des lettres, chiffres et tirets"
        
        if hostname.startswith('-') or hostname.endswith('-'):
            return False, "Le nom d'ordinateur ne peut pas commencer ou finir par un tiret"
        
        return True, hostname

    @staticmethod
    def test_network_connectivity(ip: str, timeout: int = 3) -> Tuple[bool, str]:
        import os
        import platform
        
        # Test 1: Port 445 (SMB)
        logger.info(f"Test de connexion au serveur {ip} sur le port 445 (SMB)...")
        try:
            socket.setdefaulttimeout(timeout)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, 445))
            sock.close()
            logger.info(f"✅ Port 445 accessible sur {ip}")
        except socket.timeout:
            msg = f"Délai d'attente dépassé - Le serveur {ip} ne répond pas sur le port 445.\n\nVérifiez que:\n1. Le serveur est allumé\n2. L'adresse IP est correcte\n3. Le pare-feu Windows autorise le port 445"
            logger.error(f"❌ {msg}")
            return False, msg
        except socket.error as e:
            msg = f"Impossible de se connecter au port 445 sur {ip}.\n\nErreur: {str(e)}\n\nVérifiez le pare-feu Windows et les partages réseau."
            logger.error(f"❌ {msg}")
            return False, msg
        except Exception as e:
            msg = f"Erreur inattendue lors du test de connexion: {str(e)}"
            logger.error(f"❌ {msg}")
            return False, msg
        
        # Test 2: Vérification des partages \\ip\xml et \\ip\logs
        logger.info(f"Vérification des partages réseau sur {ip}...")
        shares_ok = True
        missing_shares = []
        
        if platform.system() == "Windows":
            for share in ["xml", "logs"]:
                share_path = f"\\\\{ip}\\{share}"
                logger.info(f"Test d'accès au partage {share_path}...")
                if not os.path.exists(share_path):
                    missing_shares.append(share)
                    logger.warning(f"⚠️  Partage '{share}' non accessible : {share_path}")
                    shares_ok = False
                else:
                    logger.info(f"✅ Partage '{share}' accessible : {share_path}")
        
        if not shares_ok:
            msg = f"⚠️  Connexion réseau établie mais partages manquants:\n\n"
            msg += "Partages manquants ou inaccessibles:\n"
            for share in missing_shares:
                msg += f"  - \\\\{ip}\\{share}\n"
            msg += f"\nVérifiez que ces dossiers sont bien partagés sur le serveur {ip}."
            logger.warning(msg)
            return False, msg
        
        logger.info(f"✅ Connexion réseau et partages OK sur {ip}")
        return True, f"✅ Connexion réseau réussie\n✅ Tous les partages sont accessibles"

    @staticmethod
    def validate_mev_sector(sector: str) -> Tuple[bool, str]:
        sector = sector.strip().upper()
        valid_sectors = ["RES", "BAR", "CDR"]
        
        if sector not in valid_sectors:
            return False, f"Secteur invalide. Valeurs acceptées : {', '.join(valid_sectors)}"
        
        return True, sector
