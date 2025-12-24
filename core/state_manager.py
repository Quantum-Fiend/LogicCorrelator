"""
LogicCorrelator - State Manager
Manages correlation state and temporal event windows
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque


class StateManager:
    """Manages event state and temporal windows"""
    
    def __init__(self, config: Dict):
        """
        Initialize state manager
        
        Args:
            config: System configuration
        """
        self.config = config
        self.retention_window = config['collection']['retention_window']
        
        # Event windows organized by type
        self.event_windows = defaultdict(deque)
        
        # Correlation state
        self.correlation_state = {}
        
        # Statistics
        self.stats = {
            'total_events_stored': 0,
            'events_expired': 0,
            'windows_active': 0
        }
        
        print("[STATE_MANAGER] State manager initialized")
    
    def add_event(self, event: Dict[str, Any]):
        """
        Add event to appropriate temporal window
        
        Args:
            event: Normalized event
        """
        event_type = event.get('type', 'unknown')
        
        # Add timestamp if not present
        if 'timestamp' not in event:
            event['timestamp'] = datetime.utcnow().isoformat()
        
        # Convert timestamp to datetime for easier comparison
        if isinstance(event['timestamp'], str):
            try:
                event['_timestamp_dt'] = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
            except:
                event['_timestamp_dt'] = datetime.utcnow()
        
        # Add to window
        self.event_windows[event_type].append(event)
        self.stats['total_events_stored'] += 1
        
        # Cleanup old events
        self._cleanup_expired_events()
    
    def get_events_by_type(self, event_type: str, window_seconds: Optional[int] = None) -> List[Dict]:
        """
        Get events of specific type within time window
        
        Args:
            event_type: Type of events to retrieve
            window_seconds: Time window in seconds (None for all events)
            
        Returns:
            List of events
        """
        events = list(self.event_windows.get(event_type, []))
        
        if window_seconds is None:
            return events
        
        # Filter by time window
        cutoff_time = datetime.utcnow() - timedelta(seconds=window_seconds)
        filtered = []
        
        for event in events:
            event_time = event.get('_timestamp_dt', datetime.utcnow())
            if event_time >= cutoff_time:
                filtered.append(event)
        
        return filtered
    
    def get_events_by_field(self, event_type: str, field: str, value: Any, 
                           window_seconds: Optional[int] = None) -> List[Dict]:
        """
        Get events matching specific field value
        
        Args:
            event_type: Type of events to search
            field: Field name to match
            value: Field value to match
            window_seconds: Time window in seconds
            
        Returns:
            List of matching events
        """
        events = self.get_events_by_type(event_type, window_seconds)
        return [e for e in events if e.get(field) == value]
    
    def count_events(self, event_type: str, window_seconds: Optional[int] = None) -> int:
        """
        Count events of specific type in time window
        
        Args:
            event_type: Type of events to count
            window_seconds: Time window in seconds
            
        Returns:
            Event count
        """
        return len(self.get_events_by_type(event_type, window_seconds))
    
    def get_unique_values(self, event_type: str, field: str, 
                         window_seconds: Optional[int] = None) -> set:
        """
        Get unique values for a field across events
        
        Args:
            event_type: Type of events to search
            field: Field name
            window_seconds: Time window in seconds
            
        Returns:
            Set of unique values
        """
        events = self.get_events_by_type(event_type, window_seconds)
        return {e.get(field) for e in events if field in e}
    
    def _cleanup_expired_events(self):
        """Remove events older than retention window"""
        cutoff_time = datetime.utcnow() - timedelta(seconds=self.retention_window)
        
        for event_type, events in self.event_windows.items():
            original_count = len(events)
            
            # Remove expired events from the left (oldest)
            while events and events[0].get('_timestamp_dt', datetime.utcnow()) < cutoff_time:
                events.popleft()
                self.stats['events_expired'] += 1
            
            # Update stats
            if len(events) < original_count:
                expired = original_count - len(events)
                # Already counted in events_expired
        
        # Update active windows count
        self.stats['windows_active'] = len([w for w in self.event_windows.values() if len(w) > 0])
    
    def get_correlation_state(self, correlation_id: str) -> Optional[Dict]:
        """
        Get state for specific correlation
        
        Args:
            correlation_id: Correlation identifier
            
        Returns:
            Correlation state or None
        """
        return self.correlation_state.get(correlation_id)
    
    def set_correlation_state(self, correlation_id: str, state: Dict):
        """
        Set state for specific correlation
        
        Args:
            correlation_id: Correlation identifier
            state: State dictionary
        """
        self.correlation_state[correlation_id] = {
            **state,
            'updated_at': datetime.utcnow().isoformat()
        }
    
    def clear_correlation_state(self, correlation_id: str):
        """
        Clear state for specific correlation
        
        Args:
            correlation_id: Correlation identifier
        """
        if correlation_id in self.correlation_state:
            del self.correlation_state[correlation_id]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get state manager statistics"""
        total_events = sum(len(events) for events in self.event_windows.values())
        
        return {
            **self.stats,
            'current_events_stored': total_events,
            'event_types_tracked': len(self.event_windows),
            'correlation_states_active': len(self.correlation_state)
        }
    
    def get_window_summary(self) -> Dict[str, int]:
        """Get summary of events in each window"""
        return {
            event_type: len(events)
            for event_type, events in self.event_windows.items()
        }
