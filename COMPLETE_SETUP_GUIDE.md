# Complete Setup & Deployment Guide

## Table of Contents
1. [Prerequisites Installation](#prerequisites-installation)
2. [Kubernetes Cluster Setup](#kubernetes-cluster-setup)
3. [K8sGPT Installation & Configuration](#k8sgpt-installation--configuration)
4. [Ollama & AI Model Setup](#ollama--ai-model-setup)
5. [JIRA Configuration](#jira-configuration)
6. [Python Dependencies](#python-dependencies)
7. [Agent Deployment](#agent-deployment)
8. [Testing & Verification](#testing--verification)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites Installation

### System Requirements
- **OS**: Linux (Ubuntu 20.04+, WSL2, or any Linux distribution)
- **RAM**: Minimum 8GB (16GB recommended for AI model)
- **Disk**: 10GB free space
- **CPU**: 4+ cores recommended

### 1. Install kubectl

```bash
# Download latest kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Make it executable
chmod +x kubectl

# Move to PATH
sudo mv kubectl /usr/local/bin/

# Verify installation
kubectl version --client
```

**Expected output:**
```
Client Version: v1.28.x
```

### 2. Install Python 3 and pip

```bash
# Install Python 3
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# Verify installation
python3 --version  # Should be 3.8+
pip3 --version
```

### 3. Install curl and jq

```bash
sudo apt install -y curl jq

# Verify
curl --version
jq --version
```

---

## Kubernetes Cluster Setup

### Option A: Minikube (Recommended for Local Development)

#### Install Minikube

```bash
# Download minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64

# Install
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Verify
minikube version
```

#### Start Minikube Cluster

```bash
# Start cluster with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Verify cluster is running
kubectl cluster-info
kubectl get nodes
```

**Expected output:**
```
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   1m    v1.28.3
```

#### Enable Required Addons

```bash
# Enable metrics server (optional but useful)
minikube addons enable metrics-server

# Verify
kubectl get pods -n kube-system
```

### Option B: Kind (Kubernetes in Docker)

```bash
# Install kind
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Create cluster
kind create cluster --name k8sgpt-cluster

# Verify
kubectl cluster-info --context kind-k8sgpt-cluster
```

### Option C: Existing Cluster

If you already have a Kubernetes cluster:

```bash
# Verify access
kubectl cluster-info
kubectl get nodes

# Ensure you have admin permissions
kubectl auth can-i create pods --all-namespaces
```

---

## K8sGPT Installation & Configuration

### 1. Install K8sGPT CLI

#### Method 1: Using Homebrew (Linux)

```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"

# Install k8sgpt
brew install k8sgpt
```

#### Method 2: Direct Binary Download

```bash
# Download latest release
VERSION=$(curl -s https://api.github.com/repos/k8sgpt-ai/k8sgpt/releases/latest | jq -r .tag_name)
curl -LO "https://github.com/k8sgpt-ai/k8sgpt/releases/download/${VERSION}/k8sgpt_Linux_x86_64.tar.gz"

# Extract
tar -xzf k8sgpt_Linux_x86_64.tar.gz

# Move to PATH
sudo mv k8sgpt /usr/local/bin/

# Make executable
sudo chmod +x /usr/local/bin/k8sgpt
```

#### Method 3: Using Snap

```bash
sudo snap install k8sgpt
```

### 2. Verify K8sGPT Installation

```bash
k8sgpt version
```

**Expected output:**
```
k8sgpt: 0.4.26 (ee6f584), built at: unknown
```

### 3. Test K8sGPT (Without AI)

```bash
# Analyze cluster without AI
k8sgpt analyze --output=json

# Should return JSON with cluster analysis
```

---

## Ollama & AI Model Setup

### 1. Install Ollama

#### For Linux/WSL

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version
```

#### Start Ollama Service

```bash
# Ollama should auto-start, but if not:
ollama serve &

# Verify it's running
curl http://localhost:11434/api/tags
```

**Expected output:**
```json
{"models":[]}
```

### 2. Download AI Model

#### Option 1: Mistral 7B Instruct (Recommended - 4.4GB)

```bash
# Pull mistral model
ollama pull mistral:7b-instruct

# Verify download
ollama list
```

**Expected output:**
```
NAME                   ID              SIZE      MODIFIED
mistral:7b-instruct    6577803aa9a0    4.4 GB    now
```

#### Option 2: Qwen 2.5 7B (Alternative - 4.7GB)

```bash
ollama pull qwen2.5:7b
```

#### Option 3: Smaller Models (If RAM limited)

```bash
# Phi-3 Mini (3.8GB)
ollama pull phi3:mini

# Gemma 2B (1.4GB)
ollama pull gemma:2b
```

### 3. Test Ollama Model

```bash
# Test model
curl http://localhost:11434/api/generate -d '{
  "model": "mistral:7b-instruct",
  "prompt": "Say hello",
  "stream": false
}' | jq .response
```

**Expected output:**
```
" Hello there! How can I assist you today?"
```

### 4. Configure K8sGPT with Ollama

```bash
# Remove any existing backends
k8sgpt auth remove -b ollama 2>/dev/null || true
k8sgpt auth remove -b localai 2>/dev/null || true

# Add Ollama backend with correct configuration
k8sgpt auth add --backend ollama \
  --model mistral:7b-instruct \
  --baseurl http://localhost:11434

# Set as default
k8sgpt auth default -p ollama

# Verify configuration
k8sgpt auth list
```

**Expected output:**
```
Default:
> ollama
Active:
> ollama
```

### 5. Create Default Storage Class

```bash
# Create standard storage class for PVC tests
cat <<EOF | kubectl apply -f -
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
EOF

# Verify
kubectl get storageclass
```

**Expected output:**
```
NAME                 PROVISIONER
standard (default)   kubernetes.io/no-provisioner
```

### 6. Verify K8sGPT AI Integration

```bash
# Create a test pod with error
kubectl run test-pod --image=nginx:nonexistent --restart=Never

# Wait for error to manifest
sleep 15

# Test k8sgpt with AI explanation
k8sgpt analyze --explain --filter=Pod

# Should show AI-generated solution
# Clean up
kubectl delete pod test-pod
```

---

## JIRA Configuration

### 1. Create JIRA Account

1. Go to https://www.atlassian.com/software/jira
2. Sign up for free account
3. Create a new project (e.g., "Kubernetes Automation" - KAN)

### 2. Generate API Token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Name it "k8sgpt-automation"
4. Copy the token (you won't see it again!)

### 3. Configure JIRA Credentials

```bash
# Create environment file
cat > ~/.env.jira << 'EOF'
export JIRA_URL=https://YOUR-DOMAIN.atlassian.net
export JIRA_EMAIL=your-email@example.com
export JIRA_API_TOKEN=your-api-token-here
EOF

# Replace with your actual values
nano ~/.env.jira

# Load credentials
source ~/.env.jira

# Verify
echo $JIRA_URL
echo $JIRA_EMAIL
echo $JIRA_API_TOKEN
```

### 4. Test JIRA API Access

```bash
# Test authentication
curl -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  "$JIRA_URL/rest/api/3/myself" | jq .displayName

# Should return your name
```

### 5. Get Project Key

```bash
# List all projects
curl -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "$JIRA_URL/rest/api/3/project" | jq '.[] | {key: .key, name: .name}'

# Note your project key (e.g., "KAN")
```

---

## Python Dependencies

### 1. Create Project Directory

```bash
# Create project directory
mkdir -p ~/k8sgpt-automation
cd ~/k8sgpt-automation

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Required Packages

```bash
# Install dependencies
pip3 install flask requests

# Verify installation
python3 -c "import flask; import requests; print('✅ Dependencies installed')"
```

### 3. Create requirements.txt

```bash
cat > requirements.txt << 'EOF'
flask==3.0.0
requests==2.31.0
EOF

# Install from requirements
pip3 install -r requirements.txt
```

---

## Agent Deployment

### 1. Clone/Download Project Files

```bash
cd ~/k8sgpt-automation

# If using git
git clone <your-repo-url> .

# Or download files manually and place in this directory
```

### 2. Verify Project Structure

```bash
ls -la

# Should see:
# k8sgpt_agent_simple.py
# jira_agent_a2a.py
# jira_client_a2a.py
# test_scenarios.py
# test_single_issue.py
# run_single_test.sh
# run_all_tests.sh
# cleanup_all.sh
```

### 3. Make Scripts Executable

```bash
chmod +x run_single_test.sh
chmod +x run_all_tests.sh
chmod +x cleanup_all.sh
```

### 4. Start K8sGPT Agent

```bash
# Start K8sGPT agent
python3 k8sgpt_agent_simple.py > k8sgpt_agent.log 2>&1 &

# Save PID
echo $! > k8sgpt_agent.pid

# Verify it's running
sleep 3
curl -s http://localhost:8002/.well-known/agent-card.json | jq .name
```

**Expected output:**
```
"k8sgpt_agent"
```

### 5. Start JIRA Agent

```bash
# Load JIRA credentials
source ~/.env.jira

# Start JIRA agent
python3 jira_agent_a2a.py > jira_agent.log 2>&1 &

# Save PID
echo $! > jira_agent.pid

# Verify it's running
sleep 3
curl -s http://localhost:8003/.well-known/agent-card.json | jq .name
```

**Expected output:**
```
"jira_agent"
```

### 6. Verify Both Agents

```bash
# Check K8sGPT agent
curl -s http://localhost:8002/.well-known/agent-card.json | jq .

# Check JIRA agent
curl -s http://localhost:8003/.well-known/agent-card.json | jq .

# Check processes
ps aux | grep -E "(k8sgpt_agent|jira_agent)" | grep -v grep
```

---

## Testing & Verification

### 1. Quick Health Check

```bash
# Create health check script
cat > health_check.sh << 'EOF'
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
ollama list | grep -q mistral && echo "   ✅ Mistral model available" || echo "   ❌ Mistral model not found"

# K8sGPT Agent
echo "5. K8sGPT Agent:"
curl -s http://localhost:8002/.well-known/agent-card.json > /dev/null 2>&1 && echo "   ✅ Agent running on port 8002" || echo "   ❌ Agent not running"

# JIRA Agent
echo "6. JIRA Agent:"
curl -s http://localhost:8003/.well-known/agent-card.json > /dev/null 2>&1 && echo "   ✅ Agent running on port 8003" || echo "   ❌ Agent not running"

# JIRA Credentials
echo "7. JIRA Configuration:"
[ -n "$JIRA_URL" ] && echo "   ✅ JIRA credentials loaded" || echo "   ❌ JIRA credentials not loaded"

echo ""
echo "=== Health Check Complete ==="
EOF

chmod +x health_check.sh
./health_check.sh
```

### 2. Test Streaming Endpoint

```bash
# Test streaming with live progress
python3 test_streaming.py
```

**Expected output:**
```
⏱️ Analyzing: 0s elapsed...
⏱️ Analyzing: 2s elapsed...
...
✅ Complete!
```

### 3. Test Single Issue Workflow

```bash
# Clean up any existing test resources
./cleanup_all.sh

# Run single test
./run_single_test.sh pod_wrong_image
```

**Expected workflow:**
1. ✅ Creates pod with wrong image
2. ✅ Waits for error to manifest (15s)
3. ✅ K8sGPT detects ImagePullBackOff
4. ✅ Shows live progress during AI analysis (30s)
5. ✅ Gets AI-powered solution
6. ✅ Creates JIRA ticket
7. ✅ Updates pod image to nginx:latest
8. ✅ Verifies pod is Running
9. ✅ Updates JIRA with fix details
10. ✅ Closes JIRA ticket

### 4. Test All Scenarios

```bash
# Run all test scenarios
./run_all_tests.sh
```

This will test:
- pod_wrong_image
- pod_crashloop
- service_no_endpoints
- pvc_pending
- secret_unused
- cronjob_failed

---

## Troubleshooting

### Issue: K8sGPT Agent Not Starting

**Symptoms:**
```bash
curl http://localhost:8002/.well-known/agent-card.json
# Connection refused
```

**Solution:**
```bash
# Check logs
tail -50 k8sgpt_agent.log

# Check if port is in use
lsof -i :8002

# Kill existing process
pkill -f k8sgpt_agent_simple.py

# Restart
python3 k8sgpt_agent_simple.py > k8sgpt_agent.log 2>&1 &
```

### Issue: Ollama Not Running

**Symptoms:**
```bash
curl http://localhost:11434/api/tags
# Connection refused
```

**Solution:**
```bash
# Start Ollama
ollama serve > ollama.log 2>&1 &

# Or if installed via snap
sudo systemctl start ollama

# Verify
curl http://localhost:11434/api/tags
```

### Issue: K8sGPT Timeout

**Symptoms:**
```
Error: failed while calling AI provider ollama: timeout
```

**Solution:**
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Check model is loaded
ollama list

# Test model directly
ollama run mistral:7b-instruct "hello"

# Reconfigure k8sgpt
k8sgpt auth remove -b ollama
k8sgpt auth add --backend ollama --model mistral:7b-instruct --baseurl http://localhost:11434
k8sgpt auth default -p ollama
```

### Issue: JIRA Authentication Failed

**Symptoms:**
```
Error: 401 Unauthorized
```

**Solution:**
```bash
# Reload credentials
source ~/.env.jira

# Verify credentials
echo $JIRA_URL
echo $JIRA_EMAIL
echo $JIRA_API_TOKEN

# Test API access
curl -u "$JIRA_EMAIL:$JIRA_API_TOKEN" "$JIRA_URL/rest/api/3/myself"

# Regenerate API token if needed
# Go to https://id.atlassian.com/manage-profile/security/api-tokens
```

### Issue: Kubernetes Cluster Not Accessible

**Symptoms:**
```bash
kubectl cluster-info
# Unable to connect to server
```

**Solution:**
```bash
# For Minikube
minikube status
minikube start

# For Kind
kind get clusters
kubectl cluster-info --context kind-k8sgpt-cluster

# Check kubeconfig
kubectl config view
kubectl config current-context
```

### Issue: Python Dependencies Missing

**Symptoms:**
```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
```bash
# Install dependencies
pip3 install flask requests

# Or use requirements.txt
pip3 install -r requirements.txt

# Verify
python3 -c "import flask; import requests; print('OK')"
```

### Issue: AI Solution Not Generated

**Symptoms:**
```
Recommendation: No solution available
```

**Solution:**
```bash
# Check k8sgpt configuration
cat ~/.config/k8sgpt/k8sgpt.yaml | grep -A 5 ollama

# Should show:
# - name: ollama
#   model: mistral:7b-instruct
#   baseurl: http://localhost:11434

# If wrong, reconfigure
k8sgpt auth remove -b ollama
k8sgpt auth add --backend ollama --model mistral:7b-instruct --baseurl http://localhost:11434

# Test manually
k8sgpt analyze --explain --filter=Pod
```

---

## Starting Agents Automatically

### Create Systemd Services (Optional)

#### K8sGPT Agent Service

```bash
sudo tee /etc/systemd/system/k8sgpt-agent.service << EOF
[Unit]
Description=K8sGPT Agent
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/k8sgpt-automation
ExecStart=/usr/bin/python3 $HOME/k8sgpt-automation/k8sgpt_agent_simple.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable k8sgpt-agent
sudo systemctl start k8sgpt-agent
sudo systemctl status k8sgpt-agent
```

#### JIRA Agent Service

```bash
sudo tee /etc/systemd/system/jira-agent.service << EOF
[Unit]
Description=JIRA Agent
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/k8sgpt-automation
Environment="JIRA_URL=$JIRA_URL"
Environment="JIRA_EMAIL=$JIRA_EMAIL"
Environment="JIRA_API_TOKEN=$JIRA_API_TOKEN"
ExecStart=/usr/bin/python3 $HOME/k8sgpt-automation/jira_agent_a2a.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable jira-agent
sudo systemctl start jira-agent
sudo systemctl status jira-agent
```

---

## Quick Start Script

Create a complete startup script:

```bash
cat > start_all.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Starting K8s Issue Resolution System"
echo "========================================"

# Load JIRA credentials
echo "1. Loading JIRA credentials..."
source ~/.env.jira

# Check Kubernetes
echo "2. Checking Kubernetes cluster..."
kubectl cluster-info > /dev/null 2>&1 || { echo "❌ Kubernetes not accessible"; exit 1; }
echo "   ✅ Kubernetes accessible"

# Check Ollama
echo "3. Checking Ollama..."
curl -s http://localhost:11434/api/tags > /dev/null 2>&1 || { echo "❌ Ollama not running"; exit 1; }
echo "   ✅ Ollama running"

# Start K8sGPT Agent
echo "4. Starting K8sGPT Agent..."
pkill -f k8sgpt_agent_simple.py 2>/dev/null || true
python3 k8sgpt_agent_simple.py > k8sgpt_agent.log 2>&1 &
sleep 3
curl -s http://localhost:8002/.well-known/agent-card.json > /dev/null 2>&1 || { echo "❌ K8sGPT Agent failed"; exit 1; }
echo "   ✅ K8sGPT Agent running on port 8002"

# Start JIRA Agent
echo "5. Starting JIRA Agent..."
pkill -f jira_agent_a2a.py 2>/dev/null || true
python3 jira_agent_a2a.py > jira_agent.log 2>&1 &
sleep 3
curl -s http://localhost:8003/.well-known/agent-card.json > /dev/null 2>&1 || { echo "❌ JIRA Agent failed"; exit 1; }
echo "   ✅ JIRA Agent running on port 8003"

echo ""
echo "✅ All systems ready!"
echo ""
echo "Run a test:"
echo "  ./run_single_test.sh pod_wrong_image"
EOF

chmod +x start_all.sh
```

---

## Summary Checklist

Before running tests, ensure:

- [ ] Kubernetes cluster is running (`kubectl cluster-info`)
- [ ] K8sGPT CLI is installed (`k8sgpt version`)
- [ ] Ollama is running (`curl http://localhost:11434/api/tags`)
- [ ] Mistral model is downloaded (`ollama list`)
- [ ] K8sGPT configured with Ollama (`k8sgpt auth list`)
- [ ] JIRA credentials are set (`echo $JIRA_URL`)
- [ ] Python dependencies installed (`pip3 list | grep flask`)
- [ ] K8sGPT Agent is running (`curl http://localhost:8002/.well-known/agent-card.json`)
- [ ] JIRA Agent is running (`curl http://localhost:8003/.well-known/agent-card.json`)

Run health check:
```bash
./health_check.sh
```

If all checks pass, run:
```bash
./run_single_test.sh pod_wrong_image
```

---

## Next Steps

1. Review the workflow output
2. Check JIRA ticket created
3. Verify pod was fixed (not deleted)
4. Run additional test scenarios
5. Customize for your use cases

For detailed workflow information, see `COMPLETE_WORKFLOW_GUIDE.md`
