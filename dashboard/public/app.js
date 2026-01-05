/**
 * LogicCorrelator - Dashboard Frontend
 * Real-time event visualization and correlation monitoring
 */

// Configuration
const WS_URL = 'ws://localhost:3001';
const MAX_EVENTS_DISPLAY = 100;
const MAX_ALERTS_DISPLAY = 50;

// State
let ws = null;
let eventStreamPaused = false;
let currentAlertFilter = 'all';
let events = [];
let alerts = [];
let stats = {
    total_events: 0,
    total_alerts: 0,
    total_correlations: 0
};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    console.log('[DASHBOARD] Initializing...');
    connectWebSocket();
    startMetricsUpdate();
});

// WebSocket Connection
function connectWebSocket() {
    console.log('[DASHBOARD] Connecting to WebSocket...');

    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
        console.log('[DASHBOARD] WebSocket connected');
        updateConnectionStatus(true);
    };

    ws.onmessage = (event) => {
        try {
            const message = JSON.parse(event.data);
            handleWebSocketMessage(message);
        } catch (error) {
            console.error('[DASHBOARD] Error parsing message:', error);
        }
    };

    ws.onerror = (error) => {
        console.error('[DASHBOARD] WebSocket error:', error);
        updateConnectionStatus(false);
    };

    ws.onclose = () => {
        console.log('[DASHBOARD] WebSocket disconnected');
        updateConnectionStatus(false);

        // Attempt reconnection after 5 seconds
        setTimeout(connectWebSocket, 5000);
    };
}

// Handle WebSocket messages
function handleWebSocketMessage(message) {
    switch (message.type) {
        case 'initial_state':
            handleInitialState(message.data);
            break;

        case 'new_event':
            handleNewEvent(message.data);
            break;

        case 'new_alert':
            handleNewAlert(message.data);
            break;

        case 'new_correlation':
            handleNewCorrelation(message.data);
            break;

        case 'correlation_update':
            // Handle response from get_correlations or initial load payload
            if (message.data) {
                renderCorrelationGraph(message.data);
            }
            break;

        case 'stats_update':
            updateStats(message.data);
            break;

        default:
            console.log('[DASHBOARD] Unknown message type:', message.type);
    }

    updateLastUpdateTime();
}

// Handle initial state
function handleInitialState(data) {
    console.log('[DASHBOARD] Received initial state');

    if (data.events) {
        events = data.events;
        renderEvents();
    }

    if (data.alerts) {
        alerts = data.alerts;
        renderAlerts();
    }

    if (data.correlations && data.correlations.length > 0) {
        renderCorrelationGraph(data.correlations[0]);
    }

    if (data.stats) {
        updateStats(data.stats);
    }
}

// Handle new event
function handleNewEvent(event) {
    if (!eventStreamPaused) {
        events.push(event);

        // Keep only last MAX_EVENTS_DISPLAY
        if (events.length > MAX_EVENTS_DISPLAY) {
            events = events.slice(-MAX_EVENTS_DISPLAY);
        }

        renderEvents();
        stats.total_events++;
        updateStatsDisplay();
    }
}

// Handle new alert
function handleNewAlert(alert) {
    alerts.unshift(alert); // Add to beginning

    // Keep only last MAX_ALERTS_DISPLAY
    if (alerts.length > MAX_ALERTS_DISPLAY) {
        alerts = alerts.slice(0, MAX_ALERTS_DISPLAY);
    }

    renderAlerts();
    showAlertBanner(alert);

    stats.total_alerts++;
    updateStatsDisplay();
}

// Handle new correlation
function handleNewCorrelation(correlation) {
    stats.total_correlations++;
    updateStatsDisplay();

    // Update correlation graph
    renderCorrelationGraph(correlation);
}

// Render events
function renderEvents() {
    const eventList = document.getElementById('event-list');
    const filterText = document.getElementById('event-filter').value.toLowerCase();
    const filterType = document.getElementById('event-type-filter').value;

    // Filter events
    const filteredEvents = events.filter(event => {
        const matchesText = !filterText || JSON.stringify(event).toLowerCase().includes(filterText);
        const matchesType = !filterType || event.type === filterType;
        return matchesText && matchesType;
    });

    if (filteredEvents.length === 0) {
        eventList.innerHTML = `
            <div class="empty-state">
                <span class="empty-icon">📊</span>
                <p>No events match your filters</p>
            </div>
        `;
        return;
    }

    // Render events (most recent first)
    eventList.innerHTML = filteredEvents.reverse().map(event => {
        const eventTypeClass = event.type.replace('_', '-');
        const timestamp = new Date(event.timestamp).toLocaleTimeString();

        return `
            <div class="event-item ${eventTypeClass}">
                <div class="event-header">
                    <span class="event-type">${getEventTypeIcon(event.type)} ${event.type}</span>
                    <span class="event-time">${timestamp}</span>
                </div>
                <div class="event-details">
                    ${formatEventDetails(event)}
                </div>
            </div>
        `;
    }).join('');
}

