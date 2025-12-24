# LogicCorrelator - Setup Guide

## 🚀 Quick Setup

### Prerequisites

Before installing LogicCorrelator, ensure you have:

- **Python 3.8+** (required)
- **Node.js 16+** (required)
- **Lua 5.3+** (optional, for correlation engine)
- **AWK** (optional, for log parsing)
- **GraphViz** (optional, for graph export)

### System Requirements

- **OS:** Windows, Linux, or macOS
- **RAM:** 2GB minimum, 4GB recommended
- **Disk:** 500MB for installation
- **Network:** Internet connection for dependency installation

---

## 📦 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/LogicCorrelator.git
cd LogicCorrelator
```

### Step 2: Install Dependencies

```bash
make install
```

This will:
- Install Python dependencies (PyYAML)
- Install Node.js dependencies (Express, WebSocket)
- Create necessary directories (logs, graphs)
- Validate Lua and AWK availability

### Step 3: Verify Installation

```bash
make check
```

This checks that all required components are installed.

---

## ⚙️ Configuration

### Main Configuration

Edit `config/config.yaml` to customize:

```yaml
# Event collection settings
collection:
  buffer_size: 1000
  retention_window: 3600
  poll_interval: 5

# Correlation engine settings
correlation:
  max_correlation_events: 10000
  evaluation_interval: 1

# Alert settings
alerts:
  min_severity: MEDIUM
  destinations:
    - type: console
    - type: dashboard
```

### Event Schema

Define custom event types in `config/event_schema.json`:

```json
{
  "event_types": {
    "custom_event": {
      "fields": {
        "timestamp": {"type": "string", "required": true},
        "custom_field": {"type": "string", "required": false}
      }
    }
  }
}
```

### Correlation Rules

Add custom rules in `rules/` directory:

```yaml
# rules/custom_rules.yaml
rules:
  - name: "My Custom Rule"
    id: "CUSTOM-001"
    severity: HIGH
    mitre_techniques:
      - T1110
    conditions:
      - type: auth_fail
        count: ">= 3"
        window: 60
    actions:
      - alert:
          message: "Custom alert message"
```

---

## 🎮 Running LogicCorrelator

### Start All Services

```bash
make start
```

This starts:
- Python event aggregator
- Lua correlation engine
- Node.js dashboard server

### Access Dashboard

Open your browser to:
```
http://localhost:3000
```

### Run in Demo Mode

To see sample events and alerts:

```bash
make demo
```

### Stop Services

```bash
make stop
```

---

## 🧪 Testing

### Validate Rules

```bash
python tests/rule_validator.py
```

### Run Integration Tests

```bash
python tests/integration_test.py
```

### Generate Test Events

```bash
# Random events
python tests/event_generator.py random

# Credential attack scenario
python tests/event_generator.py credential

# Lateral movement scenario
python tests/event_generator.py lateral
```

### Run Demo Scenarios

```bash
# Credential attack demo
python demo/credential_attack_demo.py

# Lateral movement demo
python demo/lateral_movement_demo.py
```

---

## 📊 Dashboard Usage

### Event Stream
- **Filter events** - Use search box or type dropdown
- **Pause stream** - Click pause button
- **Clear events** - Click trash icon

### Alerts
- **Filter by severity** - Click severity buttons
- **View details** - Expand alert cards
- **MITRE techniques** - Shown in alert details

### Correlation Graph
- **View correlations** - Automatically updated
- **Refresh** - Click refresh button
- **Export** - Use DOT exporter feature

### Performance Metrics
- **Events/sec** - Real-time throughput
- **Latency** - Correlation processing time
- **Detection rate** - Percentage of correlated events
- **Active rules** - Number of loaded rules

---

## 🔧 Troubleshooting

### Python Dependencies Not Installing

```bash
# Manually install
pip install pyyaml
```

### Node.js Dependencies Not Installing

```bash
# Navigate to dashboard directory
cd dashboard

# Install manually
npm install
```

### Dashboard Not Starting

Check if port 3000 is already in use:

```bash
# Windows
netstat -ano | findstr :3000

# Linux/Mac
lsof -i :3000
```

### Lua Not Found

Lua is optional. The system will work without it, but correlation engine features will be limited.

To install Lua:

**Windows:**
```bash
# Download from https://www.lua.org/download.html
```

**Linux:**
```bash
sudo apt-get install lua5.3
```

**macOS:**
```bash
brew install lua
```

### GraphViz Not Found

GraphViz is optional and only needed for DOT graph export.

To install:

**Windows:**
```bash
# Download from https://graphviz.org/download/
```

**Linux:**
```bash
sudo apt-get install graphviz
```

**macOS:**
```bash
brew install graphviz
```

---

## 🎯 Next Steps

### For Security Teams

1. **Customize Rules** - Edit files in `rules/` directory
2. **Add Event Sources** - Modify collectors for your environment
3. **Configure Alerts** - Set up alert destinations in `config/config.yaml`
4. **Deploy to Production** - Follow your organization's deployment process

### For Developers

1. **Read Architecture** - See `ARCHITECTURE.md` for technical details
2. **Review Code** - Explore the codebase
3. **Contribute** - See `CONTRIBUTING.md` for guidelines
4. **Extend Features** - Add new collectors, rules, or visualizations

### For Researchers

1. **Analyze Rules** - Study correlation logic in `rules/`
2. **Test Scenarios** - Run demo scenarios
3. **MITRE Mapping** - Explore ATT&CK integration
4. **Performance** - Benchmark correlation engine

---

## 📚 Additional Resources

### Documentation
- [README.md](README.md) - Project overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [CHANGELOG.md](CHANGELOG.md) - Version history

### Community
- GitHub Issues - Bug reports and feature requests
- Discussions - Community Q&A
- Pull Requests - Code contributions

---

## 🆘 Getting Help

### Common Issues

**Q: Dashboard shows "Disconnected"**
A: Check that the WebSocket server is running on port 3001

**Q: No events appearing**
A: Ensure event collectors are running and sending to aggregator

**Q: Rules not triggering**
A: Validate rules with `python tests/rule_validator.py`

**Q: High memory usage**
A: Adjust `retention_window` in `config/config.yaml`

### Support Channels

- **Documentation** - Check this guide and README.md
- **GitHub Issues** - Report bugs or request features
- **Community** - Join discussions

---

## ✅ Checklist

Before deploying to production:

- [ ] All dependencies installed
- [ ] Configuration customized for your environment
- [ ] Rules validated and tested
- [ ] Event collectors configured
- [ ] Dashboard accessible
- [ ] Integration tests passing
- [ ] Demo scenarios working
- [ ] Alert destinations configured
- [ ] Monitoring set up
- [ ] Documentation reviewed

---

**You're all set! 🎉**

LogicCorrelator is now ready to detect advanced threats in your environment.

For questions or issues, please refer to the documentation or open a GitHub issue.

**Happy threat hunting! 🔍**
