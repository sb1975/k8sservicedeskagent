# K8s Issue Resolution with Multi-Agent System

Automated Kubernetes issue detection, resolution, and tracking using three agents communicating via Agent2Agent (A2A) Protocol.

## Architecture

```
Orchestrator Agent
    ├─► K8sGPT Agent (Agent2Agent Protocol, Port 8002)
    │   - Detects issues
    │   - Provides AI solutions
    │
    └─► JIRA Agent (Agent2Agent Protocol, Port 8003)
        - Creates/updates/closes tickets
        - Connects to Atlassian via REST API
```

## Quick Start

### 1. Setup JIRA Credentials
```bash
export JIRA_URL=https://sudeep-batra.atlassian.net
export JIRA_EMAIL=batrasudeep@gmail.com
export JIRA_API_TOKEN=your-token-here
```

### 2. Test Single Issue
```bash
./run_single_test.sh pod_wrong_image
```

### 3. Test All Issues
```bash
./run_all_tests.sh
```

## Available Test Scenarios

| Scenario | Resource | Issue | Fix |
|----------|----------|-------|-----|
| `pod_wrong_image` | Pod | ImagePullBackOff | Update image tag |
| `pod_crashloop` | Pod | CrashLoopBackOff | Fix command |
| `service_no_endpoints` | Service | No endpoints | Update selector |
| `pvc_pending` | PVC | Pending state | Recreate with valid SC |
| `secret_unused` | Secret | Unused resource | Delete (security) |
| `cronjob_failed` | CronJob | Failed jobs | Fix job command |

## Workflow

1. **Inject Error** - Create misconfigured K8s resource
2. **Detect** - K8sGPT analyzes cluster (fast, ~10s)
3. **Get Solution** - K8sGPT provides AI-powered fix (~30s with streaming)
4. **Create JIRA** - Ticket with full analysis and solution
5. **Apply Intelligent Fix** - Fix root cause (update image, fix selector, etc.)
6. **Verify** - Confirm resource is healthy
7. **Update JIRA** - Add fix details
8. **Close JIRA** - Mark as Done

## Core Files

- `k8sgpt_agent_simple.py` - K8sGPT Agent2Agent server (port 8002)
- `jira_agent_a2a.py` - JIRA Agent2Agent server (port 8003)
- `jira_client_a2a.py` - JIRA client
- `test_scenarios.py` - Issue definitions
- `test_single_issue.py` - Orchestrator workflow
- `run_single_test.sh` - Single test runner
- `run_all_tests.sh` - All tests runner
- `cleanup_all.sh` - Resource cleanup

## Documentation

📚 **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Complete documentation guide

### Quick Links
- **[COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)** - Full installation from scratch ⭐
- **[COMPLETE_WORKFLOW_GUIDE.md](COMPLETE_WORKFLOW_GUIDE.md)** - Architecture & workflow details
- **[ASYNC_IMPROVEMENTS.md](ASYNC_IMPROVEMENTS.md)** - Streaming & performance features
- **[COMPLETE_FIXES_SUMMARY.md](COMPLETE_FIXES_SUMMARY.md)** - All improvements summary

## Requirements

- Kubernetes cluster with kubectl access
- k8sgpt CLI installed
- Ollama with Mistral 7B model
- Python 3 with flask, requests
- JIRA account with API token

**📖 For complete setup instructions, see [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)**
