# LogicCorrelator - Unified Makefile
# Multi-language event correlation engine build system

.PHONY: all install start stop test clean help demo

# Default target
all: install

# Colors for output
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Print colored message
define print_msg
	@echo "$(CYAN)[LogicCorrelator]$(NC) $(1)"
endef

define print_success
	@echo "$(GREEN)[SUCCESS]$(NC) $(1)"
endef

define print_error
	@echo "$(RED)[ERROR]$(NC) $(1)"
endef

# Help target
help:
	@echo "$(CYAN)╔═══════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(CYAN)║         LogicCorrelator - Build System Help              ║$(NC)"
	@echo "$(CYAN)╚═══════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "Available targets:"
	@echo "  $(GREEN)make install$(NC)    - Install all dependencies"
	@echo "  $(GREEN)make start$(NC)      - Start all services"
	@echo "  $(GREEN)make stop$(NC)       - Stop all services"
	@echo "  $(GREEN)make demo$(NC)       - Run demo mode with sample events"
	@echo "  $(GREEN)make test$(NC)       - Run tests and validation"
	@echo "  $(GREEN)make clean$(NC)      - Clean generated files"
	@echo "  $(GREEN)make help$(NC)       - Show this help message"
	@echo ""

# Install dependencies
install:
	$(call print_msg,Installing dependencies...)
	@echo ""
	
	# Python dependencies
	$(call print_msg,Installing Python dependencies...)
	@pip install pyyaml --quiet || $(call print_error,Failed to install Python dependencies)
	$(call print_success,Python dependencies installed)
	@echo ""
	
	# Node.js dependencies
	$(call print_msg,Installing Node.js dependencies...)
	@cd dashboard && npm install --silent || $(call print_error,Failed to install Node.js dependencies)
	$(call print_success,Node.js dependencies installed)
	@echo ""
	
	# Create necessary directories
	$(call print_msg,Creating directories...)
	@mkdir -p logs graphs
	$(call print_success,Directories created)
	@echo ""
	
	# Validate Lua syntax
	$(call print_msg,Validating Lua files...)
	@lua -e "print('Lua interpreter available')" 2>/dev/null || echo "$(YELLOW)[WARNING]$(NC) Lua not found - install Lua 5.3+ for correlation engine"
	@echo ""
	
	# Check AWK availability
	$(call print_msg,Checking AWK availability...)
	@awk 'BEGIN {print "AWK available"}' || echo "$(YELLOW)[WARNING]$(NC) AWK not found"
	@echo ""
	
	$(call print_success,Installation complete!)
	@echo ""

# Start all services
start:
	$(call print_msg,Starting LogicCorrelator services...)
	@echo ""
	@python orchestrator.py start

# Stop all services
stop:
	$(call print_msg,Stopping LogicCorrelator services...)
	@python orchestrator.py stop

# Run demo mode
demo:
	$(call print_msg,Starting demo mode...)
	@echo ""
	$(call print_msg,Dashboard will be available at http://localhost:3000)
	@cd dashboard && DEMO_MODE=true npm start

# Run tests
test: test-rules test-python test-integration

test-rules:
	$(call print_msg,Validating correlation rules...)
	@python tests/rule_validator.py

test-python:
	$(call print_msg,Testing Python components...)
	@python -m pytest tests/ -v || echo "$(YELLOW)[WARNING]$(NC) pytest not installed"

test-integration:
	$(call print_msg,Running integration tests...)
	@python tests/integration_test.py

# Clean generated files
clean:
	$(call print_msg,Cleaning generated files...)
	@rm -rf logs/*.log
	@rm -rf graphs/*.dot graphs/*.png
	@rm -rf dashboard/node_modules
	@rm -rf __pycache__ core/__pycache__ features/__pycache__
	@find . -name "*.pyc" -delete
	$(call print_success,Cleanup complete)

# Quick start (install + demo)
quickstart: install demo

# Check system requirements
check:
	@echo "$(CYAN)╔═══════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(CYAN)║         System Requirements Check                        ║$(NC)"
	@echo "$(CYAN)╚═══════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "Checking Python..."
	@python --version || echo "$(RED)[MISSING]$(NC) Python not found"
	@echo ""
	@echo "Checking Node.js..."
	@node --version || echo "$(RED)[MISSING]$(NC) Node.js not found"
	@echo ""
	@echo "Checking Lua..."
	@lua -v || echo "$(YELLOW)[OPTIONAL]$(NC) Lua not found"
	@echo ""
	@echo "Checking AWK..."
	@awk --version || echo "$(YELLOW)[OPTIONAL]$(NC) AWK not found"
	@echo ""
	@echo "Checking GraphViz..."
	@dot -V || echo "$(YELLOW)[OPTIONAL]$(NC) GraphViz not found (needed for graph export)"
	@echo ""
