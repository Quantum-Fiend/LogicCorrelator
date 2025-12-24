/**
 * LogicCorrelator - Dashboard Server
 * Real-time event correlation visualization and monitoring
 */

const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const path = require('path');
const fs = require('fs');

// Configuration
const PORT = process.env.PORT || 3000;
const WS_PORT = process.env.WS_PORT || 3001;

// Initialize Express app
const app = express();
const server = http.createServer(app);

// Initialize WebSocket server
const wss = new WebSocket.Server({ port: WS_PORT });

// Middleware
app.use(express.json());
app.use(express.static('public'));

// In-memory storage for demo
const state = {
    events: [],
    alerts: [],
    correlations: [],
    stats: {
        total_events: 0,
        total_alerts: 0,
        total_correlations: 0,
        rules_active: 0
    }
};

// WebSocket connection handler
wss.on('connection', (ws) => {
    console.log('[DASHBOARD] New WebSocket connection');

    // Send current state to new client
    ws.send(JSON.stringify({
        type: 'initial_state',
        data: {
            events: state.events.slice(-50),
            alerts: state.alerts.slice(-20),
            stats: state.stats
        }
    }));

    ws.on('message', (message) => {
        try {
            const data = JSON.parse(message);
            handleWebSocketMessage(ws, data);
        } catch (error) {
            console.error('[DASHBOARD] Error parsing WebSocket message:', error);
        }
    });

    ws.on('close', () => {
        console.log('[DASHBOARD] WebSocket connection closed');
    });
});

// Handle WebSocket messages
function handleWebSocketMessage(ws, data) {
    switch (data.type) {
        case 'get_stats':
            ws.send(JSON.stringify({
                type: 'stats_update',
                data: state.stats
            }));
            break;

        case 'get_events':
            ws.send(JSON.stringify({
                type: 'events_update',
                data: state.events.slice(-100)
            }));
            break;

        case 'get_alerts':
            ws.send(JSON.stringify({
                type: 'alerts_update',
                data: state.alerts.slice(-50)
            }));
            break;

        default:
            console.log('[DASHBOARD] Unknown message type:', data.type);
    }
}

// Broadcast to all connected clients
function broadcast(message) {
    wss.clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify(message));
        }
    });
}

// API Routes

// Health check
app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        connections: wss.clients.size
    });
});

// Get statistics
app.get('/api/stats', (req, res) => {
    res.json(state.stats);
});

// Get recent events
app.get('/api/events', (req, res) => {
    const limit = parseInt(req.query.limit) || 100;
    res.json(state.events.slice(-limit));
});

// Get recent alerts
app.get('/api/alerts', (req, res) => {
    const limit = parseInt(req.query.limit) || 50;
    res.json(state.alerts.slice(-limit));
});

// Receive new event (from aggregator)
app.post('/api/events', (req, res) => {
    const event = req.body;

    // Add to state
    state.events.push({
        ...event,
        received_at: new Date().toISOString()
    });

    // Keep only last 1000 events
    if (state.events.length > 1000) {
        state.events = state.events.slice(-1000);
    }

    state.stats.total_events++;

    // Broadcast to connected clients
    broadcast({
        type: 'new_event',
        data: event
    });

    res.json({ success: true });
});

// Receive new alert (from correlation engine)
app.post('/api/alerts', (req, res) => {
    const alert = req.body;

    // Add to state
    state.alerts.push({
        ...alert,
        received_at: new Date().toISOString()
    });

    // Keep only last 500 alerts
    if (state.alerts.length > 500) {
        state.alerts = state.alerts.slice(-500);
    }

    state.stats.total_alerts++;

    // Broadcast to connected clients
    broadcast({
        type: 'new_alert',
        data: alert
    });

    console.log(`[DASHBOARD] New alert: ${alert.rule_name} (${alert.severity})`);

    res.json({ success: true });
});

// Receive correlation update
app.post('/api/correlations', (req, res) => {
    const correlation = req.body;

    state.correlations.push({
        ...correlation,
        received_at: new Date().toISOString()
    });

    if (state.correlations.length > 200) {
        state.correlations = state.correlations.slice(-200);
    }

    state.stats.total_correlations++;

    broadcast({
        type: 'new_correlation',
        data: correlation
    });

    res.json({ success: true });
});

// Serve main dashboard page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start server
server.listen(PORT, () => {
    console.log('='.repeat(60));
    console.log('LogicCorrelator - Dashboard Server');
    console.log('='.repeat(60));
    console.log(`HTTP Server:      http://localhost:${PORT}`);
    console.log(`WebSocket Server: ws://localhost:${WS_PORT}`);
    console.log('='.repeat(60));
    console.log('Dashboard ready. Open browser to http://localhost:3000');
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n[DASHBOARD] Shutting down gracefully...');

    wss.clients.forEach((client) => {
        client.close();
    });

    server.close(() => {
        console.log('[DASHBOARD] Server closed');
        process.exit(0);
    });
});

// Demo event generator (for testing)
if (process.env.DEMO_MODE === 'true') {
    console.log('[DASHBOARD] Demo mode enabled - generating sample events');

    setInterval(() => {
        // Generate random event
        const eventTypes = ['auth_fail', 'auth_success', 'process_start', 'network_connect'];
        const randomType = eventTypes[Math.floor(Math.random() * eventTypes.length)];

        const demoEvent = {
            type: randomType,
            timestamp: new Date().toISOString(),
            user: `user${Math.floor(Math.random() * 10)}`,
            source_ip: `192.168.1.${Math.floor(Math.random() * 255)}`,
            _source: 'demo_generator'
        };

        state.events.push(demoEvent);
        state.stats.total_events++;

        broadcast({
            type: 'new_event',
            data: demoEvent
        });

        // Occasionally generate alert
        if (Math.random() > 0.9) {
            const demoAlert = {
                rule_id: 'DEMO-001',
                rule_name: 'Demo Alert',
                severity: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'][Math.floor(Math.random() * 4)],
                message: 'This is a demo alert',
                timestamp: new Date().toISOString(),
                confidence: Math.random()
            };

            state.alerts.push(demoAlert);
            state.stats.total_alerts++;

            broadcast({
                type: 'new_alert',
                data: demoAlert
            });
        }
    }, 2000);
}
