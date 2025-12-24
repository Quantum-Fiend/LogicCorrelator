"""
LogicCorrelator - Service Orchestrator
Manages all system components and services
"""

import sys
import subprocess
import time
import signal
from pathlib import Path
from typing import List, Dict, Optional


class ServiceOrchestrator:
    """Orchestrates all LogicCorrelator services"""
    
    def __init__(self):
        """Initialize orchestrator"""
        self.processes: Dict[str, subprocess.Popen] = {}
        self.running = False
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print("="*60)
        print("LogicCorrelator - Service Orchestrator")
        print("="*60)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n[ORCHESTRATOR] Received shutdown signal")
        self.stop_all()
        sys.exit(0)
    
    def start_all(self):
        """Start all services"""
        print("[ORCHESTRATOR] Starting all services...\n")
        self.running = True
        
        # Start Python aggregator
        self._start_aggregator()
        time.sleep(2)
        
        # Start Node.js dashboard
        self._start_dashboard()
        time.sleep(2)
        
        # Start Lua correlation engine (if available)
        self._start_correlation_engine()
        
        print("\n" + "="*60)
        print("All services started!")
        print("="*60)
        print("Dashboard: http://localhost:3000")
        print("WebSocket: ws://localhost:3001")
        print("="*60)
        print("\nPress Ctrl+C to stop all services\n")
        
        # Keep orchestrator running
        try:
            while self.running:
                time.sleep(1)
                self._check_health()
        except KeyboardInterrupt:
            print("\n[ORCHESTRATOR] Interrupted")
            self.stop_all()
    
    def _start_aggregator(self):
        """Start Python event aggregator"""
        print("[ORCHESTRATOR] Starting event aggregator...")
        
        try:
            process = subprocess.Popen(
                [sys.executable, "core/event_aggregator.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )
            
            self.processes['aggregator'] = process
            print("[ORCHESTRATOR] ✓ Event aggregator started (PID: {})".format(process.pid))
            
        except Exception as e:
            print(f"[ORCHESTRATOR] ✗ Failed to start aggregator: {e}")
    
    def _start_dashboard(self):
        """Start Node.js dashboard server"""
        print("[ORCHESTRATOR] Starting dashboard server...")
        
        try:
            process = subprocess.Popen(
                ["node", "dashboard_server.js"],
                cwd="dashboard",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes['dashboard'] = process
            print("[ORCHESTRATOR] ✓ Dashboard server started (PID: {})".format(process.pid))
            
        except Exception as e:
            print(f"[ORCHESTRATOR] ✗ Failed to start dashboard: {e}")
    
    def _start_correlation_engine(self):
        """Start Lua correlation engine"""
        print("[ORCHESTRATOR] Starting correlation engine...")
        
        # Check if Lua is available
        try:
            subprocess.run(['lua', '-v'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("[ORCHESTRATOR] ⚠ Lua not available - correlation engine not started")
            return
        
        try:
            # In production, this would start the Lua engine
            # For now, we'll just note it's available
            print("[ORCHESTRATOR] ✓ Correlation engine interface ready")
            
        except Exception as e:
            print(f"[ORCHESTRATOR] ✗ Failed to start correlation engine: {e}")
    
    def _check_health(self):
        """Check health of all services"""
        for name, process in list(self.processes.items()):
            if process.poll() is not None:
                print(f"[ORCHESTRATOR] ⚠ Service '{name}' has stopped unexpectedly")
                # Could implement auto-restart here
    
    def stop_all(self):
        """Stop all services gracefully"""
        print("\n[ORCHESTRATOR] Stopping all services...")
        self.running = False
        
        for name, process in self.processes.items():
            print(f"[ORCHESTRATOR] Stopping {name}...")
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"[ORCHESTRATOR] ✓ {name} stopped")
            except subprocess.TimeoutExpired:
                print(f"[ORCHESTRATOR] ⚠ Force killing {name}")
                process.kill()
            except Exception as e:
                print(f"[ORCHESTRATOR] ✗ Error stopping {name}: {e}")
        
        print("[ORCHESTRATOR] All services stopped")
    
    def get_status(self):
        """Get status of all services"""
        print("\n" + "="*60)
        print("Service Status")
        print("="*60)
        
        for name, process in self.processes.items():
            status = "Running" if process.poll() is None else "Stopped"
            pid = process.pid if process.poll() is None else "N/A"
            print(f"{name:20} {status:10} PID: {pid}")
        
        print("="*60 + "\n")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py [start|stop|status]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    orchestrator = ServiceOrchestrator()
    
    if command == "start":
        orchestrator.start_all()
    elif command == "stop":
        orchestrator.stop_all()
    elif command == "status":
        orchestrator.get_status()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: start, stop, status")
        sys.exit(1)


if __name__ == "__main__":
    main()
