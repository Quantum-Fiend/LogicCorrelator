--[[
  LogicCorrelator - Correlation Engine
  Core event correlation and rule evaluation engine
]]--

local json = require("cjson")
local socket = require("socket")

-- Correlation Engine Module
local CorrelationEngine = {}
CorrelationEngine.__index = CorrelationEngine

-- Create new correlation engine instance
function CorrelationEngine:new(config)
    local instance = {
        config = config or {},
        rules = {},
        event_windows = {},
        correlation_state = {},
        alerts = {},
        decision_graphs = {},
        stats = {
            events_processed = 0,
            correlations_found = 0,
            alerts_generated = 0,
            rules_evaluated = 0
        }
    }
    setmetatable(instance, CorrelationEngine)
    return instance
end

-- Load rules from YAML (parsed to Lua table)
function CorrelationEngine:load_rules(rules_table)
    for _, rule in ipairs(rules_table.rules or {}) do
        if rule.enabled ~= false then
            table.insert(self.rules, rule)
            print(string.format("[ENGINE] Loaded rule: %s (%s)", rule.name, rule.id))
        end
    end
    print(string.format("[ENGINE] Total rules loaded: %d", #self.rules))
end

-- Process incoming event
function CorrelationEngine:process_event(event)
    self.stats.events_processed = self.stats.events_processed + 1
    
    -- Add event to appropriate time windows
    self:add_to_windows(event)
    
    -- Evaluate all rules against current state
    self:evaluate_rules(event)
    
    -- Clean up expired events
    self:cleanup_expired_events()
end

-- Add event to temporal windows
function CorrelationEngine:add_to_windows(event)
    local event_type = event.type
    
    if not self.event_windows[event_type] then
        self.event_windows[event_type] = {}
    end
    
    table.insert(self.event_windows[event_type], {
        event = event,
        timestamp = event.timestamp or os.time(),
        processed = false
    })
end

-- Evaluate all rules against current event
function CorrelationEngine:evaluate_rules(trigger_event)
    for _, rule in ipairs(self.rules) do
        self.stats.rules_evaluated = self.stats.rules_evaluated + 1
        
        if self:evaluate_rule(rule, trigger_event) then
            self:trigger_alert(rule, trigger_event)
        end
    end
end

-- Evaluate single rule
function CorrelationEngine:evaluate_rule(rule, trigger_event)
    local conditions = rule.conditions or {}
    local matched_events = {}
    local current_time = os.time()
    
    -- Track decision path for explainability
    local decision_path = {
        rule_id = rule.id,
        rule_name = rule.name,
        trigger_event = trigger_event,
        conditions_evaluated = {},
        matched = false
    }
    
    -- Evaluate each condition in sequence
    for i, condition in ipairs(conditions) do
        local condition_result = self:evaluate_condition(condition, matched_events, current_time)
        
        table.insert(decision_path.conditions_evaluated, {
            index = i,
            condition = condition,
            result = condition_result.matched,
            matched_events = condition_result.events
        })
        
        if not condition_result.matched then
            -- Condition failed, rule doesn't match
            decision_path.matched = false
            decision_path.failed_at_condition = i
            return false
        end
        
        -- Add matched events to correlation state
        for _, evt in ipairs(condition_result.events) do
            table.insert(matched_events, evt)
        end
    end
    
    -- All conditions matched
    decision_path.matched = true
    decision_path.all_matched_events = matched_events
    
    -- Store decision graph
    table.insert(self.decision_graphs, decision_path)
    
    self.stats.correlations_found = self.stats.correlations_found + 1
    return true
end

-- Evaluate single condition
function CorrelationEngine:evaluate_condition(condition, previous_events, current_time)
    local result = {
        matched = false,
        events = {}
    }
    
    local event_type = condition.type
    local window_events = self.event_windows[event_type] or {}
    
    -- Get time window
    local window_size = condition.window or 60
    local within_time = condition.within or window_size
    
    -- Filter events by time window
    local candidate_events = {}
    for _, evt_wrapper in ipairs(window_events) do
        local age = current_time - evt_wrapper.timestamp
        if age <= window_size then
            table.insert(candidate_events, evt_wrapper.event)
        end
    end
    
    -- Apply count filter
    local count_filter = condition.count or ">= 1"
    local required_count = self:parse_count_filter(count_filter)
    
    if #candidate_events < required_count then
        return result
    end
    
    -- Apply field filters
    local filtered_events = self:apply_field_filters(candidate_events, condition)
    
    -- Apply temporal constraints (after_previous, within)
    if condition.after_previous and #previous_events > 0 then
        local last_event_time = previous_events[#previous_events].timestamp or 0
        filtered_events = self:filter_by_time_after(filtered_events, last_event_time, within_time)
    end
    
    -- Check if we have enough events
    if #filtered_events >= required_count then
        result.matched = true
        result.events = filtered_events
    end
    
    return result
end

-- Parse count filter (e.g., ">= 5", "< 10")
function CorrelationEngine:parse_count_filter(filter_str)
    if type(filter_str) == "number" then
        return filter_str
    end
    
    local operator, value = filter_str:match("([><=]+)%s*(%d+)")
    value = tonumber(value) or 1
    
    -- For simplicity, return the numeric value
    -- In production, would evaluate operator
    return value
end

-- Apply field filters to events
function CorrelationEngine:apply_field_filters(events, condition)
    local filtered = {}
    
    for _, event in ipairs(events) do
        local matches = true
        
        -- Check process_name filter
        if condition.process_name then
            if type(condition.process_name) == "table" then
                local found = false
                for _, name in ipairs(condition.process_name) do
                    if event.process_name == name then
                        found = true
                        break
                    end
                end
                matches = matches and found
            else
                matches = matches and (event.process_name == condition.process_name)
            end
        end
        
        -- Check command_line_contains filter
        if condition.command_line_contains and event.command_line then
            local found = false
            local patterns = condition.command_line_contains
            if type(patterns) == "string" then
                patterns = {patterns}
            end
            for _, pattern in ipairs(patterns) do
                if event.command_line:find(pattern, 1, true) then
                    found = true
                    break
                end
            end
            matches = matches and found
        end
        
        -- Check same_user filter
        if condition.same_user and #filtered > 0 then
            matches = matches and (event.user == filtered[1].user)
        end
        
        -- Check direction filter
        if condition.direction then
            matches = matches and (event.direction == condition.direction)
        end
        
        -- Check dest_port filter
        if condition.dest_port then
            if type(condition.dest_port) == "table" then
                local found = false
                for _, port in ipairs(condition.dest_port) do
                    if event.dest_port == port then
                        found = true
                        break
                    end
                end
                matches = matches and found
            else
                matches = matches and (event.dest_port == condition.dest_port)
            end
        end
        
        if matches then
            table.insert(filtered, event)
        end
    end
    
    return filtered
end

-- Filter events that occurred after a specific time
function CorrelationEngine:filter_by_time_after(events, after_time, within_seconds)
    local filtered = {}
    local deadline = after_time + within_seconds
    
    for _, event in ipairs(events) do
        local evt_time = event.timestamp or 0
        if evt_time > after_time and evt_time <= deadline then
            table.insert(filtered, event)
        end
    end
    
    return filtered
end

-- Trigger alert for matched rule
function CorrelationEngine:trigger_alert(rule, trigger_event)
    self.stats.alerts_generated = self.stats.alerts_generated + 1
    
    local actions = rule.actions or {}
    local alert_action = nil
    
    -- Find alert action
    for _, action in ipairs(actions) do
        if action.alert then
            alert_action = action.alert
            break
        end
    end
    
    if not alert_action then
        alert_action = {
            message = rule.description or rule.name,
            severity = rule.severity or "MEDIUM",
            confidence = 0.75
        }
    end
    
    local alert = {
        timestamp = os.time(),
        rule_id = rule.id,
        rule_name = rule.name,
        message = alert_action.message,
        severity = alert_action.severity,
        confidence = alert_action.confidence,
        mitre_techniques = rule.mitre_techniques or {},
        trigger_event = trigger_event,
        tags = self:extract_tags(actions)
    }
    
    table.insert(self.alerts, alert)
    
    -- Print alert to console
    print(string.format("\n[ALERT] %s", string.rep("=", 60)))
    print(string.format("Rule: %s (%s)", alert.rule_name, alert.rule_id))
    print(string.format("Severity: %s | Confidence: %.2f", alert.severity, alert.confidence))
    print(string.format("Message: %s", alert.message))
    if #alert.mitre_techniques > 0 then
        print(string.format("MITRE ATT&CK: %s", table.concat(alert.mitre_techniques, ", ")))
    end
    print(string.rep("=", 60) .. "\n")
    
    return alert
end

-- Extract tags from rule actions
function CorrelationEngine:extract_tags(actions)
    for _, action in ipairs(actions) do
        if action.tag then
            return action.tag
        end
    end
    return {}
end

-- Clean up expired events from windows
function CorrelationEngine:cleanup_expired_events()
    local current_time = os.time()
    local max_retention = self.config.retention_window or 3600
    
    for event_type, events in pairs(self.event_windows) do
        local cleaned = {}
        for _, evt_wrapper in ipairs(events) do
            local age = current_time - evt_wrapper.timestamp
            if age <= max_retention then
                table.insert(cleaned, evt_wrapper)
            end
        end
        self.event_windows[event_type] = cleaned
    end
end

-- Get current statistics
function CorrelationEngine:get_stats()
    return {
        events_processed = self.stats.events_processed,
        correlations_found = self.stats.correlations_found,
        alerts_generated = self.stats.alerts_generated,
        rules_evaluated = self.stats.rules_evaluated,
        rules_loaded = #self.rules,
        event_windows_size = self:count_total_events()
    }
end

-- Count total events in all windows
function CorrelationEngine:count_total_events()
    local total = 0
    for _, events in pairs(self.event_windows) do
        total = total + #events
    end
    return total
end

-- Export decision graph to DOT format
function CorrelationEngine:export_decision_graph(graph_index)
    local graph = self.decision_graphs[graph_index]
    if not graph then
        return nil
    end
    
    local dot = {"digraph CorrelationGraph {"}
    table.insert(dot, '  rankdir=LR;')
    table.insert(dot, '  node [shape=box, style=rounded];')
    table.insert(dot, '')
    
    -- Add rule node
    table.insert(dot, string.format('  rule [label="%s\\n%s", fillcolor=lightblue, style=filled];', 
        graph.rule_id, graph.rule_name))
    
    -- Add condition nodes
    for i, cond_result in ipairs(graph.conditions_evaluated) do
        local color = cond_result.result and "lightgreen" or "lightcoral"
        local label = string.format("Condition %d\\n%s", i, cond_result.condition.type)
        table.insert(dot, string.format('  cond%d [label="%s", fillcolor=%s, style=filled];', 
            i, label, color))
        
        if i == 1 then
            table.insert(dot, string.format('  rule -> cond%d;', i))
        else
            table.insert(dot, string.format('  cond%d -> cond%d;', i-1, i))
        end
    end
    
    -- Add result node
    local result_color = graph.matched and "green" or "red"
    local result_label = graph.matched and "MATCHED\\nAlert Generated" or "NO MATCH"
    table.insert(dot, string.format('  result [label="%s", fillcolor=%s, style=filled, shape=ellipse];', 
        result_label, result_color))
    
    if #graph.conditions_evaluated > 0 then
        table.insert(dot, string.format('  cond%d -> result;', #graph.conditions_evaluated))
    end
    
    table.insert(dot, '}')
    
    return table.concat(dot, '\n')
end

-- Get recent alerts
function CorrelationEngine:get_recent_alerts(count)
    count = count or 10
    local recent = {}
    local start_idx = math.max(1, #self.alerts - count + 1)
    
    for i = start_idx, #self.alerts do
        table.insert(recent, self.alerts[i])
    end
    
    return recent
end

return CorrelationEngine
