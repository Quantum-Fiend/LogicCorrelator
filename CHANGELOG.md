# Changelog

All notable changes to LogicCorrelator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-24

### 🎉 Initial Release

#### Added

**Core Engine**
- Lua-based correlation engine with temporal logic
- Rule DSL for defining correlation patterns
- Event state management with sliding windows
- Explainable decision graphs
- Rule conflict resolution (priority, severity, confidence)

**Event Collection**
- Bash collector for Linux systems (auth, process, network, file events)
- PowerShell collector for Windows (security events, processes, registry)
- AWK high-speed log parser (syslog, Apache, iptables, DNS)
- Event normalization and validation pipeline

**Python Aggregation Layer**
- Event aggregator with queuing and batching
- JSON schema validation
- State manager for temporal windows
- Event persistence and expiration

**Dashboard**
- Node.js/Express server with WebSocket support
- Real-time event streaming
- Interactive correlation graph visualization
- Alert timeline with severity filtering
- Performance metrics dashboard
- Premium dark mode UI with glassmorphism

**Advanced Features**
- DOT graph export for decision path visualization
- MITRE ATT&CK technique mapping
- ATT&CK Navigator layer generation
- Rule simulation mode
- Performance profiling

**Correlation Rules**
- Credential attack detection (stuffing, spraying, brute force)
- Lateral movement detection (SMB, WMI, RDP, Pass-the-Hash)
- Data exfiltration detection (DNS tunneling, cloud uploads, archival)
- Privilege escalation detection (UAC bypass, token impersonation)

**Configuration**
- YAML-based system configuration
- JSON event schema definitions
- Windows Terminal SOC workflow layout
- Flexible rule definitions in YAML

**Build System**
- Unified Makefile for multi-language orchestration
- Service orchestrator with health monitoring
- Automated dependency installation
- Test suite integration

**Documentation**
- Comprehensive README with examples
- Architecture documentation
- Rule authoring guide
- Contributing guidelines
- MIT License

#### Technical Details

**Languages Used**
1. Lua - Correlation engine and rule evaluation
2. Python - Event aggregation and state management
3. Bash - Linux event collection
4. PowerShell - Windows event collection
5. JavaScript (Node.js) - Dashboard server
6. YAML - Configuration and rule definitions
7. JSON - Event schemas and data contracts
8. AWK - High-speed log parsing
9. Windows Terminal JSON - SOC workflow configuration

**Architecture Highlights**
- Event-driven architecture with WebSocket streaming
- Stateful correlation across temporal windows
- Explainable AI approach (logic-based, not ML)
- MITRE ATT&CK framework integration
- Multi-stage attack pattern detection

**Performance**
- Handles 1000+ events per second
- Sub-second correlation latency
- Efficient memory management with event expiration
- Batch processing for optimal throughput

### 🔒 Security

- Input validation on all event sources
- Schema-based event validation
- Secure WebSocket connections
- No sensitive data in logs

### 📊 Metrics

- **Lines of Code**: ~5000+
- **Correlation Rules**: 20+ pre-built rules
- **Event Types**: 7 core event types
- **MITRE Techniques**: 15+ mapped techniques
- **Test Coverage**: Integration tests included

---

## [Unreleased]

### Planned Features
- eBPF-based event collection for Linux
- Sysmon integration for Windows
- Distributed deployment support
- Cloud-native architecture (Kubernetes)
- Rule marketplace
- Additional MITRE ATT&CK coverage
- Machine learning anomaly detection (optional layer)

---

## Version History

- **1.0.0** (2025-12-24) - Initial release

---

[1.0.0]: https://github.com/yourusername/LogicCorrelator/releases/tag/v1.0.0
