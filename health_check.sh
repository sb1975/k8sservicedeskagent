#!/bin/bash
echo "=== System Health Check ==="
echo ""

# Kubernetes
echo "1. Kubernetes Cluster:"
kubectl cluster-info > /dev/null 2>&1 && echo "   ✅ Cluster accessible" || echo "   ❌ Cluster not accessible"

# K8sGPT CLI
echo "2. K8sGPT CLI:"
k8sgpt version > /dev/null 2>&1 && echo "   ✅ K8sGPT installed" || echo "   ❌ K8sGPT not installed"

# Ollama
echo "3. Ollama Service:"
curl -s http://localhost:11434/api/tags > /dev/null 2>&1 && echo "   ✅ Ollama running" || echo "   ❌ Ollama not running"

# Ollama Model
echo "4. AI Model:"
ollama list 2>/dev/null | grep -q mistral && echo "   ✅ Mistral model available" || echo "   ❌ Mistral model not found"

# K8sGPT Agent
echo "5. K8sGPT Agent:"
curl -s http://localhost:8002/.well-known/agent-card.json > /dev/null 2>&1 && echo "   ✅ Agent running on port 8002" || echo "   ❌ Agent not running"

# JIRA Agent
echo "6. JIRA Agent:"
curl -s http://localhost:8003/.well-known/agent-card.json > /dev/null 2>&1 && echo "   ✅ Agent running on port 8003" || echo "   ❌ Agent not running"

# JIRA Credentials
echo "7. JIRA Configuration:"
[ -n "$JIRA_URL" ] && echo "   ✅ JIRA credentials loaded" || echo "   ❌ JIRA credentials not loaded (run: source ~/.env.jira)"

# Python Dependencies
echo "8. Python Dependencies:"
python3 -c "import flask; import requests" 2>/dev/null && echo "   ✅ Flask and requests installed" || echo "   ❌ Python dependencies missing"

echo ""
echo "=== Health Check Complete ==="
