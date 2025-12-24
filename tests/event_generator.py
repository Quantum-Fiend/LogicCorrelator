"""
LogicCorrelator - Event Generator
Generates synthetic events for testing and demonstration
"""

import json
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any


class EventGenerator:
    """Generates synthetic security events"""
    
    def __init__(self):
        """Initialize event generator"""
        self.users = ['alice', 'bob', 'charlie', 'admin', 'service_account']
        self.ips = [f'192.168.1.{i}' for i in range(10, 50)]
        self.external_ips = ['203.0.113.10', '198.51.100.20', '192.0.2.30']
        self.processes = [
            'powershell.exe', 'cmd.exe', 'wmic.exe', 'psexec.exe',
            'net.exe', 'sc.exe', 'reg.exe', 'rundll32.exe'
        ]
    
    def generate_auth_fail(self, user: str = None, ip: str = None) -> Dict[str, Any]:
        """Generate authentication failure event"""
        return {
            'type': 'auth_fail',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'user': user or random.choice(self.users),
            'source_ip': ip or random.choice(self.ips),
            'service': 'ssh',
            'reason': 'invalid_password',
            '_source': 'event_generator'
        }
    
    def generate_auth_success(self, user: str = None, ip: str = None) -> Dict[str, Any]:
        """Generate successful authentication event"""
        return {
            'type': 'auth_success',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'user': user or random.choice(self.users),
            'source_ip': ip or random.choice(self.ips),
            'service': 'ssh',
            '_source': 'event_generator'
        }
    
    def generate_process_start(self, process: str = None, user: str = None) -> Dict[str, Any]:
        """Generate process start event"""
        proc = process or random.choice(self.processes)
        return {
            'type': 'process_start',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'process_name': proc,
            'command_line': f'{proc} /c whoami',
            'pid': random.randint(1000, 9999),
            'user': user or random.choice(self.users),
            'executable_path': f'C:\\Windows\\System32\\{proc}',
            '_source': 'event_generator'
        }
    
    def generate_network_connect(self, dest_ip: str = None, dest_port: int = None) -> Dict[str, Any]:
        """Generate network connection event"""
        return {
            'type': 'network_connect',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'source_ip': random.choice(self.ips),
            'source_port': random.randint(49152, 65535),
            'dest_ip': dest_ip or random.choice(self.external_ips),
            'dest_port': dest_port or random.choice([80, 443, 445, 3389]),
            'protocol': 'tcp',
            'direction': 'outbound',
            '_source': 'event_generator'
        }
    
    def generate_credential_attack_scenario(self) -> List[Dict[str, Any]]:
        """Generate credential stuffing attack scenario"""
        events = []
        user = 'alice'
        ip = '192.168.1.100'
        
        print("[GENERATOR] Generating credential attack scenario...")
        
        # Multiple failed logins
        for i in range(5):
            events.append(self.generate_auth_fail(user, ip))
            time.sleep(0.1)
        
        # Successful login
        time.sleep(0.5)
        events.append(self.generate_auth_success(user, ip))
        
        # Suspicious process execution
        time.sleep(0.5)
        events.append(self.generate_process_start('powershell.exe', user))
        
        # External connection
        time.sleep(0.5)
        events.append(self.generate_network_connect('203.0.113.10', 443))
        
        return events
    
    def generate_lateral_movement_scenario(self) -> List[Dict[str, Any]]:
        """Generate lateral movement scenario"""
        events = []
        user = 'admin'
        
        print("[GENERATOR] Generating lateral movement scenario...")
        
        # SMB connection
        events.append(self.generate_network_connect('192.168.1.50', 445))
        time.sleep(0.5)
        
        # Remote execution
        events.append(self.generate_process_start('psexec.exe', user))
        time.sleep(0.5)
        
        # Additional SMB activity
        events.append(self.generate_network_connect('192.168.1.51', 445))
        
        return events
    
    def generate_random_events(self, count: int = 10) -> List[Dict[str, Any]]:
        """Generate random events"""
        events = []
        generators = [
            self.generate_auth_fail,
            self.generate_auth_success,
            self.generate_process_start,
            self.generate_network_connect
        ]
        
        for _ in range(count):
            generator = random.choice(generators)
            events.append(generator())
            time.sleep(0.1)
        
        return events


def main():
    """Main entry point"""
    import sys
    
    print("="*60)
    print("LogicCorrelator - Event Generator")
    print("="*60)
    
    generator = EventGenerator()
    
    if len(sys.argv) > 1:
        scenario = sys.argv[1].lower()
    else:
        scenario = 'random'
    
    # Generate events based on scenario
    if scenario == 'credential':
        events = generator.generate_credential_attack_scenario()
    elif scenario == 'lateral':
        events = generator.generate_lateral_movement_scenario()
    elif scenario == 'random':
        events = generator.generate_random_events(20)
    else:
        print(f"Unknown scenario: {scenario}")
        print("Available scenarios: credential, lateral, random")
        return 1
    
    # Output events as JSON (one per line)
    print(f"\nGenerated {len(events)} events:\n")
    for event in events:
        print(json.dumps(event))
    
    return 0


if __name__ == "__main__":
    exit(main())
