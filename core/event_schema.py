"""
LogicCorrelator - Event Schema Validator
Validates events against JSON schema definitions
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path


class EventValidator:
    """Validates events against defined schemas"""
    
    def __init__(self, schema_path: str = "config/event_schema.json"):
        """
        Initialize validator with schema file
        
        Args:
            schema_path: Path to event schema JSON file
        """
        self.schema_path = schema_path
        self.schemas = self._load_schemas()
        print(f"[VALIDATOR] Loaded {len(self.schemas)} event type schemas")
    
    def _load_schemas(self) -> Dict[str, Dict]:
        """Load event schemas from JSON file"""
        try:
            with open(self.schema_path, 'r') as f:
                data = json.load(f)
            return data.get('event_types', {})
        except FileNotFoundError:
            print(f"[VALIDATOR] Warning: Schema file not found: {self.schema_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"[VALIDATOR] Error parsing schema file: {e}")
            return {}
    
    def validate(self, event: Dict[str, Any]) -> bool:
        """
        Validate event against its schema
        
        Args:
            event: Event dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        event_type = event.get('type')
        
        if not event_type:
            print("[VALIDATOR] Event missing 'type' field")
            return False
        
        if event_type not in self.schemas:
            print(f"[VALIDATOR] Unknown event type: {event_type}")
            return False
        
        schema = self.schemas[event_type]
        fields = schema.get('fields', {})
        
        # Validate required fields
        for field_name, field_spec in fields.items():
            if field_spec.get('required', False):
                if field_name not in event:
                    print(f"[VALIDATOR] Missing required field '{field_name}' for event type '{event_type}'")
                    return False
            
            # Validate field type if present
            if field_name in event:
                if not self._validate_field_type(event[field_name], field_spec):
                    print(f"[VALIDATOR] Invalid type for field '{field_name}' in event type '{event_type}'")
                    return False
        
        return True
    
    def _validate_field_type(self, value: Any, field_spec: Dict) -> bool:
        """
        Validate field value against type specification
        
        Args:
            value: Field value
            field_spec: Field specification from schema
            
        Returns:
            True if valid, False otherwise
        """
        field_type = field_spec.get('type', 'string')
        
        # Type checking
        if field_type == 'string' and not isinstance(value, str):
            return False
        elif field_type == 'integer' and not isinstance(value, int):
            return False
        elif field_type == 'boolean' and not isinstance(value, bool):
            return False
        
        # Enum validation
        if 'enum' in field_spec:
            if value not in field_spec['enum']:
                return False
        
        return True
    
    def get_schema(self, event_type: str) -> Optional[Dict]:
        """
        Get schema for specific event type
        
        Args:
            event_type: Event type name
            
        Returns:
            Schema dictionary or None if not found
        """
        return self.schemas.get(event_type)
    
    def list_event_types(self) -> list:
        """Get list of all supported event types"""
        return list(self.schemas.keys())
