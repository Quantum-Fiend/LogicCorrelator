"""
LogicCorrelator - Integration Test
End-to-end integration testing
"""

import json
import time
import subprocess
import sys
from pathlib import Path


class IntegrationTest:
    """Integration tests for LogicCorrelator"""
    
    def __init__(self):
        """Initialize test suite"""
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def test_event_validation(self):
        """Test event schema validation"""
        print("\n[TEST] Event Schema Validation...")
        
        try:
            from core.event_schema import EventValidator
            
            validator = EventValidator("config/event_schema.json")
            
            # Valid event
            valid_event = {
                'type': 'auth_fail',
                'timestamp': '2025-12-24T12:00:00Z',
                'user': 'testuser',
                'source_ip': '192.168.1.1'
            }
            
            if validator.validate(valid_event):
                print("  ✓ Valid event accepted")
                self.passed += 1
            else:
                print("  ✗ Valid event rejected")
                self.failed += 1
                return False
            
            # Invalid event (missing required field)
            invalid_event = {
                'type': 'auth_fail',
                'user': 'testuser'
            }
            
            if not validator.validate(invalid_event):
                print("  ✓ Invalid event rejected")
                self.passed += 1
            else:
                print("  ✗ Invalid event accepted")
                self.failed += 1
                return False
            
            return True
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            self.failed += 1
            return False
    
    def test_state_manager(self):
        """Test state manager functionality"""
        print("\n[TEST] State Manager...")
        
        try:
            from core.state_manager import StateManager
            
            config = {
                'collection': {'retention_window': 3600}
            }
            
            manager = StateManager(config)
            
            # Add events
            event1 = {
                'type': 'auth_fail',
                'timestamp': '2025-12-24T12:00:00Z',
                'user': 'alice'
            }
            
            event2 = {
                'type': 'auth_fail',
                'timestamp': '2025-12-24T12:00:05Z',
                'user': 'alice'
            }
            
            manager.add_event(event1)
            manager.add_event(event2)
            
            # Query events
            events = manager.get_events_by_type('auth_fail')
            
            if len(events) == 2:
                print("  ✓ Events stored correctly")
                self.passed += 1
            else:
                print(f"  ✗ Expected 2 events, got {len(events)}")
                self.failed += 1
                return False
            
            # Count events
            count = manager.count_events('auth_fail')
            if count == 2:
                print("  ✓ Event counting works")
                self.passed += 1
            else:
                print(f"  ✗ Expected count 2, got {count}")
                self.failed += 1
                return False
            
            return True
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            self.failed += 1
            return False
    
    def test_rule_validation(self):
        """Test rule validation"""
        print("\n[TEST] Rule Validation...")
        
        try:
            from tests.rule_validator import RuleValidator
            
            validator = RuleValidator()
            
            # Test a rule file
            rule_file = "rules/credential_attacks.yaml"
            
            if Path(rule_file).exists():
                if validator.validate_rule_file(rule_file):
                    print("  ✓ Rule file validation passed")
                    self.passed += 1
                    return True
                else:
                    print("  ✗ Rule file validation failed")
                    self.failed += 1
                    return False
            else:
                print(f"  ⚠ Rule file not found: {rule_file}")
                return True
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            self.failed += 1
            return False
    
    def test_mitre_mapper(self):
        """Test MITRE ATT&CK mapper"""
        print("\n[TEST] MITRE ATT&CK Mapper...")
        
        try:
            from features.mitre_mapper import MITREMapper
            
            mapper = MITREMapper()
            
            # Test technique lookup
            tech_info = mapper.get_technique_info("T1110.001")
            
            if tech_info and tech_info['name'] == "Password Guessing":
                print("  ✓ Technique lookup works")
                self.passed += 1
            else:
                print("  ✗ Technique lookup failed")
                self.failed += 1
                return False
            
            # Test alert enrichment
            alert = {
                'rule_name': 'Test Rule',
                'mitre_techniques': ['T1110.001', 'T1059.001']
            }
            
            enriched = mapper.enrich_alert(alert)
            
            if 'mitre_details' in enriched and len(enriched['mitre_details']) == 2:
                print("  ✓ Alert enrichment works")
                self.passed += 1
            else:
                print("  ✗ Alert enrichment failed")
                self.failed += 1
                return False
            
            return True
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            self.failed += 1
            return False
    
    def test_event_generation(self):
        """Test event generator"""
        print("\n[TEST] Event Generator...")
        
        try:
            from tests.event_generator import EventGenerator
            
            generator = EventGenerator()
            
            # Generate events
            events = generator.generate_random_events(5)
            
            if len(events) == 5:
                print("  ✓ Event generation works")
                self.passed += 1
            else:
                print(f"  ✗ Expected 5 events, got {len(events)}")
                self.failed += 1
                return False
            
            # Validate generated events
            from core.event_schema import EventValidator
            validator = EventValidator("config/event_schema.json")
            
            valid_count = sum(1 for e in events if validator.validate(e))
            
            if valid_count == len(events):
                print("  ✓ Generated events are valid")
                self.passed += 1
            else:
                print(f"  ✗ Only {valid_count}/{len(events)} events are valid")
                self.failed += 1
                return False
            
            return True
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            self.failed += 1
            return False
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("="*60)
        print("LogicCorrelator - Integration Tests")
        print("="*60)
        
        # Run tests
        self.test_event_validation()
        self.test_state_manager()
        self.test_rule_validation()
        self.test_mitre_mapper()
        self.test_event_generation()
        
        # Summary
        print("\n" + "="*60)
        print("Test Summary")
        print("="*60)
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Total:  {self.passed + self.failed}")
        
        if self.failed == 0:
            print("\n✓ All tests passed!")
            print("="*60)
            return 0
        else:
            print(f"\n✗ {self.failed} test(s) failed")
            print("="*60)
            return 1


def main():
    """Main entry point"""
    test_suite = IntegrationTest()
    return test_suite.run_all_tests()


if __name__ == "__main__":
    exit(main())
