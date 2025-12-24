#!/bin/bash
#
# LogicCorrelator - Linux Event Collector
# Collects system events from Linux and outputs normalized JSON
#

set -euo pipefail

# Configuration
POLL_INTERVAL=5
OUTPUT_FORMAT="json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${CYAN}[COLLECTOR]${NC} $1" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" >&2
}

# Generate ISO8601 timestamp
timestamp() {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
}

# Collect authentication events
collect_auth_events() {
    local auth_log="/var/log/auth.log"
    
    if [[ ! -f "$auth_log" ]]; then
        auth_log="/var/log/secure"
    fi
    
    if [[ ! -f "$auth_log" ]]; then
        log_error "Auth log not found"
        return
    fi
    
    # Monitor for failed SSH logins
    tail -n 50 "$auth_log" | grep -i "failed password" | while read -r line; do
        # Parse log line
        local user=$(echo "$line" | grep -oP 'for (invalid user )?\K[^ ]+' | head -1)
        local ip=$(echo "$line" | grep -oP 'from \K[0-9.]+' | head -1)
        
        if [[ -n "$user" && -n "$ip" ]]; then
            cat <<EOF
{"type":"auth_fail","timestamp":"$(timestamp)","user":"$user","source_ip":"$ip","service":"ssh","reason":"invalid_password","_source":"linux_collector"}
EOF
        fi
    done
    
    # Monitor for successful SSH logins
    tail -n 50 "$auth_log" | grep -i "accepted password\|accepted publickey" | while read -r line; do
        local user=$(echo "$line" | grep -oP 'for \K[^ ]+' | head -1)
        local ip=$(echo "$line" | grep -oP 'from \K[0-9.]+' | head -1)
        
        if [[ -n "$user" && -n "$ip" ]]; then
            cat <<EOF
{"type":"auth_success","timestamp":"$(timestamp)","user":"$user","source_ip":"$ip","service":"ssh","_source":"linux_collector"}
EOF
        fi
    done
}

# Collect process events
collect_process_events() {
    # Monitor for new processes (requires root or specific permissions)
    # This is a simplified version - production would use auditd or eBPF
    
    # Get recently started processes
    ps aux --sort=-start_time | head -20 | tail -n +2 | while read -r line; do
        local user=$(echo "$line" | awk '{print $1}')
        local pid=$(echo "$line" | awk '{print $2}')
        local cmd=$(echo "$line" | awk '{for(i=11;i<=NF;i++) printf "%s ", $i; print ""}')
        local process_name=$(echo "$cmd" | awk '{print $1}' | xargs basename)
        
        # Only report suspicious processes
        if [[ "$process_name" =~ (bash|sh|python|perl|nc|netcat|nmap) ]]; then
            cat <<EOF
{"type":"process_start","timestamp":"$(timestamp)","process_name":"$process_name","command_line":"$cmd","pid":$pid,"user":"$user","_source":"linux_collector"}
EOF
        fi
    done
}

# Collect network events
collect_network_events() {
    # Monitor active network connections
    # Requires root or CAP_NET_ADMIN
    
    if command -v ss &> /dev/null; then
        # Use ss (modern)
        ss -tunap 2>/dev/null | grep ESTAB | while read -r line; do
            local proto=$(echo "$line" | awk '{print tolower($1)}')
            local local_addr=$(echo "$line" | awk '{print $5}')
            local remote_addr=$(echo "$line" | awk '{print $6}')
            local process=$(echo "$line" | grep -oP 'users:\(\(".*?"\)' | grep -oP '"\K[^"]+' | head -1)
            
            # Parse addresses
            local src_ip=$(echo "$local_addr" | cut -d: -f1)
            local src_port=$(echo "$local_addr" | rev | cut -d: -f1 | rev)
            local dest_ip=$(echo "$remote_addr" | cut -d: -f1)
            local dest_port=$(echo "$remote_addr" | rev | cut -d: -f1 | rev)
            
            # Determine direction (simplified)
            local direction="outbound"
            if [[ "$dest_port" =~ ^(22|80|443|3389)$ ]]; then
                direction="outbound"
            fi
            
            cat <<EOF
{"type":"network_connect","timestamp":"$(timestamp)","source_ip":"$src_ip","source_port":$src_port,"dest_ip":"$dest_ip","dest_port":$dest_port,"protocol":"$proto","process_name":"$process","direction":"$direction","_source":"linux_collector"}
EOF
        done
    fi
}

# Collect file access events
collect_file_events() {
    # Monitor sensitive file access
    # This would typically use inotify or auditd
    
    # Check for recent modifications to sensitive files
    local sensitive_paths=(
        "/etc/passwd"
        "/etc/shadow"
        "/etc/sudoers"
        "/root/.ssh"
        "/home/*/.ssh"
    )
    
    for path in "${sensitive_paths[@]}"; do
        if [[ -e "$path" ]]; then
            # Check if modified in last 5 minutes
            if [[ $(find "$path" -mmin -5 2>/dev/null | wc -l) -gt 0 ]]; then
                local user=$(stat -c '%U' "$path" 2>/dev/null || echo "unknown")
                cat <<EOF
{"type":"file_access","timestamp":"$(timestamp)","file_path":"$path","operation":"modify","user":"$user","_source":"linux_collector"}
EOF
            fi
        fi
    done
}

# Main collection loop
main() {
    log "Linux Event Collector started"
    log "Collecting events every ${POLL_INTERVAL} seconds"
    log "Press Ctrl+C to stop"
    
    while true; do
        # Collect all event types
        collect_auth_events
        collect_process_events
        collect_network_events
        collect_file_events
        
        # Wait before next collection
        sleep "$POLL_INTERVAL"
    done
}

# Handle Ctrl+C gracefully
trap 'log "Collector stopped"; exit 0' INT TERM

# Run main function
main
