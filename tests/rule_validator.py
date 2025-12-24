"""
LogicCorrelator - Rule Validator
Validates correlation rule syntax and structure
"""

import yaml
import json
from pathlib import Path
from typing import List, Dict, Any


class RuleValidator:
    """Validates correlation rules"""
    
    REQUIRED_FIELDS = ['name', 'id', 'severity', 'conditions', 'actions']
    VALID_SEVERITIES = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    VALID_EVENT_TYPES = [
        'auth_fail', 'auth_success', 'process_start', 'network_connect',
        'file_access', 'registry_change', 'privilege_escalation'
    ]
    
    def __init__(self):
        """Initialize validator"""
        self.errors = []
        self.warnings = []
    
    def validate_rule_file(self, filepath: str) -> bool:
        """
        Validate a YAML rule file
        
        Args:
            filepath: Path to rule file
            
        Returns:
            True if valid, False otherwise
        """
        print(f"\n[VALIDATOR] Validating {filepath}...")
        self.errors = []
        self.warnings = []
        
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
            
            if not data or 'rules' not in data:
                self.errors.append("File must contain 'rules' key")
                return False
            
            rules = data['rules']
            if not isinstance(rules, list):
                self.errors.append("'rules' must be a list")
                return False
            
            for i, rule in enumerate(rules):
                self._validate_rule(rule, i)
            
            # Print results
            if self.errors:
                print(f"  ✗ {len(self.errors)} error(s) found:")
                for error in self.errors:
                    print(f"    - {error}")
                return False
            
            if self.warnings:
                print(f"  ⚠ {len(self.warnings)} warning(s):")
                for warning in self.warnings:
                    print(f"    - {warning}")
            
            print(f"  ✓ Valid ({len(rules)} rule(s))")
            return True
            
        except yaml.YAMLError as e:
            self.errors.append(f"YAML parsing error: {e}")
            print(f"  ✗ YAML error: {e}")
            return False
        except FileNotFoundError:
            self.errors.append(f"File not found: {filepath}")
            print(f"  ✗ File not found")
            return False
        except Exception as e:
            self.errors.append(f"Unexpected error: {e}")
            print(f"  ✗ Error: {e}")
            return False
    
    def _validate_rule(self, rule: Dict[str, Any], index: int):
        """Validate a single rule"""
        rule_id = rule.get('id', f'rule-{index}')
        
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in rule:
                self.errors.append(f"Rule {rule_id}: Missing required field '{field}'")
        
        # Validate severity
        severity = rule.get('severity', '').upper()
        if severity and severity not in self.VALID_SEVERITIES:
            self.errors.append(
                f"Rule {rule_id}: Invalid severity '{severity}'. "
                f"Must be one of {self.VALID_SEVERITIES}"
            )
        
        # Validate conditions
        conditions = rule.get('conditions', [])
        if not isinstance(conditions, list):
            self.errors.append(f"Rule {rule_id}: 'conditions' must be a list")
        elif len(conditions) == 0:
            self.errors.append(f"Rule {rule_id}: Must have at least one condition")
        else:
            for i, condition in enumerate(conditions):
                self._validate_condition(condition, rule_id, i)
        
        # Validate actions
        actions = rule.get('actions', [])
        if not isinstance(actions, list):
            self.errors.append(f"Rule {rule_id}: 'actions' must be a list")
        elif len(actions) == 0:
            self.warnings.append(f"Rule {rule_id}: No actions defined")
        
        # Validate MITRE techniques (optional but recommended)
        if 'mitre_techniques' not in rule:
            self.warnings.append(f"Rule {rule_id}: No MITRE ATT&CK techniques specified")
    
    def _validate_condition(self, condition: Dict[str, Any], rule_id: str, index: int):
        """Validate a condition"""
        if 'type' not in condition:
            self.errors.append(f"Rule {rule_id}, condition {index}: Missing 'type' field")
            return
        
        event_type = condition['type']
        if event_type not in self.VALID_EVENT_TYPES:
            self.warnings.append(
                f"Rule {rule_id}, condition {index}: "
                f"Unknown event type '{event_type}'"
            )
        
        # Validate temporal fields
        if 'window' in condition:
            if not isinstance(condition['window'], int) or condition['window'] <= 0:
                self.errors.append(
                    f"Rule {rule_id}, condition {index}: "
                    f"'window' must be a positive integer"
                )
        
        if 'within' in condition:
            if not isinstance(condition['within'], int) or condition['within'] <= 0:
                self.errors.append(
                    f"Rule {rule_id}, condition {index}: "
                    f"'within' must be a positive integer"
                )


def main():
    """Main entry point"""
    print("="*60)
    print("LogicCorrelator - Rule Validator")
    print("="*60)
    
    validator = RuleValidator()
    rules_dir = Path("rules")
    
    if not rules_dir.exists():
        print(f"\n[ERROR] Rules directory not found: {rules_dir}")
        return 1
    
    # Find all YAML files
    rule_files = list(rules_dir.glob("*.yaml")) + list(rules_dir.glob("*.yml"))
    
    if not rule_files:
        print(f"\n[WARNING] No rule files found in {rules_dir}")
        return 0
    
    print(f"\nFound {len(rule_files)} rule file(s)")
    
    # Validate each file
    all_valid = True
    for rule_file in rule_files:
        if not validator.validate_rule_file(str(rule_file)):
            all_valid = False
    
    # Summary
    print("\n" + "="*60)
    if all_valid:
        print("✓ All rule files are valid!")
        print("="*60)
        return 0
    else:
        print("✗ Some rule files have errors")
        print("="*60)
        return 1


if __name__ == "__main__":
    exit(main())
