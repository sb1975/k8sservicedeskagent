#!/bin/bash
set -e

echo "🚀 Starting K8s Issue Resolution System"
echo "========================================"

# Load JIRA credentials
echo "1. Loading JIRA credentials..."
if [ -f ~/.env.jira ]; then
    source ~/.env.jira
    echo "   ✅ JIRA credentials loaded"
else
    echo "   ❌ ~/.env.jira not found"
    echo "   Create it with:"
    echo "   export JIRA_URL=https://your-domain.atlassian.net"
    echo "   export JIRA_EMAIL=your-email@example.com"
    echo "   export JIRA_API_TOKEN=your-token"
    exit 1
fi

# Check Kubernetes
echo "2. Checking Kubernetes cluster..."
if kubectl cluster-info > /dev/null 2>&1; then
    echo "   ✅ Kubernetes accessible"
else
    echo "   ❌ Kubernetes not accessible"
    echo "   Start your cluster (minikube start / kind create cluster)"
    exit 1
fi

# Check Ollama
echo "3. Checking Ollama..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "   ✅ Ollama running"
else
    echo "   ❌ Ollama not running"
    echo "   Start it with: ollama serve &"
    exit 1
fi

# Check Ollama model
echo "4. Checking AI model..."
if ollama list 2>/dev/null | grep -q mistral; then
    echo "   ✅ Mistral model available"
else
    echo "   ⚠️  Mistral model not found"
    echo "   Download it with: ollama pull mistral:7b-instruct"
fi

# Start K8sGPT Agent
echo "5. Starting K8sGPT Agent..."
pkill -f k8sgpt_agent_simple.py 2>/dev/null || true
sleep 1
python3 k8sgpt_agent_simple.py > k8sgpt_agent.log 2>&1 &
sleep 3
if curl -s http://localhost:8002/.well-known/agent-card.json > /dev/null 2>&1; then
    echo "   ✅ K8sGPT Agent running on port 8002"
else
    echo "   ❌ K8sGPT Agent failed to start"
    echo "   Check logs: tail k8sgpt_agent.log"
    exit 1
fi

# Start JIRA Agent
echo "6. Starting JIRA Agent..."
pkill -f jira_agent_a2a.py 2>/dev/null || true
sleep 1
python3 jira_agent_a2a.py > jira_agent.log 2>&1 &
sleep 3
if curl -s http://localhost:8003/.well-known/agent-card.json > /dev/null 2>&1; then
    echo "   ✅ JIRA Agent running on port 8003"
else
    echo "   ❌ JIRA Agent failed to start"
    echo "   Check logs: tail jira_agent.log"
    exit 1
fi

echo ""
echo "✅ All systems ready!"
echo ""
echo "Run a test:"
echo "  ./run_single_test.sh pod_wrong_image"
echo ""
echo "Or run health check:"
echo "  ./health_check.sh"
