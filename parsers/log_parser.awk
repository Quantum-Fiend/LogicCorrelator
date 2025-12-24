#!/usr/bin/awk -f
#
# LogicCorrelator - High-Speed Log Parser (AWK)
# Parses various log formats and outputs normalized JSON events
#

BEGIN {
    # Initialize
    FS = " "
    OFS = ""
    
    # Timestamp format
    timestamp_format = strftime("%Y-%m-%dT%H:%M:%SZ", systime())
    
    # Print header
    print "[AWK_PARSER] Log parser started" > "/dev/stderr"
}

# Function to generate ISO8601 timestamp
function get_timestamp() {
    return strftime("%Y-%m-%dT%H:%M:%SZ", systime())
}

# Function to escape JSON strings
function json_escape(str) {
    gsub(/"/, "\\\"", str)
    gsub(/\\/, "\\\\", str)
    gsub(/\n/, "\\n", str)
    gsub(/\r/, "\\r", str)
    gsub(/\t/, "\\t", str)
    return str
}

# Function to output JSON event
function output_json(type, fields) {
    printf "{\"type\":\"%s\",\"timestamp\":\"%s\"", type, get_timestamp()
    print fields
    print ",\"_source\":\"awk_parser\"}"
}

# Parse SSH authentication logs (auth.log / secure)
/sshd.*Failed password/ {
    user = ""
    ip = ""
    
    # Extract user
    for (i = 1; i <= NF; i++) {
        if ($i == "for") {
            if ($(i+1) == "invalid") {
                user = $(i+3)
            } else {
                user = $(i+1)
            }
        }
        if ($i == "from") {
            ip = $(i+1)
        }
    }
    
    if (user != "" && ip != "") {
        fields = sprintf(",\"user\":\"%s\",\"source_ip\":\"%s\",\"service\":\"ssh\",\"reason\":\"invalid_password\"", 
                        json_escape(user), json_escape(ip))
        output_json("auth_fail", fields)
    }
}

/sshd.*Accepted password|sshd.*Accepted publickey/ {
    user = ""
    ip = ""
    
    for (i = 1; i <= NF; i++) {
        if ($i == "for") {
            user = $(i+1)
        }
        if ($i == "from") {
            ip = $(i+1)
        }
    }
    
    if (user != "" && ip != "") {
        fields = sprintf(",\"user\":\"%s\",\"source_ip\":\"%s\",\"service\":\"ssh\"", 
                        json_escape(user), json_escape(ip))
        output_json("auth_success", fields)
    }
}

# Parse Apache/Nginx access logs (Common Log Format)
# Format: IP - - [timestamp] "METHOD /path HTTP/1.1" status size
/^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+ .* ".*" [0-9]+ [0-9]+/ {
    ip = $1
    method = ""
    path = ""
    status = $(NF-1)
    size = $NF
    
    # Extract HTTP method and path
    for (i = 1; i <= NF; i++) {
        if ($i ~ /^"(GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH)/) {
            method = substr($i, 2)
            path = $(i+1)
            break
        }
    }
    
    # Detect suspicious patterns
    if (path ~ /\.\.|admin|wp-admin|phpmyadmin|\.php|\.asp|\.jsp|exec|cmd|shell/) {
        fields = sprintf(",\"source_ip\":\"%s\",\"method\":\"%s\",\"path\":\"%s\",\"status\":%s,\"size\":%s", 
                        ip, method, json_escape(path), status, size)
        output_json("web_access_suspicious", fields)
    }
}

