import os
import re
import xml.etree.ElementTree as ET
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class XMLConfigManager:
    def __init__(self, config_path: str = r"c:\pos\xml\config.xml", 
                 devices_path: str = r"c:\pos\xml\devices.xml",
                 menu_path: str = r"c:\pos\xml\menu.xml"):
        self.config_path = config_path
        self.devices_path = devices_path
        self.menu_path = menu_path
        self._ensure_paths_exist()

    def _ensure_paths_exist(self):
        for path in [self.config_path, self.devices_path]:
            dir_path = os.path.dirname(path)
            if dir_path and not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    logger.info(f"Créé le répertoire : {dir_path}")
                except Exception as e:
                    logger.warning(f"Impossible de créer {dir_path}: {e}")
        
        if not os.path.exists(self.config_path):
            self._create_default_config()
    
    def _create_default_config(self):
        try:
            default_config = '''<?xml version="1.0" encoding="utf-8"?>
<Config Database="" Server="" Replication="0" Auto_Logout="0" GUI_Dark_Mode="1" 
        Debut_Print="0" Auto_Print="0" Use_Floorplan="1" Use_Retail="1" 
        Use_Counter="1" Use_Pickup="1" Use_Delivery="1" GUI_Font_Size="12" 
        GUI_List_Height="30" MEV_UserName="" MEV_Gst="" MEV_Qst="" 
        MEV_Auth_Code="" MEV_File_Number="" MEV_Address="" MEV_Zip="" 
        MEV_Sector="RES" MEV_Commerce_Name="" />
'''
            with open(self.config_path, 'w', encoding="utf-8") as f:
                f.write(default_config)
            logger.info(f"Fichier de configuration par défaut créé : {self.config_path}")
        except Exception as e:
            logger.error(f"Impossible de créer le fichier de configuration par défaut : {e}")

    def load_config_data(self, keys: Optional[List[str]] = None) -> Dict[str, str]:
        if keys is None:
            keys = [
                "Database", "Server", "Replication", "Auto_Logout", "GUI_Dark_Mode",
                "Debut_Print", "Auto_Print", "Use_Floorplan", "Use_Retail",
                "Use_Counter", "Use_Pickup", "Use_Delivery", "GUI_Font_Size", "GUI_List_Height"
            ]
        
        data = {}
        if not os.path.exists(self.config_path):
            logger.warning(f"Fichier de configuration introuvable : {self.config_path}")
            return data

        try:
            with open(self.config_path, 'r', encoding="utf-8") as f:
                content = f.read()
                for key in keys:
                    m = re.search(rf'{key}="([^"]*)"', content)
                    if m:
                        data[key] = m.group(1)
                    else:
                        data[key] = ""
            logger.info(f"Configuration chargée avec succès : {len(data)} clés")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration : {e}")
        
        return data

    def load_mev_data(self) -> Dict[str, str]:
        keys = [
            "MEV_UserName", "MEV_Gst", "MEV_Qst", "MEV_Auth_Code",
            "MEV_File_Number", "MEV_Address", "MEV_Zip", "MEV_Sector",
            "MEV_Commerce_Name"
        ]
        return self.load_config_data(keys)

    def save_config_data(self, data: Dict[str, str]) -> bool:
        if not os.path.exists(self.config_path):
            logger.warning(f"Fichier de configuration introuvable, création d'un nouveau fichier")
            self._create_default_config()
            if not os.path.exists(self.config_path):
                logger.error("Impossible de créer le fichier de configuration")
                return False

        try:
            with open(self.config_path, 'r', encoding="utf-8") as f:
                content = f.read()

            for key, value in data.items():
                if re.search(rf'{key}="[^"]*"', content):
                    content = re.sub(rf'{key}="[^"]*"', f'{key}="{value}"', content)
                else:
                    logger.warning(f"Clé non trouvée dans le fichier : {key}")

            with open(self.config_path, 'w', encoding="utf-8") as f:
                f.write(content)
            
            logger.info("Configuration sauvegardée avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde : {e}")
            return False

    def update_xml_attribute(self, filepath: str, element_name: str, new_value: str) -> bool:
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            element = root.find(element_name)
            if element is not None:
                element.text = new_value
                tree.write(filepath, encoding="utf-8", xml_declaration=True)
                logger.info(f"Élément {element_name} mis à jour avec succès")
                return True
            else:
                logger.warning(f"Élément {element_name} non trouvé dans {filepath}")
                return False
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour XML : {e}")
            return False
    
    def load_devices_data(self) -> Dict[str, str]:
        data = {}
        if not os.path.exists(self.devices_path):
            logger.warning(f"Fichier devices.xml introuvable : {self.devices_path}")
            return data

        try:
            with open(self.devices_path, 'r', encoding="utf-8") as f:
                content = f.read()
                
                m_ip = re.search(r'ip="([^"]*)"', content)
                if m_ip:
                    data['ip'] = m_ip.group(1)
                else:
                    data['ip'] = ""
                
                m_com = re.search(r'com="([^"]*)"', content)
                if m_com:
                    data['com'] = m_com.group(1)
                else:
                    data['com'] = ""
                
                m_baud = re.search(r'baud="([^"]*)"', content)
                if m_baud:
                    data['baud'] = m_baud.group(1)
                else:
                    data['baud'] = "9600"
                
                m_protocol = re.search(r'protocol="([^"]*)"', content)
                if m_protocol:
                    data['protocol'] = m_protocol.group(1)
                else:
                    data['protocol'] = "Web Network Printer"
                
            logger.info(f"Devices chargé : {data}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de devices.xml : {e}")
        
        return data

    def save_devices_data(self, data: Dict[str, str]) -> bool:
        if not os.path.exists(self.devices_path):
            logger.warning(f"Fichier devices.xml introuvable, création d'un nouveau fichier")
            try:
                default_devices = '''<?xml version="1.0" encoding="utf-8"?>
<Devices ip="" com="" baud="9600" protocol="Web Network Printer" />
'''
                with open(self.devices_path, 'w', encoding="utf-8") as f:
                    f.write(default_devices)
                logger.info(f"Fichier devices.xml créé : {self.devices_path}")
            except Exception as e:
                logger.error(f"Impossible de créer devices.xml : {e}")
                return False

        try:
            with open(self.devices_path, 'r', encoding="utf-8") as f:
                content = f.read()

            for key, value in data.items():
                if key == 'ip':
                    content = re.sub(r'ip="[^"]*"', f'ip="{value}"', content)
                    if 'ip=' not in content:
                        content = content.replace('<Devices ', f'<Devices ip="{value}" ')
                elif key == 'com':
                    content = re.sub(r'com="[^"]*"', f'com="{value}"', content)
                    if 'com=' not in content:
                        content = content.replace('<Devices ', f'<Devices com="{value}" ')
                elif key == 'baud':
                    content = re.sub(r'baud="[^"]*"', f'baud="{value}"', content)
                    if 'baud=' not in content:
                        content = content.replace('<Devices ', f'<Devices baud="{value}" ')
                elif key == 'protocol':
                    content = re.sub(r'protocol="[^"]*"', f'protocol="{value}"', content)
                    if 'protocol=' not in content:
                        content = content.replace('<Devices ', f'<Devices protocol="{value}" ')

            with open(self.devices_path, 'w', encoding="utf-8") as f:
                f.write(content)
            
            logger.info(f"Devices.xml sauvegardé avec succès : {data}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de devices.xml : {e}")
            return False

    def update_layout_header(self, commerce_name: str, address_num: str, address_street: str, 
                            city: str, postal_code: str) -> bool:
        layout_path = r"c:\pos\xml\layout.xml"
        
        if not os.path.exists(layout_path):
            logger.warning(f"Fichier layout.xml introuvable : {layout_path}")
            return False
        
        try:
            tree = ET.parse(layout_path)
            root = tree.getroot()
            
            header = root.find("Header")
            if header is None:
                logger.warning("Élément <Header> non trouvé dans layout.xml")
                return False
            
            value_elements = header.findall("value[@center='True']")
            
            if len(value_elements) < 3:
                logger.warning(f"Pas assez d'éléments <value center='True'> trouvés (trouvé: {len(value_elements)}, requis: 3)")
                return False
            
            line1 = commerce_name.upper() if commerce_name else ""
            line2 = f"{address_num} {address_street}".strip().upper()
            line3 = f"{city}, QUEBEC, {postal_code}".upper()
            
            value_elements[0].set("text", line1)
            value_elements[1].set("text", line2)
            value_elements[2].set("text", line3)
            
            tree.write(layout_path, encoding="utf-8", xml_declaration=True)
            logger.info(f"Layout header mis à jour avec succès:")
            logger.info(f"  Ligne 1: {line1}")
            logger.info(f"  Ligne 2: {line2}")
            logger.info(f"  Ligne 3: {line3}")
            return True
        
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du layout header : {e}")
            return False
    
    def ensure_receipt_printer_in_menu(self) -> bool:
        if not os.path.exists(self.menu_path):
            logger.warning(f"Fichier menu.xml introuvable : {self.menu_path}")
            return False
        
        try:
            with open(self.menu_path, 'r', encoding="utf-8") as f:
                content = f.read()
            
            if '<Printer Name="Receipt"' in content:
                logger.info("Ligne Receipt Printer déjà présente dans menu.xml")
                return True
            
            printer_line = '<Printer Name="Receipt" DriverName="Receipt" MEV="1" Full_Size="0" Label="0" RAW="0" Catch_All="0" Print_Tables="1" Print_Counter="1" Print_Pickup="1" Print_Delivery="1" list_Events="|Receipt,Reports|" list_Categories="" list_Items="" list_Options="" list_Choices="" IP="" Port="" Auto_Remove_Tickets="0" />'
            
            if '<PRINTERS Text="PRINTERS">' in content:
                content = content.replace(
                    '<PRINTERS Text="PRINTERS">',
                    f'<PRINTERS Text="PRINTERS">\n\t\t{printer_line}'
                )
                
                with open(self.menu_path, 'w', encoding="utf-8") as f:
                    f.write(content)
                
                logger.info("Ligne Receipt Printer ajoutée dans menu.xml avec succès")
                return True
            else:
                logger.warning("Section <PRINTERS Text=\"PRINTERS\"> non trouvée dans menu.xml")
                return False
        
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de menu.xml : {e}")
            return False
