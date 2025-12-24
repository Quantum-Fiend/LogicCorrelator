"""
LogicCorrelator - Credential Attack Demo
Demonstrates detection of credential stuffing attack
"""

import json
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.event_generator import EventGenerator


def run_demo():
    """Run credential attack demonstration"""
    print("="*60)
    print("LogicCorrelator - Credential Attack Demo")
    print("="*60)
    print()
    print("This demo simulates a credential stuffing attack:")
    print("  1. Multiple failed login attempts (5x)")
    print("  2. Successful authentication")
    print("  3. Suspicious PowerShell execution")
    print("  4. External network connection")
    print()
    print("Expected Detection:")
    print("  • Rule: Credential Compromise Chain (CRED-003)")
    print("  • Severity: CRITICAL")
    print("  • MITRE: T1110, T1059.001, T1071")
    print()
    print("="*60)
    print()
    
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
        print(f"     {json.dumps(event, indent=2)}")
        time.sleep(1)
    
    print()
    
    # Phase 2: Successful compromise
    print("[PHASE 2] Successful authentication...")
    time.sleep(2)
    event = generator.generate_auth_success(user, attacker_ip)
    print(f"  → Login successful!")
    print(f"     {json.dumps(event, indent=2)}")
    time.sleep(1)
    
    print()
    
    # Phase 3: Command execution
    print("[PHASE 3] Suspicious process execution...")
    time.sleep(2)
    event = generator.generate_process_start('powershell.exe', user)
    print(f"  → PowerShell launched")
    print(f"     {json.dumps(event, indent=2)}")
    time.sleep(1)
    
    print()
    
    # Phase 4: External connection
    print("[PHASE 4] External network connection...")
    time.sleep(2)
    event = generator.generate_network_connect('198.51.100.50', 443)
    print(f"  → Outbound connection established")
    print(f"     {json.dumps(event, indent=2)}")
    
    print()
    print("="*60)
    print("Attack simulation complete!")
    print("="*60)
    print()
    print("Expected Alert:")
    print("  🚨 CRITICAL: Possible credential compromise with command execution")
    print("  📊 Confidence: 95%")
    print("  🎯 MITRE ATT&CK:")
    print("     - T1110 (Brute Force)")
    print("     - T1059.001 (PowerShell)")
    print("     - T1071 (Application Layer Protocol)")
    print()
    print("Decision Graph:")
    print("  Rule → Condition 1 (auth_fail ≥3) → Condition 2 (process_start)")
    print("      → Condition 3 (network_connect) → ALERT")
    print()
    print("="*60)
    print()
    print("To see this in action:")
    print("  1. Start LogicCorrelator: make start")
    print("  2. Open dashboard: http://localhost:3000")
    print("  3. Run this demo and watch alerts appear!")
    print()


if __name__ == "__main__":
    run_demo()
