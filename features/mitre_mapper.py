"""
LogicCorrelator - MITRE ATT&CK Mapper
Maps detected patterns to MITRE ATT&CK techniques
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path


class MITREMapper:
    """Maps correlation rules and alerts to MITRE ATT&CK framework"""
    
    # MITRE ATT&CK technique database (simplified subset)
    TECHNIQUES = {
        "T1110": {
            "name": "Brute Force",
            "description": "Adversaries may use brute force techniques to gain access to accounts",
            "tactics": ["Credential Access"],
            "url": "https://attack.mitre.org/techniques/T1110/"
        },
        "T1110.001": {
            "name": "Password Guessing",
            "description": "Adversaries may use password guessing to gain access",
            "tactics": ["Credential Access"],
            "parent": "T1110",
            "url": "https://attack.mitre.org/techniques/T1110/001/"
        },
        "T1110.003": {
            "name": "Password Spraying",
            "description": "Adversaries may use password spraying to gain access",
            "tactics": ["Credential Access"],
            "parent": "T1110",
            "url": "https://attack.mitre.org/techniques/T1110/003/"
        },
        "T1110.004": {
            "name": "Credential Stuffing",
            "description": "Adversaries may use credential stuffing attacks",
            "tactics": ["Credential Access"],
            "parent": "T1110",
            "url": "https://attack.mitre.org/techniques/T1110/004/"
        },
        "T1059.001": {
            "name": "PowerShell",
            "description": "Adversaries may abuse PowerShell for execution",
            "tactics": ["Execution"],
            "parent": "T1059",
            "url": "https://attack.mitre.org/techniques/T1059/001/"
        },
        "T1021.002": {
            "name": "SMB/Windows Admin Shares",
            "description": "Adversaries may use SMB for lateral movement",
            "tactics": ["Lateral Movement"],
            "parent": "T1021",
            "url": "https://attack.mitre.org/techniques/T1021/002/"
        },
        "T1047": {
            "name": "Windows Management Instrumentation",
            "description": "Adversaries may abuse WMI for execution",
            "tactics": ["Execution"],
            "url": "https://attack.mitre.org/techniques/T1047/"
        },
        "T1041": {
            "name": "Exfiltration Over C2 Channel",
            "description": "Adversaries may exfiltrate data over existing C2 channel",
            "tactics": ["Exfiltration"],
            "url": "https://attack.mitre.org/techniques/T1041/"
        },
        "T1071": {
            "name": "Application Layer Protocol",
            "description": "Adversaries may use application layer protocols",
            "tactics": ["Command and Control"],
            "url": "https://attack.mitre.org/techniques/T1071/"
        },
        "T1078": {
            "name": "Valid Accounts",
            "description": "Adversaries may use valid accounts to maintain access",
            "tactics": ["Defense Evasion", "Persistence", "Privilege Escalation", "Initial Access"],
            "url": "https://attack.mitre.org/techniques/T1078/"
        },
        "T1548.002": {
            "name": "Bypass User Account Control",
            "description": "Adversaries may bypass UAC mechanisms",
            "tactics": ["Privilege Escalation", "Defense Evasion"],
            "parent": "T1548",
            "url": "https://attack.mitre.org/techniques/T1548/002/"
        },
        "T1134": {
            "name": "Access Token Manipulation",
            "description": "Adversaries may modify access tokens",
            "tactics": ["Defense Evasion", "Privilege Escalation"],
            "url": "https://attack.mitre.org/techniques/T1134/"
        },
        "T1003.001": {
            "name": "LSASS Memory",
            "description": "Adversaries may dump credentials from LSASS",
            "tactics": ["Credential Access"],
            "parent": "T1003",
            "url": "https://attack.mitre.org/techniques/T1003/001/"
        }
    }
    
    def __init__(self):
        """Initialize MITRE mapper"""
        print(f"[MITRE_MAPPER] Initialized with {len(self.TECHNIQUES)} techniques")
    
    def get_technique_info(self, technique_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a MITRE ATT&CK technique
        
        Args:
            technique_id: MITRE technique ID (e.g., "T1110.001")
            
        Returns:
            Technique information dictionary or None
        """
        return self.TECHNIQUES.get(technique_id)
    
    def enrich_alert(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich alert with MITRE ATT&CK information
        
        Args:
            alert: Alert dictionary
            
        Returns:
            Enriched alert with MITRE details
        """
        enriched = alert.copy()
        
        technique_ids = alert.get('mitre_techniques', [])
        if not technique_ids:
            return enriched
        
        mitre_details = []
        tactics = set()
        
        for tech_id in technique_ids:
            tech_info = self.get_technique_info(tech_id)
            if tech_info:
                mitre_details.append({
                    'id': tech_id,
                    'name': tech_info['name'],
                    'description': tech_info['description'],
                    'url': tech_info['url']
                })
                tactics.update(tech_info['tactics'])
        
        enriched['mitre_details'] = mitre_details
        enriched['mitre_tactics'] = list(tactics)
        
        return enriched
    
    def generate_attack_navigator_layer(self, alerts: List[Dict[str, Any]], 
                                       layer_name: str = "LogicCorrelator Detections") -> Dict:
        """
        Generate MITRE ATT&CK Navigator layer JSON
        
        Args:
            alerts: List of alerts with MITRE techniques
            layer_name: Name for the layer
            
        Returns:
            ATT&CK Navigator layer JSON
        """
        # Count technique occurrences
        technique_counts = {}
        for alert in alerts:
            for tech_id in alert.get('mitre_techniques', []):
                technique_counts[tech_id] = technique_counts.get(tech_id, 0) + 1
        
        # Build layer
        techniques = []
        max_count = max(technique_counts.values()) if technique_counts else 1
        
        for tech_id, count in technique_counts.items():
            tech_info = self.get_technique_info(tech_id)
            if tech_info:
                # Color intensity based on frequency
                score = count / max_count
                
                techniques.append({
                    "techniqueID": tech_id,
                    "tactic": tech_info['tactics'][0].lower().replace(' ', '-'),
                    "score": score,
                    "color": self._get_color_for_score(score),
                    "comment": f"Detected {count} time(s)",
                    "enabled": True
                })
        
        layer = {
            "name": layer_name,
            "versions": {
                "attack": "13",
                "navigator": "4.8",
                "layer": "4.4"
            },
            "domain": "enterprise-attack",
            "description": f"LogicCorrelator detections - {len(alerts)} alerts analyzed",
            "filters": {
                "platforms": ["windows", "linux"]
            },
            "sorting": 3,
            "layout": {
                "layout": "side",
                "showID": True,
                "showName": True
            },
            "hideDisabled": False,
            "techniques": techniques,
            "gradient": {
                "colors": ["#ffffff", "#ff6666"],
                "minValue": 0,
                "maxValue": 1
            },
            "legendItems": [],
            "metadata": [],
            "showTacticRowBackground": False,
            "tacticRowBackground": "#dddddd"
        }
        
        return layer
    
    def _get_color_for_score(self, score: float) -> str:
        """
        Get color based on detection score
        
        Args:
            score: Score between 0 and 1
            
        Returns:
            Hex color string
        """
        if score >= 0.8:
            return "#ff0000"  # Red - very frequent
        elif score >= 0.6:
            return "#ff6600"  # Orange
        elif score >= 0.4:
            return "#ffcc00"  # Yellow
        elif score >= 0.2:
            return "#99cc00"  # Light green
        else:
            return "#66ff66"  # Green - infrequent
    
    def save_navigator_layer(self, layer: Dict, filename: str = "logiccorrelator_layer.json"):
        """
        Save ATT&CK Navigator layer to file
        
        Args:
            layer: Navigator layer dictionary
            filename: Output filename
        """
        output_path = Path("graphs") / filename
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(layer, f, indent=2)
        
        print(f"[MITRE_MAPPER] Saved ATT&CK Navigator layer: {output_path}")
        print(f"[MITRE_MAPPER] Upload to https://mitre-attack.github.io/attack-navigator/")
    
    def get_coverage_report(self, alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate coverage report showing which tactics/techniques were detected
        
        Args:
            alerts: List of alerts
            
        Returns:
            Coverage report dictionary
        """
        tactics_covered = set()
        techniques_covered = set()
        
        for alert in alerts:
            for tech_id in alert.get('mitre_techniques', []):
                tech_info = self.get_technique_info(tech_id)
                if tech_info:
                    techniques_covered.add(tech_id)
                    tactics_covered.update(tech_info['tactics'])
        
        return {
            'tactics_covered': list(tactics_covered),
            'techniques_covered': list(techniques_covered),
            'total_tactics': len(tactics_covered),
            'total_techniques': len(techniques_covered),
            'coverage_percentage': (len(techniques_covered) / len(self.TECHNIQUES)) * 100
        }
