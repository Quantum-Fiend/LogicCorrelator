"""
LogicCorrelator - Event Aggregator
Central event aggregation and normalization service
"""

import json
import sys
import time
import threading
import queue
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import yaml
import subprocess

from event_schema import EventValidator
from state_manager import StateManager


class EventAggregator:
    """Central event aggregation and processing service"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the event aggregator"""
        self.config = self._load_config(config_path)
        self.event_queue = queue.Queue(maxsize=self.config['collection']['buffer_size'])
        self.validator = EventValidator("config/event_schema.json")
        self.state_manager = StateManager(self.config)
        
        self.running = False
        self.stats = {
            'events_received': 0,
            'events_validated': 0,
            'events_rejected': 0,
            'events_forwarded': 0
        }
        
        # Lua engine process
        self.lua_engine = None
        
        print("[AGGREGATOR] Event Aggregator initialized")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load YAML configuration"""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        print(f"[AGGREGATOR] Configuration loaded from {config_path}")
        return config
    
    def start(self):
        """Start the aggregator service"""
        self.running = True
        print("[AGGREGATOR] Starting event aggregator...")
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self._process_events, daemon=True)
        self.processing_thread.start()
        
        # Start Lua correlation engine
        self._start_lua_engine()
        
        print("[AGGREGATOR] Event aggregator started")
    
    def stop(self):
        """Stop the aggregator service"""
        print("[AGGREGATOR] Stopping event aggregator...")
        self.running = False
        
        if self.lua_engine:
            self.lua_engine.terminate()
            self.lua_engine.wait()
        
        print("[AGGREGATOR] Event aggregator stopped")
    
    def _start_lua_engine(self):
        """Start the Lua correlation engine as a subprocess"""
        try:
            # In production, this would start the Lua engine
            # For now, we'll simulate it
            print("[AGGREGATOR] Lua correlation engine interface ready")
        except Exception as e:
            print(f"[AGGREGATOR] Error starting Lua engine: {e}")
    
    def receive_event(self, event: Dict[str, Any]) -> bool:
        """
        Receive and queue an event
        
        Args:
            event: Raw event dictionary
            
        Returns:
            True if event was queued, False otherwise
        """
        self.stats['events_received'] += 1
        
        try:
            # Add timestamp if not present
            if 'timestamp' not in event:
                event['timestamp'] = datetime.utcnow().isoformat()
            
            # Queue the event
            self.event_queue.put(event, block=False)
            return True
            
        except queue.Full:
            print("[AGGREGATOR] Event queue full, dropping event")
            self.stats['events_rejected'] += 1
            return False
    
    def _process_events(self):
        """Background thread to process queued events"""
        print("[AGGREGATOR] Event processing thread started")
        
        batch = []
        batch_size = self.config['performance']['batch_size']
        
        while self.running:
            try:
                # Get event from queue with timeout
                event = self.event_queue.get(timeout=1.0)
                
                # Normalize and validate
                normalized_event = self._normalize_event(event)
                
                if self.validator.validate(normalized_event):
                    self.stats['events_validated'] += 1
                    batch.append(normalized_event)
                    
                    # Update state manager
                    self.state_manager.add_event(normalized_event)
                    
                    # Process batch when full
                    if len(batch) >= batch_size:
                        self._forward_batch(batch)
                        batch = []
                else:
                    self.stats['events_rejected'] += 1
                    print(f"[AGGREGATOR] Invalid event rejected: {normalized_event.get('type', 'unknown')}")
                
            except queue.Empty:
                # Process any remaining events in batch
                if batch:
                    self._forward_batch(batch)
                    batch = []
                continue
            except Exception as e:
                print(f"[AGGREGATOR] Error processing event: {e}")
                self.stats['events_rejected'] += 1
    
    def _normalize_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize event to standard schema
        
        Args:
            event: Raw event
            
        Returns:
            Normalized event
        """
        normalized = event.copy()
        
        # Ensure required fields
        if 'type' not in normalized:
            # Try to infer type from event content
            normalized['type'] = self._infer_event_type(event)
        
        # Normalize timestamp to ISO8601
        if 'timestamp' in normalized:
            if isinstance(normalized['timestamp'], (int, float)):
                normalized['timestamp'] = datetime.fromtimestamp(normalized['timestamp']).isoformat()
        
        # Add metadata
        normalized['_metadata'] = {
            'received_at': datetime.utcnow().isoformat(),
            'source': event.get('_source', 'unknown')
        }
        
        return normalized
    
    def _infer_event_type(self, event: Dict[str, Any]) -> str:
        """Infer event type from event fields"""
        # Simple heuristics
        if 'auth' in str(event).lower():
            if 'fail' in str(event).lower():
                return 'auth_fail'
            return 'auth_success'
        elif 'process' in str(event).lower():
            return 'process_start'
        elif 'network' in str(event).lower() or 'connection' in str(event).lower():
            return 'network_connect'
        elif 'file' in str(event).lower():
            return 'file_access'
        
        return 'unknown'
    
    def _forward_batch(self, batch: List[Dict[str, Any]]):
        """
        Forward batch of events to Lua correlation engine
        
        Args:
            batch: List of normalized events
        """
        try:
            # In production, this would send to Lua engine via IPC
            # For now, we'll just log
            for event in batch:
                self._forward_to_lua(event)
                self.stats['events_forwarded'] += 1
            
            if len(batch) > 0:
                print(f"[AGGREGATOR] Forwarded batch of {len(batch)} events to correlation engine")
        
        except Exception as e:
            print(f"[AGGREGATOR] Error forwarding batch: {e}")
    
    def _forward_to_lua(self, event: Dict[str, Any]):
        """
        Forward single event to Lua engine
        
        Args:
            event: Normalized event
        """
        # In production, this would use named pipes, sockets, or FFI
        # For demonstration, we'll write to a file that Lua can read
        try:
            event_json = json.dumps(event)
            # Could write to named pipe or socket here
            pass
        except Exception as e:
            print(f"[AGGREGATOR] Error forwarding event: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get aggregator statistics"""
        return {
            **self.stats,
            'queue_size': self.event_queue.qsize(),
            'state_manager_stats': self.state_manager.get_stats()
        }
    
    def print_stats(self):
        """Print statistics to console"""
        stats = self.get_stats()
        print("\n" + "="*60)
        print("EVENT AGGREGATOR STATISTICS")
        print("="*60)
        print(f"Events Received:   {stats['events_received']}")
        print(f"Events Validated:  {stats['events_validated']}")
        print(f"Events Rejected:   {stats['events_rejected']}")
        print(f"Events Forwarded:  {stats['events_forwarded']}")
        print(f"Queue Size:        {stats['queue_size']}")
        print("="*60 + "\n")


def main():
    """Main entry point for event aggregator"""
    print("="*60)
    print("LogicCorrelator - Event Aggregator")
    print("="*60)
    
    # Create aggregator
    aggregator = EventAggregator()
    
    # Start service
    aggregator.start()
    
    try:
        # Listen for events on stdin
        print("[AGGREGATOR] Listening for events on stdin (JSON format)...")
        print("[AGGREGATOR] Press Ctrl+C to stop")
        
        stats_interval = 30  # Print stats every 30 seconds
        last_stats_time = time.time()
        
        for line in sys.stdin:
            try:
                # Parse JSON event
                event = json.loads(line.strip())
                aggregator.receive_event(event)
                
                # Print stats periodically
                if time.time() - last_stats_time >= stats_interval:
                    aggregator.print_stats()
                    last_stats_time = time.time()
                    
            except json.JSONDecodeError:
                print(f"[AGGREGATOR] Invalid JSON: {line[:100]}")
            except Exception as e:
                print(f"[AGGREGATOR] Error: {e}")
    
    except KeyboardInterrupt:
        print("\n[AGGREGATOR] Received interrupt signal")
    
    finally:
        aggregator.stop()
        aggregator.print_stats()
        print("[AGGREGATOR] Shutdown complete")


if __name__ == "__main__":
    main()
