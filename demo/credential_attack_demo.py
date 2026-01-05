"""
LogicCorrelator - Credential Attack Demo
Demonstrates detection of credential stuffing attack
"""

import json
import time
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.event_generator import EventGenerator



def run_demo():
    """Run credential attack demonstration"""
    import urllib.request
    import urllib.error

    DASHBOARD_API = "http://localhost:3000/api"

    def send_event(event):
        try:
            req = urllib.request.Request(
                f"{DASHBOARD_API}/events",
                data=json.dumps(event).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req)
        except Exception as e:
            print(f"[!] Failed to send event to dashboard: {e}")

    def send_alert(alert):
        try:
            req = urllib.request.Request(
                f"{DASHBOARD_API}/alerts",
                data=json.dumps(alert).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req)
        except Exception as e:
            print(f"[!] Failed to send alert to dashboard: {e}")

    print("="*60)
    print("LogicCorrelator - Credential Attack Demo")
    print("="*60)
    print()
    print("This demo simulates a credential stuffing attack (Connected Mode)")
    
    generator = EventGenerator()
    
    # Generate attack scenario
    print("[DEMO] Starting attack simulation...\n")
    
    user = 'alice'
    attacker_ip = '203.0.113.100'
    
    # Phase 1: Brute force attempts
    print("[PHASE 1] Brute force login attempts...")
    for i in range(5):
        event = generator.generate_auth_fail(user, attacker_ip)
        print(f"  → Failed login attempt {i+1}/5")
        send_event(event)
        time.sleep(1)
    
    print()
    
    # Phase 2: Successful compromise
    print("[PHASE 2] Successful authentication...")
    time.sleep(2)
    event = generator.generate_auth_success(user, attacker_ip)
    print(f"  → Login successful!")
    send_event(event)
    time.sleep(1)
    
    print()
    
    # Phase 3: Command execution
    print("[PHASE 3] Suspicious process execution...")
    time.sleep(2)
    event = generator.generate_process_start('powershell.exe', user)
    print(f"  → PowerShell launched")
    send_event(event)
    time.sleep(1)
    
    print()
    
    # Phase 4: External connection
    print("[PHASE 4] External network connection...")
    time.sleep(2)
    event = generator.generate_network_connect('198.51.100.50', 443)
    print(f"  → Outbound connection established")
    send_event(event)
    
    print()
    print("="*60)
    print("[ENGINE] Correlating events...")
    time.sleep(2)
    
    # Simulate Alert Generation
    alert = {
        "rule_id": "CRED-003",
        "rule_name": "Credential Compromise Chain",
        "severity": "CRITICAL",
        "message": "Possible credential stuffing attack followed by command execution",
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "confidence": 0.95,
        "mitre_techniques": ["T1110", "T1059.001", "T1071"]
    }
    
    print(f"  🚨 Generated Alert: {alert['rule_name']}")
    send_alert(alert)

    # Simulate Graph Generation
    print("[ENGINE] Generating correlation graph...")
    
    correlation_graph = {
        "rule_name": "Credential Compromise Chain",
        "event_count": 7,
        "graph": {
            "nodes": [
                {"id": "user_alice", "label": "User: Alice", "type": "user"},
                {"id": "ip_attacker", "label": "IP: 203.0.113.100", "type": "ip"},
                {"id": "proc_powershell", "label": "PowerShell.exe", "type": "process"},
                {"id": "ip_c2", "label": "C2: 198.51.100.50", "type": "ip"},
                {"id": "alert_node", "label": "Credential Chain", "type": "alert"}
            ],
            "edges": [
                {"source": "ip_attacker", "target": "user_alice", "label": "Brute Force (5x)"},
                {"source": "ip_attacker", "target": "user_alice", "label": "Login Success"},
                {"source": "user_alice", "target": "proc_powershell", "label": "Spawned"},
                {"source": "proc_powershell", "target": "ip_c2", "label": "Connect Loopback"},
                {"source": "proc_powershell", "target": "alert_node", "label": "Triggered"}
            ]
        }
    }

    def send_correlation(correlation):
        try:
            req = urllib.request.Request(
                f"{DASHBOARD_API}/correlations",
                data=json.dumps(correlation).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req)
            print("  ✓ Graph data sent to dashboard")
        except Exception as e:
            print(f"[!] Failed to send graph to dashboard: {e}")

    send_correlation(correlation_graph)
    
    print("="*60)
    print("Attack simulation complete!")
    print("Check your dashboard at http://localhost:3000")
    print("="*60)

if __name__ == "__main__":
    run_demo()
