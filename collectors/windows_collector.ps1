# LogicCorrelator - Windows Event Collector
# Collects Windows security and system events, outputs normalized JSON

param(
    [int]$PollInterval = 5,
    [switch]$Verbose
)

# Configuration
$ErrorActionPreference = "Continue"

# Event IDs to monitor
$SecurityEventIDs = @{
    4624 = "Successful Logon"
    4625 = "Failed Logon"
    4688 = "Process Creation"
    4689 = "Process Termination"
    4720 = "User Account Created"
    4726 = "User Account Deleted"
    4732 = "Member Added to Security-Enabled Local Group"
    5140 = "Network Share Accessed"
    5156 = "Windows Filtering Platform Connection"
}

# Logging functions
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    
    $color = switch ($Level) {
        "ERROR" { "Red" }
        "SUCCESS" { "Green" }
        "WARNING" { "Yellow" }
        default { "Cyan" }
    }
    
    Write-Host "[COLLECTOR] $Message" -ForegroundColor $color
}

# Get ISO8601 timestamp
function Get-Timestamp {
    return (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}

# Convert event to JSON
function ConvertTo-EventJson {
    param($Event)
    
    return $Event | ConvertTo-Json -Compress
}

# Collect authentication events
function Get-AuthenticationEvents {
    $startTime = (Get-Date).AddSeconds(-$PollInterval)
    
    # Failed logons (Event ID 4625)
    Get-WinEvent -FilterHashtable @{
        LogName = 'Security'
        ID = 4625
        StartTime = $startTime
    } -ErrorAction SilentlyContinue | ForEach-Object {
        $event = $_
        
        $user = $event.Properties[5].Value
        $sourceIP = $event.Properties[19].Value
        $reason = $event.Properties[8].Value
        
        $eventObj = @{
            type = "auth_fail"
            timestamp = Get-Timestamp
            user = $user
            source_ip = $sourceIP
            reason = $reason
            service = "Windows"
            event_id = 4625
            _source = "windows_collector"
        }
        
        Write-Output (ConvertTo-EventJson $eventObj)
    }
    
    # Successful logons (Event ID 4624)
    Get-WinEvent -FilterHashtable @{
        LogName = 'Security'
        ID = 4624
        StartTime = $startTime
    } -ErrorAction SilentlyContinue | ForEach-Object {
        $event = $_
        
        $user = $event.Properties[5].Value
        $sourceIP = $event.Properties[18].Value
        $logonType = $event.Properties[8].Value
        
        # Filter out system/service logons
        if ($logonType -notin @(0, 3, 5)) {
            $eventObj = @{
                type = "auth_success"
                timestamp = Get-Timestamp
                user = $user
                source_ip = $sourceIP
                service = "Windows"
                logon_type = $logonType
                event_id = 4624
                _source = "windows_collector"
            }
            
            Write-Output (ConvertTo-EventJson $eventObj)
        }
    }
}

# Collect process creation events
function Get-ProcessEvents {
    $startTime = (Get-Date).AddSeconds(-$PollInterval)
    
    # Process creation (Event ID 4688)
    Get-WinEvent -FilterHashtable @{
        LogName = 'Security'
        ID = 4688
        StartTime = $startTime
    } -ErrorAction SilentlyContinue | ForEach-Object {
        $event = $_
        
        $processName = $event.Properties[5].Value
        $processId = $event.Properties[4].Value
        $commandLine = $event.Properties[8].Value
        $user = $event.Properties[1].Value
        $parentProcessName = $event.Properties[13].Value
        
        # Only report suspicious processes
        $suspiciousProcesses = @(
            'powershell.exe', 'cmd.exe', 'wmic.exe', 'psexec.exe',
            'net.exe', 'net1.exe', 'sc.exe', 'reg.exe', 'regedit.exe',
            'mshta.exe', 'rundll32.exe', 'regsvr32.exe', 'certutil.exe'
        )
        
        $baseName = Split-Path $processName -Leaf
        
        if ($baseName -in $suspiciousProcesses) {
            $eventObj = @{
                type = "process_start"
                timestamp = Get-Timestamp
                process_name = $baseName
                command_line = $commandLine
                pid = $processId
                user = $user
                parent_process = $parentProcessName
                executable_path = $processName
                event_id = 4688
                _source = "windows_collector"
            }
            
            Write-Output (ConvertTo-EventJson $eventObj)
        }
    }
}

# Collect network connection events
function Get-NetworkEvents {
    $startTime = (Get-Date).AddSeconds(-$PollInterval)
    
    # Windows Filtering Platform connections (Event ID 5156)
    Get-WinEvent -FilterHashtable @{
        LogName = 'Security'
        ID = 5156
        StartTime = $startTime
    } -ErrorAction SilentlyContinue | ForEach-Object {
        $event = $_
        
        $processId = $event.Properties[0].Value
        $direction = $event.Properties[2].Value
        $sourceIP = $event.Properties[3].Value
        $sourcePort = $event.Properties[4].Value
        $destIP = $event.Properties[5].Value
        $destPort = $event.Properties[6].Value
        $protocol = $event.Properties[7].Value
        
        # Get process name from PID
        $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
        $processName = if ($process) { $process.ProcessName } else { "unknown" }
        
        $directionStr = if ($direction -eq 0) { "inbound" } else { "outbound" }
        $protocolStr = switch ($protocol) {
            6 { "tcp" }
            17 { "udp" }
            1 { "icmp" }
            default { "unknown" }
        }
        
        $eventObj = @{
            type = "network_connect"
            timestamp = Get-Timestamp
            source_ip = $sourceIP
            source_port = $sourcePort
            dest_ip = $destIP
            dest_port = $destPort
            protocol = $protocolStr
            process_name = $processName
            direction = $directionStr
            event_id = 5156
            _source = "windows_collector"
        }
        
        Write-Output (ConvertTo-EventJson $eventObj)
    }
}

# Collect registry change events
function Get-RegistryEvents {
    # Monitor registry changes via Sysmon or audit logs
    # This is a placeholder - requires Sysmon or advanced auditing
    
    $startTime = (Get-Date).AddSeconds(-$PollInterval)
    
    # Would monitor Event IDs 12, 13, 14 from Sysmon if available
    # For now, we'll skip this unless Sysmon is installed
}

# Main collection loop
function Start-Collector {
    Write-Log "Windows Event Collector started" "SUCCESS"
    Write-Log "Collecting events every $PollInterval seconds"
    Write-Log "Press Ctrl+C to stop" "WARNING"
    
    while ($true) {
        try {
            # Collect all event types
            Get-AuthenticationEvents
            Get-ProcessEvents
            Get-NetworkEvents
            Get-RegistryEvents
            
            # Wait before next collection
            Start-Sleep -Seconds $PollInterval
            
        } catch {
            Write-Log "Error during collection: $_" "ERROR"
        }
    }
}

# Handle Ctrl+C gracefully
$null = Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action {
    Write-Log "Collector stopped" "WARNING"
}

# Start the collector
Start-Collector
