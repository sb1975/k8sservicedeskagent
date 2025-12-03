# Documentation Index

Complete documentation for K8s Issue Resolution with Multi-Agent System.

## 📚 Documentation Files

### 1. **README.md** - Quick Start Guide
- Project overview
- Architecture diagram
- Quick start commands
- Available test scenarios
- Core files reference

**Use when:** You want a quick overview of the project

---

### 2. **COMPLETE_SETUP_GUIDE.md** - Full Installation Guide ⭐
- **Prerequisites installation** (kubectl, Python, curl, jq)
- **Kubernetes cluster setup** (Minikube, Kind, or existing)
- **K8sGPT installation** (3 methods)
- **Ollama & AI model setup** (Mistral 7B)
- **JIRA configuration** (API tokens, credentials)
- **Python dependencies** (Flask, requests)
- **Agent deployment** (K8sGPT Agent, JIRA Agent)
- **Testing & verification**
- **Troubleshooting** (common issues)
- **Systemd services** (auto-start)

**Use when:** Setting up the system from scratch

**Start here if:** This is your first time deploying the system

---

### 3. **COMPLETE_WORKFLOW_GUIDE.md** - Architecture & Workflow
- System architecture diagrams
- Three-agent system explanation
- Complete workflow diagram (9 steps)
- Agent communication details
- Agent2Agent (A2A) protocol
- Step-by-step execution guide
- Detailed examples with actual commands
- Agent interaction summary

**Use when:** You want to understand how the system works internally

---

### 4. **ASYNC_IMPROVEMENTS.md** - Streaming & Performance
- Problem statement (long waits, no feedback)
- Streaming endpoint implementation
- Server-Sent Events (SSE) architecture
- Resource type filtering for speed
- Async threading details
- Performance comparison (before/after)
- Technical implementation details

**Use when:** You want to understand the async/streaming features

---

### 5. **FIXES_APPLIED.md** - Initial Bug Fixes
- K8sGPT warning issues
- Pod deletion vs image update
- Verification logic fixes
- Changes made to each file

**Use when:** You want to know what bugs were fixed

---

### 6. **COMPLETE_FIXES_SUMMARY.md** - All Improvements
- Model configuration fixes
- Live progress implementation
- Speed optimizations (4x faster)
- Correct fix application
- Architecture changes
- Performance comparison table
- Test instructions

**Use when:** You want a comprehensive summary of all improvements

---

### 7. **INTELLIGENT_FIXES.md** - Smart Fix Implementation
- Intelligent fixes vs deletions
- Fix strategies for each scenario
- Storage class setup
- Before/after comparison
- Test results

**Use when:** You want to understand how issues are fixed intelligently

---

## 🚀 Quick Start Workflow

### First Time Setup

1. **Read:** [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)
2. **Install:** All prerequisites (Kubernetes, K8sGPT, Ollama, etc.)
3. **Configure:** JIRA credentials and K8sGPT with Ollama
4. **Deploy:** Start both agents
5. **Verify:** Run health check

```bash
# Follow COMPLETE_SETUP_GUIDE.md step by step
# Then run:
bash health_check.sh
```

### Daily Usage

1. **Start agents:**
```bash
bash start_all.sh
```

2. **Run health check:**
```bash
bash health_check.sh
```

3. **Test single scenario:**
```bash
./run_single_test.sh pod_wrong_image
```

4. **Test all scenarios:**
```bash
./run_all_tests.sh
```

---

## 🛠️ Utility Scripts

### health_check.sh
Verifies all system components are working:
- Kubernetes cluster
- K8sGPT CLI
- Ollama service
- AI model availability
- K8sGPT Agent (port 8002)
- JIRA Agent (port 8003)
- JIRA credentials
- Python dependencies

```bash
bash health_check.sh
```

### start_all.sh
Starts all agents with proper checks:
- Loads JIRA credentials
- Verifies Kubernetes access
- Checks Ollama is running
- Starts K8sGPT Agent
- Starts JIRA Agent
- Confirms all systems ready

```bash
bash start_all.sh
```

### run_single_test.sh
Tests a single issue scenario:
```bash
./run_single_test.sh <scenario>
```

Available scenarios:
- `pod_wrong_image` - ImagePullBackOff
- `pod_crashloop` - CrashLoopBackOff
- `service_no_endpoints` - Service with no endpoints
- `pvc_pending` - PVC in pending state
- `secret_unused` - Unused secret
- `cronjob_failed` - Failed CronJob

### run_all_tests.sh
Runs all test scenarios sequentially:
```bash
./run_all_tests.sh
```

### cleanup_all.sh
Removes all test resources:
```bash
./cleanup_all.sh
```

### test_streaming.py
Quick test of streaming endpoint:
```bash
python3 test_streaming.py
```

---

## 📋 Troubleshooting Guide

### Common Issues

| Issue | Solution | Documentation |
|-------|----------|---------------|
| Agents won't start | Check logs, verify ports | COMPLETE_SETUP_GUIDE.md → Troubleshooting |
| Ollama timeout | Verify model loaded, check config | COMPLETE_SETUP_GUIDE.md → Ollama Setup |
| JIRA auth failed | Reload credentials, regenerate token | COMPLETE_SETUP_GUIDE.md → JIRA Configuration |
| K8s not accessible | Start cluster (minikube/kind) | COMPLETE_SETUP_GUIDE.md → Kubernetes Setup |
| No AI solution | Check k8sgpt config, test manually | COMPLETE_FIXES_SUMMARY.md → Model Config |

### Quick Diagnostics

