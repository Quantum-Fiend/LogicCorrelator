"""
LogicCorrelator - Lateral Movement Demo
Demonstrates detection of lateral movement via SMB
"""

import json
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.event_generator import EventGenerator


def run_demo():
    """Run lateral movement demonstration"""
    print("="*60)
    print("LogicCorrelator - Lateral Movement Demo")
    print("="*60)
    print()
    print("This demo simulates lateral movement via SMB:")
    print("  1. Remote SMB connection (port 445)")
    print("  2. Remote execution tool (PsExec)")
    print("  3. Additional SMB connections to other hosts")
    print()
    print("Expected Detection:")
    print("  • Rule: SMB Lateral Movement (LAT-001)")
    print("  • Severity: HIGH")
    print("  • MITRE: T1021.002, T1570")
    print()
    print("="*60)
    print()
    
    generator = EventGenerator()
    
    print("[DEMO] Starting lateral movement simulation...\n")
    
    # Phase 1: Initial SMB connection
    print("[PHASE 1] Initial SMB connection...")
    event = generator.generate_network_connect('192.168.1.50', 445)
    print(f"  → SMB connection to 192.168.1.50:445")
    print(f"     {json.dumps(event, indent=2)}")
    time.sleep(2)
    
    print()
    
    # Phase 2: Remote execution
    print("[PHASE 2] Remote execution tool launched...")
    time.sleep(1)
    event = generator.generate_process_start('psexec.exe', 'admin')
    print(f"  → PsExec.exe executed")
    print(f"     {json.dumps(event, indent=2)}")
    time.sleep(2)
    
    print()
    
    # Phase 3: Lateral spread
    print("[PHASE 3] Lateral spread to additional hosts...")
    targets = ['192.168.1.51', '192.168.1.52', '192.168.1.53']
    
    for target in targets:
        time.sleep(1)
        event = generator.generate_network_connect(target, 445)
        print(f"  → SMB connection to {target}:445")
        print(f"     {json.dumps(event, indent=2)}")
    
    print()
    print("="*60)
    print("Lateral movement simulation complete!")
    print("="*60)
    print()
    print("Expected Alert:")
    print("  🚨 HIGH: Possible SMB lateral movement detected")
    print("  📊 Confidence: 85%")
    print("  🎯 MITRE ATT&CK:")
    print("     - T1021.002 (SMB/Windows Admin Shares)")
    print("     - T1570 (Lateral Tool Transfer)")
    print()
    print("Attack Chain:")
    print("  SMB Connection → Remote Execution → Lateral Spread")
    print()
    print("Indicators:")
    print("  • Multiple SMB connections in short timeframe")
    print("  • Use of remote execution tools (PsExec)")
    print("  • Pattern consistent with lateral movement")
    print()
    print("="*60)
    print()
    print("Recommended Response:")
    print("  1. Isolate affected hosts")
    print("  2. Review authentication logs")
    print("  3. Check for unauthorized access")
    print("  4. Investigate source of initial compromise")
    print()


if __name__ == "__main__":
    run_demo()