# Parse firewall logs (iptables format)
/IN=.*OUT=.*SRC=.*DST=.*PROTO=/ {
    src_ip = ""
    dst_ip = ""
    src_port = ""
    dst_port = ""
    proto = ""
    
    for (i = 1; i <= NF; i++) {
        if ($i ~ /^SRC=/) {
            src_ip = substr($i, 5)
        }
        if ($i ~ /^DST=/) {
            dst_ip = substr($i, 5)
        }
        if ($i ~ /^PROTO=/) {
            proto = tolower(substr($i, 7))
        }
        if ($i ~ /^SPT=/) {
            src_port = substr($i, 5)
        }
        if ($i ~ /^DPT=/) {
            dst_port = substr($i, 5)
        }
    }
    
    if (src_ip != "" && dst_ip != "") {
        fields = sprintf(",\"source_ip\":\"%s\",\"source_port\":%s,\"dest_ip\":\"%s\",\"dest_port\":%s,\"protocol\":\"%s\",\"direction\":\"outbound\"", 
                        src_ip, src_port, dst_ip, dst_port, proto)
        output_json("network_connect", fields)
    }
}

# Parse syslog process start messages
/kernel:.*process.*started|systemd.*Started/ {
    process_name = ""
    pid = ""
    
    # Extract process information
    for (i = 1; i <= NF; i++) {
        if ($i ~ /\[.*\]/) {
            pid = $i
            gsub(/[\[\]]/, "", pid)
        }
    }
    
    # Get process name from context
    if ($0 ~ /Started/) {
        for (i = 1; i <= NF; i++) {
            if ($i == "Started") {
                process_name = $(i+1)
                break
            }
        }
    }
    
    if (process_name != "") {
        fields = sprintf(",\"process_name\":\"%s\",\"pid\":%s,\"user\":\"system\"", 
                        json_escape(process_name), pid)
        output_json("process_start", fields)
    }
}

# Parse sudo commands
/sudo:.*COMMAND=/ {
    user = ""
    command = ""
    
    for (i = 1; i <= NF; i++) {
        if ($i ~ /^USER=/) {
            user = substr($i, 6)
        }
        if ($i ~ /^COMMAND=/) {
            # Get rest of line as command
            command = substr($0, index($0, "COMMAND=") + 8)
            break
        }
    }
    
    if (user != "" && command != "") {
        fields = sprintf(",\"user\":\"%s\",\"command\":\"%s\",\"method\":\"sudo\"", 
                        json_escape(user), json_escape(command))
        output_json("privilege_escalation", fields)
    }
}

# Parse failed sudo attempts
/sudo:.*authentication failure/ {
    user = ""
    
    for (i = 1; i <= NF; i++) {
        if ($i ~ /^user=/) {
            user = substr($i, 6)
            break
        }
    }
    
    if (user != "") {
        fields = sprintf(",\"user\":\"%s\",\"method\":\"sudo\",\"success\":false", 
                        json_escape(user))
        output_json("privilege_escalation", fields)
    }
}

# Parse DNS queries (if available)
/query\[A\]|query\[AAAA\]/ {
    domain = ""
    query_type = ""
    
    for (i = 1; i <= NF; i++) {
        if ($i ~ /query\[.*\]/) {
            query_type = $i
            gsub(/query\[|\]/, "", query_type)
            domain = $(i+1)
            break
        }
    }
    
    # Detect suspicious domains
    if (domain ~ /\.tk$|\.ml$|\.ga$|\.cf$|pastebin|ngrok|duckdns/) {
        fields = sprintf(",\"domain\":\"%s\",\"query_type\":\"%s\"", 
                        json_escape(domain), query_type)
        output_json("dns_query_suspicious", fields)
    }
}

# Generic error/warning detection
/ERROR|CRITICAL|FATAL|ALERT/ {
    severity = ""
    message = $0
    
    if ($0 ~ /ERROR/) severity = "ERROR"
    else if ($0 ~ /CRITICAL/) severity = "CRITICAL"
    else if ($0 ~ /FATAL/) severity = "FATAL"
    else if ($0 ~ /ALERT/) severity = "ALERT"
    
    fields = sprintf(",\"severity\":\"%s\",\"message\":\"%s\"", 
                    severity, json_escape(message))
    output_json("system_error", fields)
}

END {
    print "[AWK_PARSER] Log parser finished" > "/dev/stderr"
}