```bash
# Run health check
bash health_check.sh

# Check agent logs
tail -50 k8sgpt_agent.log
tail -50 jira_agent.log

# Test k8sgpt manually
k8sgpt analyze --explain --filter=Pod

# Test Ollama
curl http://localhost:11434/api/generate -d '{"model":"mistral:7b-instruct","prompt":"hello","stream":false}'

# Test JIRA API
source ~/.env.jira
curl -u "$JIRA_EMAIL:$JIRA_API_TOKEN" "$JIRA_URL/rest/api/3/myself"
```

---

##  Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  K8s ServiceDesk AGENT                       │
│                  (test_single_issue.py)                      │
└────────────┬──────────────────────────────┬─────────────────┘
             │                               │
             │ A2A Protocol                  │ A2A Protocol
             │ (HTTP/JSON)                   │ (HTTP/JSON)
             │                               │
    ┌────────▼────────┐            ┌────────▼────────┐
    │  K8sGPT AGENT   │            │  JIRA AGENT     │
    │  Port 8002      │            │  Port 8003      │
    │                 │            │                 │
    │ • Analyze       │            │ • Create issue  │
    │ • Get solution  │            │ • Update issue  │
    │ • Stream        │            │ • Close issue   │
    └─────────────────┘            └────────┬────────┘
                                            │
                                            │ REST API
                                            │
                                   ┌────────▼────────┐
                                   │ Atlassian JIRA  │
                                   └─────────────────┘
```

---

## 🎯 Key Features

✅ **Automated Detection** - K8sGPT finds issues in ~10s  
✅ **AI-Powered Solutions** - Mistral 7B provides intelligent fixes  
✅ **Live Progress** - Streaming updates every 2s  
✅ **Fast Analysis** - Resource filtering reduces time 4x  
✅ **Issue Tracking** - JIRA maintains complete audit trail  
✅ **Smart Fixes** - Updates resources instead of deleting  
✅ **Verification** - Confirms issues are resolved  
✅ **Multi-Agent** - Three specialized agents working together  

---

## 📊 Performance Metrics

| Metric | Before | After |
|--------|--------|-------|
| AI Model | tinyllama (useless) | mistral:7b-instruct |
| Analysis Time | 120s timeout | 30s with filter |
| User Feedback | None | Live progress every 2s |
| Fix Action | Delete pod | Update image |
| Verification | Wrong (NotFound) | Correct (Running) |
| AI Solution | Warnings/errors | Proper recommendations |

---

## 🔗 External Resources

- **K8sGPT**: https://github.com/k8sgpt-ai/k8sgpt
- **Ollama**: https://ollama.com
- **Mistral AI**: https://mistral.ai
- **JIRA API**: https://developer.atlassian.com/cloud/jira/platform/rest/v3/
- **Kubernetes**: https://kubernetes.io/docs/

---

## 📝 File Structure

```
k8sgpt-automation/
├── README.md                      # Quick start
├── COMPLETE_SETUP_GUIDE.md        # Full installation ⭐
├── COMPLETE_WORKFLOW_GUIDE.md     # Architecture & workflow
├── ASYNC_IMPROVEMENTS.md          # Streaming features
├── FIXES_APPLIED.md               # Bug fixes
├── COMPLETE_FIXES_SUMMARY.md      # All improvements
├── INTELLIGENT_FIXES.md           # Smart fix strategies
├── DOCUMENTATION_INDEX.md         # This file
│
├── k8sgpt_agent_simple.py         # K8sGPT Agent (port 8002)
├── jira_agent_a2a.py              # JIRA Agent (port 8003)
├── jira_client_a2a.py             # JIRA client library
│
├── test_scenarios.py              # Issue definitions
├── test_single_issue.py           # Orchestrator workflow
├── test_streaming.py              # Streaming test
│
├── health_check.sh                # System health check
├── start_all.sh                   # Start all agents
├── run_single_test.sh             # Single test runner
├── run_all_tests.sh               # All tests runner
├── cleanup_all.sh                 # Resource cleanup
│
└── requirements.txt               # Python dependencies
```

---

## 🎓 Learning Path

### Beginner
1. Read **README.md** for overview
2. Follow **COMPLETE_SETUP_GUIDE.md** step by step
3. Run `bash health_check.sh`
4. Run `./run_single_test.sh pod_wrong_image`

### Intermediate
1. Read **COMPLETE_WORKFLOW_GUIDE.md** to understand architecture
2. Review **ASYNC_IMPROVEMENTS.md** for streaming features
3. Run `./run_all_tests.sh`
4. Customize test scenarios

### Advanced
1. Read **COMPLETE_FIXES_SUMMARY.md** for all improvements
2. Modify agents for custom use cases
3. Add new test scenarios
4. Integrate with CI/CD pipelines

---

## 💡 Next Steps

After completing setup:

1. ✅ Run health check: `bash health_check.sh`
2. ✅ Test single scenario: `./run_single_test.sh pod_wrong_image`
3. ✅ Check JIRA ticket created
4. ✅ Verify pod was fixed (not deleted)
5. ✅ Run all scenarios: `./run_all_tests.sh`
6. ✅ Customize for your environment

---

## 📞 Support

For issues or questions:
1. Check **COMPLETE_SETUP_GUIDE.md** → Troubleshooting section
2. Run `bash health_check.sh` to diagnose
3. Check agent logs: `tail -50 k8sgpt_agent.log`
4. Review relevant documentation file

---

**Last Updated:** December 2024  
**Version:** 2.0 (with async/streaming support)
