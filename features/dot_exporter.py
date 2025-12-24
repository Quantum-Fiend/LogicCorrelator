"""
LogicCorrelator - DOT Graph Exporter
Exports correlation decision paths to GraphViz DOT format
"""

import subprocess
from typing import Dict, List, Any, Optional
from pathlib import Path


class DOTExporter:
    """Exports correlation graphs to DOT format"""
    
    def __init__(self, output_dir: str = "graphs"):
        """
        Initialize DOT exporter
        
        Args:
            output_dir: Directory to save exported graphs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        print(f"[DOT_EXPORTER] Initialized, output directory: {self.output_dir}")
    
    def export_decision_graph(self, correlation: Dict[str, Any], filename: str) -> Optional[str]:
        """
        Export correlation decision graph to DOT format
        
        Args:
            correlation: Correlation data with decision path
            filename: Output filename (without extension)
            
        Returns:
            Path to generated DOT file, or None on error
        """
        try:
            dot_content = self._generate_dot(correlation)
            
            # Save DOT file
            dot_path = self.output_dir / f"{filename}.dot"
            with open(dot_path, 'w') as f:
                f.write(dot_content)
            
            print(f"[DOT_EXPORTER] Exported DOT file: {dot_path}")
            
            # Try to render to PNG if GraphViz is available
            self._render_graph(dot_path, filename)
            
            return str(dot_path)
            
        except Exception as e:
            print(f"[DOT_EXPORTER] Error exporting graph: {e}")
            return None
    
    def _generate_dot(self, correlation: Dict[str, Any]) -> str:
        """
        Generate DOT format string from correlation data
        
        Args:
            correlation: Correlation data
            
        Returns:
            DOT format string
        """
        lines = [
            "digraph CorrelationGraph {",
            "    rankdir=LR;",
            "    node [shape=box, style=rounded, fontname=\"Arial\"];",
            "    edge [fontname=\"Arial\"];",
            ""
        ]
        
        # Add rule node
        rule_id = correlation.get('rule_id', 'UNKNOWN')
        rule_name = correlation.get('rule_name', 'Unknown Rule')
        lines.append(f'    rule [label="{rule_id}\\n{rule_name}", fillcolor=lightblue, style=filled];')
        lines.append("")
        
        # Add condition nodes
        conditions = correlation.get('conditions_evaluated', [])
        for i, cond in enumerate(conditions):
            cond_type = cond.get('condition', {}).get('type', 'unknown')
            matched = cond.get('result', False)
            event_count = len(cond.get('matched_events', []))
            
            color = "lightgreen" if matched else "lightcoral"
            label = f"Condition {i+1}\\n{cond_type}\\nEvents: {event_count}"
            
            lines.append(f'    cond{i} [label="{label}", fillcolor={color}, style=filled];')
            
            # Add edge from previous node
            if i == 0:
                lines.append(f'    rule -> cond{i};')
            else:
                lines.append(f'    cond{i-1} -> cond{i};')
        
        lines.append("")
        
        # Add result node
        matched = correlation.get('matched', False)
        result_color = "green" if matched else "red"
        result_label = "MATCHED\\nAlert Generated" if matched else "NO MATCH"
        lines.append(f'    result [label="{result_label}", fillcolor={result_color}, style=filled, shape=ellipse];')
        
        if conditions:
            lines.append(f'    cond{len(conditions)-1} -> result;')
        
        # Add event nodes (optional, for detailed view)
        if correlation.get('show_events', False):
            lines.append("")
            lines.append("    // Event nodes")
            for i, cond in enumerate(conditions):
                for j, event in enumerate(cond.get('matched_events', [])[:3]):  # Limit to 3 events
                    event_label = f"{event.get('type', 'unknown')}\\n{event.get('timestamp', '')}"
                    lines.append(f'    event{i}_{j} [label="{event_label}", shape=note, fillcolor=lightyellow, style=filled];')
                    lines.append(f'    cond{i} -> event{i}_{j} [style=dashed];')
        
        lines.append("}")
        
        return '\n'.join(lines)
    
    def _render_graph(self, dot_path: Path, filename: str):
        """
        Render DOT file to PNG using GraphViz
        
        Args:
            dot_path: Path to DOT file
            filename: Base filename
        """
        try:
            png_path = self.output_dir / f"{filename}.png"
            
            # Try to run dot command
            result = subprocess.run(
                ['dot', '-Tpng', str(dot_path), '-o', str(png_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"[DOT_EXPORTER] Rendered PNG: {png_path}")
            else:
                print(f"[DOT_EXPORTER] GraphViz not available or error rendering")
                
        except FileNotFoundError:
            print("[DOT_EXPORTER] GraphViz 'dot' command not found - install GraphViz to render images")
        except subprocess.TimeoutExpired:
            print("[DOT_EXPORTER] GraphViz rendering timed out")
        except Exception as e:
            print(f"[DOT_EXPORTER] Error rendering graph: {e}")
    
    def export_correlation_chain(self, events: List[Dict], rule_name: str, filename: str) -> Optional[str]:
        """
        Export a simple correlation chain visualization
        
        Args:
            events: List of correlated events
            rule_name: Name of the rule that matched
            filename: Output filename
            
        Returns:
            Path to DOT file
        """
        lines = [
            "digraph CorrelationChain {",
            "    rankdir=LR;",
            "    node [shape=box, fontname=\"Arial\"];",
            ""
        ]
        
        # Add rule node
        lines.append(f'    rule [label="{rule_name}", shape=ellipse, fillcolor=lightblue, style=filled];')
        
        # Add event nodes
        for i, event in enumerate(events):
            event_type = event.get('type', 'unknown')
            timestamp = event.get('timestamp', '')[:19]  # Truncate timestamp
            user = event.get('user', 'N/A')
            
            label = f"{event_type}\\n{timestamp}\\nUser: {user}"
            lines.append(f'    event{i} [label="{label}", fillcolor=lightyellow, style=filled];')
            
            if i == 0:
                lines.append(f'    rule -> event{i};')
            else:
                lines.append(f'    event{i-1} -> event{i};')
        
        lines.append("}")
        
        dot_content = '\n'.join(lines)
        
        # Save file
        dot_path = self.output_dir / f"{filename}.dot"
        with open(dot_path, 'w') as f:
            f.write(dot_content)
        
        print(f"[DOT_EXPORTER] Exported correlation chain: {dot_path}")
        
        # Render
        self._render_graph(dot_path, filename)
        
        return str(dot_path)