// Get event type icon
function getEventTypeIcon(type) {
    const icons = {
        'auth_fail': '🔴',
        'auth_success': '🟢',
        'process_start': '⚙️',
        'network_connect': '🌐',
        'file_access': '📁',
        'registry_change': '📝',
        'privilege_escalation': '⬆️'
    };
    return icons[type] || '📌';
}

// Format event details
function formatEventDetails(event) {
    const details = [];

    if (event.user) details.push(`User: <strong>${event.user}</strong>`);
    if (event.source_ip) details.push(`IP: <strong>${event.source_ip}</strong>`);
    if (event.process_name) details.push(`Process: <strong>${event.process_name}</strong>`);
    if (event.dest_ip) details.push(`Dest: <strong>${event.dest_ip}:${event.dest_port}</strong>`);
    if (event.file_path) details.push(`File: <strong>${event.file_path}</strong>`);

    return details.join(' | ');
}

// Render alerts
function renderAlerts() {
    const alertList = document.getElementById('alert-list');

    // Filter by severity
    const filteredAlerts = currentAlertFilter === 'all'
        ? alerts
        : alerts.filter(alert => alert.severity === currentAlertFilter);

    if (filteredAlerts.length === 0) {
        alertList.innerHTML = `
            <div class="empty-state">
                <span class="empty-icon">✅</span>
                <p>No ${currentAlertFilter === 'all' ? '' : currentAlertFilter} alerts</p>
            </div>
        `;
        return;
    }

    alertList.innerHTML = filteredAlerts.map(alert => {
        const timestamp = new Date(alert.timestamp).toLocaleString();
        const severityClass = alert.severity.toLowerCase();

        return `
            <div class="alert-item severity-${severityClass}">
                <div class="alert-item-header">
                    <span class="alert-severity">${alert.severity}</span>
                    <span class="alert-time">${timestamp}</span>
                </div>
                <div class="alert-item-body">
                    <h4>${alert.rule_name}</h4>
                    <p>${alert.message}</p>
                    ${alert.mitre_techniques && alert.mitre_techniques.length > 0 ? `
                        <div class="alert-mitre">
                            <strong>MITRE ATT&CK:</strong> ${alert.mitre_techniques.join(', ')}
                        </div>
                    ` : ''}
                    <div class="alert-confidence">
                        Confidence: <strong>${(alert.confidence * 100).toFixed(0)}%</strong>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Show alert banner
function showAlertBanner(alert) {
    const banner = document.getElementById('alert-banner');
    const title = document.getElementById('alert-title');
    const message = document.getElementById('alert-message');

    title.textContent = `${alert.severity}: ${alert.rule_name}`;
    message.textContent = alert.message;

    banner.className = `alert-banner severity-${alert.severity.toLowerCase()}`;
    banner.style.display = 'block';

    // Auto-hide after 10 seconds
    setTimeout(() => {
        banner.style.display = 'none';
    }, 10000);
}

// Close alert banner
function closeAlertBanner() {
    document.getElementById('alert-banner').style.display = 'none';
}

// Render correlation graph with Cytoscape.js
let cy = null;

function initGraph() {
    if (cy) return;

    const container = document.getElementById('correlation-graph');
    container.innerHTML = ''; // Clear placeholder

    // Fix: Remove flex styling and ensure size
    container.style.display = 'block';
    container.style.width = '100%';
    container.style.height = '100%';

    cy = cytoscape({
        container: container,

        style: [
            {
                selector: 'node',
                style: {
                    'background-color': '#3b82f6', // accent-primary
                    'label': 'data(label)',
                    'color': '#f9fafb', // text-primary
                    'font-size': '12px',
                    'font-family': 'Inter, sans-serif',
                    'text-valign': 'bottom',
                    'text-margin-y': 5,
                    'width': 40,
                    'height': 40,
                    'border-width': 2,
                    'border-color': '#1f2937',
                    'overlay-opacity': 0
                }
            },
            {
                selector: 'node[type="user"]',
                style: {
                    'background-color': '#8b5cf6', // accent-secondary
                    'shape': 'ellipse'
                }
            },
            {
                selector: 'node[type="ip"]',
                style: {
                    'background-color': '#10b981', // accent-success
                    'shape': 'round-rectangle'
                }
            },
            {
                selector: 'node[type="process"]',
                style: {
                    'background-color': '#f59e0b', // accent-warning
                    'shape': 'cut-rectangle'
                }
            },
            {
                selector: 'node[type="alert"]',
                style: {
                    'background-color': '#ef4444', // accent-danger
                    'shape': 'diamond',
                    'width': 50,
                    'height': 50
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'line-color': '#4b5563', // border-color
                    'target-arrow-color': '#4b5563',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    'label': 'data(label)',
                    'font-size': '10px',
                    'color': '#9ca3af', // text-secondary
                    'text-rotation': 'autorotate',
                    'text-background-color': '#111827', // bg-secondary
                    'text-background-opacity': 0.8,
                    'text-background-padding': 2
                }
            }
        ],

        layout: {
            name: 'cose',
            animate: true,
            randomize: true,
            componentSpacing: 100,
            nodeRepulsion: 400000,
            nodeOverlap: 10,
            idealEdgeLength: 100,
            edgeElasticity: 100,
            nestingFactor: 5,
            gravity: 80,
            numIter: 1000,
            initialTemp: 200,
            coolingFactor: 0.95,
            minTemp: 1.0
        }
    });

    // Resize on window resize
    window.addEventListener('resize', () => cy.resize());
}

function renderCorrelationGraph(correlation) {
    // Initialize graph if not already done
    if (!cy) initGraph();

    if (!correlation.graph) {
        // Fallback for simple updates
        return;
    }

    const { nodes, edges } = correlation.graph;

    // Add nodes
    nodes.forEach(node => {
        if (cy.getElementById(node.id).empty()) {
            cy.add({
                group: 'nodes',
                data: node
            });
        }
    });

    // Add edges
    edges.forEach(edge => {
        const edgeId = `${edge.source}-${edge.target}`;
        if (cy.getElementById(edgeId).empty()) {
            cy.add({
                group: 'edges',
                data: { id: edgeId, ...edge }
            });
        }
    });

    // Rerun layout
    const layout = cy.layout({
        name: 'cose',
        animate: true,
        animationDuration: 500
    });
    layout.run();

    // Center logic
    cy.resize();
    cy.center();
    cy.fit(null, 50);
}

// Update stats display
function updateStatsDisplay() {
    document.getElementById('stat-events').textContent = stats.total_events.toLocaleString();
    document.getElementById('stat-correlations').textContent = stats.total_correlations.toLocaleString();
    document.getElementById('stat-alerts').textContent = stats.total_alerts.toLocaleString();
}

// Update stats
function updateStats(newStats) {
    stats = { ...stats, ...newStats };
    updateStatsDisplay();
}

// Update connection status
function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connection-status');

    if (connected) {
        statusElement.className = 'connection-status connected';
        statusElement.innerHTML = '<span class="status-dot"></span><span>Connected</span>';
    } else {
        statusElement.className = 'connection-status disconnected';
        statusElement.innerHTML = '<span class="status-dot"></span><span>Disconnected</span>';
    }
}

// Update last update time
function updateLastUpdateTime() {
    document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
}

// Toggle event stream
function toggleEventStream() {
    eventStreamPaused = !eventStreamPaused;
    const toggle = document.getElementById('stream-toggle');
    toggle.textContent = eventStreamPaused ? '▶' : '⏸';
}

// Clear events
function clearEvents() {
    if (confirm('Clear all events from display?')) {
        events = [];
        renderEvents();
    }
}

// Filter alerts by severity
function filterAlerts(severity) {
    currentAlertFilter = severity;

    // Update button states
    document.querySelectorAll('.severity-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.severity === severity) {
            btn.classList.add('active');
        }
    });

    renderAlerts();
}

// Refresh correlation graph
function refreshGraph() {
    // Request latest correlations from server
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'get_correlations' }));
    }
}

// Start metrics update interval
function startMetricsUpdate() {
    setInterval(() => {
        // Calculate events per second (simplified)
        const eps = Math.floor(Math.random() * 50); // Demo value
        document.getElementById('metric-eps').textContent = eps;

        // Random latency
        const latency = Math.floor(Math.random() * 100) + 10;
        document.getElementById('metric-latency').textContent = `${latency}ms`;

        // Rules active
        document.getElementById('metric-rules').textContent = '24';

        // Detection rate
        const detectionRate = stats.total_events > 0
            ? ((stats.total_correlations / stats.total_events) * 100).toFixed(1)
            : 0;
        document.getElementById('metric-detection').textContent = `${detectionRate}%`;
    }, 2000);
}

// Event listeners
document.getElementById('event-filter').addEventListener('input', renderEvents);
document.getElementById('event-type-filter').addEventListener('change', renderEvents);
