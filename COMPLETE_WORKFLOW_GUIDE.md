# Complete K8s Issue Resolution Workflow Guide

## System Architecture

### Three Agents System

```
┌─────────────────────────────────────────────────────────────────┐
│                  K8s Service Desk Agent                         │
│                  (Customer Support Agent)                       │
│                                                                 │
│  • Coordinates entire workflow                                  │
│  • Executes kubectl commands                                    │
│  • Manages JIRA lifecycle                                       │
│  • Verifies fixes                                               │
└────────────┬──────────────────────────────────┬─────────────────┘
             │                                   │
             │ Agent2Agent (A2A) Protocol        │ Agent2Agent (A2A) Protocol
             │ (HTTP/JSON)                       │ (HTTP/JSON)
             │                                   │
    ┌────────▼────────┐                 ┌───────▼────────┐
    │  K8sGPT AGENT   │                 │  JIRA AGENT    │
    │  (Port 8002)    │                 │  (Port 8003)   │
    │                 │                 │                │
    │  • Analyzes     │                 │  • Creates     │
    │    cluster      │                 │    issues      │
    │  • Detects      │                 │  • Updates     │
    │    issues       │                 │    tickets     │
    │  • Provides     │                 │  • Closes      │
    │    solutions    │                 │    tickets     │
    └─────────────────┘                 └────────┬───────┘
                                                 │
                                                 │ REST API
                                                 │ (HTTP/JSON)
                                                 │
                                        ┌────────▼────────┐
                                        │  Atlassian      │
                                        │  JIRA Cloud     │
                                        └─────────────────┘
```

## Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: ERROR INJECTION                                          │
│ User/Script creates misconfigured K8s resource                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: ERROR MANIFESTATION                                      │
│ K8s resource enters error state (ImagePullBackOff, Pending, etc)│
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: DETECTION                                                │
│                                                                   │
│ Orchestrator ──────► K8sGPT Agent (A2A)                         │
│                      │                                            │
│                      ├─► Runs: k8sgpt analyze --output=json     │
│                      │                                            │
│                      └─► Returns: JSON with all cluster issues   │
│                                                                   │
│ Orchestrator ◄────── K8sGPT Agent                               │
│   │                                                               │
│   └─► Parses JSON and finds specific issue                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: JIRA TICKET CREATION                                     │
│                                                                   │
│ Orchestrator ──────► JIRA Agent (A2A)                           │
│                      │                                            │
│   Sends:             ├─► POST /create_issue                      │
│   • Project: KAN     ├─► Body: {project, summary, description}  │
│   • K8sGPT details   │                                            │
│                      └─► JIRA Agent → Atlassian REST API        │
│                           Creates ticket in Atlassian            │
│                                                                   │
│ Orchestrator ◄────── JIRA Agent                                 │
│   │                                                               │
│   └─► Receives: Issue Key (e.g., KAN-11)                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: GET AI-POWERED SOLUTION                                  │
│                                                                   │
│ Orchestrator ──────► K8sGPT Agent (A2A)                         │
│                      │                                            │
│                      ├─► Runs: k8sgpt analyze --explain          │
│                      │    Uses AI to generate intelligent fix    │
│                      │                                            │
│                      └─► Returns: Step-by-step solution          │
│                           Example: "Update image to nginx:latest"│
│                                                                   │
│ Orchestrator ◄────── K8sGPT Agent                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: APPLY FIX (Based on K8sGPT AI Solution)                 │
│                                                                   │
│ Orchestrator applies fix based on K8sGPT recommendation:         │
│   • Intelligent: kubectl set image pod/name app=nginx:latest     │
│   • Fallback: kubectl delete pod <name>                          │
│                                                                   │
│ K8sGPT AI provides context-aware solutions:                      │
│   - Wrong image → Fix image tag                                  │
│   - Resource limits → Adjust limits                              │
│   - Missing config → Add configuration                           │
│                                                                   │
│ Result: Issue resolved intelligently, not just deleted           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 7: VERIFY FIX                                               │
│                                                                   │
│ Orchestrator executes verification:                              │
│   • kubectl get <resource> <name>                                │
│   • Expects: "NotFound" error                                    │
│                                                                   │
│ Result: Confirms resource no longer exists                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 8: UPDATE JIRA                                              │
│                                                                   │
│ Orchestrator ──────► JIRA Agent (A2A)                           │
│                      │                                            │
│   Sends:             ├─► POST /update_issue                      │
│   • Issue key        ├─► Body: {issue_key, comment}             │
│   • Fix details      │                                            │
│                      └─► JIRA Agent → Atlassian REST API        │
│                           Adds comment to ticket                 │
│                                                                   │
│ Orchestrator ◄────── JIRA Agent                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 9: CLOSE JIRA                                               │
│                                                                   │
│ Orchestrator ──────► JIRA Agent (A2A)                           │
│                      │                                            │
│   Sends:             ├─► POST /close_issue                       │
│   • Issue key        ├─► Body: {issue_key, comment}             │
│   • Final comment    │                                            │
│                      └─► JIRA Agent → Atlassian REST API        │
│                           Closes ticket (status=Done)            │
│                                                                   │
│ Orchestrator ◄────── JIRA Agent                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
                   ✅ COMPLETE
```

## Agent Communication Details

### 1. K8sGPT Agent (Agent2Agent Protocol)

**Technology:** Flask HTTP Server on port 8002

**Endpoints:**
```
GET  /.well-known/agent-card.json  → Agent metadata
POST /analyze_cluster               → Fast detection (~10s, no AI)
POST /get_solution                  → AI-powered solution (~120s, intelligent)
```

**Key Difference:**
- `/analyze_cluster`: Uses `k8sgpt analyze --output=json` (fast, detection only)
- `/get_solution`: Uses `k8sgpt analyze --explain` (slow, AI-powered fixes)

**Request Example:**
```bash
POST http://localhost:8002/analyze_cluster
Content-Type: application/json
Body: {}
```

**Response Example (analyze_cluster - Fast):**
```json
{
  "result": {
    "status": "ProblemDetected",
    "problems": 3,
    "results": [{
      "kind": "Pod",
      "name": "default/broken-image-pod",
      "error": [{
        "Text": "Back-off pulling image \"nginx:nonexistent\""
      }]
    }]
  }
}
```

**Response Example (get_solution - AI-Powered):**
```json
{
  "solution": {
    "results": [{
      "kind": "Pod",
      "name": "default/broken-image-pod",
      "details": "The image 'nginx:nonexistent' cannot be found in the registry. To fix: 1) Update pod spec with valid image: kubectl set image pod/broken-image-pod app=nginx:latest, or 2) Check image name spelling, or 3) Verify registry access."
    }]
  }
}
```

### 2. JIRA Agent (Agent2Agent Protocol)

**Technology:** Flask HTTP Server on port 8003

**Endpoints:**
```
GET  /.well-known/agent-card.json  → Agent metadata
POST /create_issue                  → Create JIRA issue
POST /update_issue                  → Update JIRA issue
POST /close_issue                   → Close JIRA issue
```

**Backend:** Uses Atlassian REST API v3 internally

**Request Example:**
```bash
POST http://localhost:8003/create_issue
Content-Type: application/json
Body: {
  "project": "KAN",
  "summary": "Pod broken-image-pod issue",
  "description": "Issue details..."
}
```

**Response Example:**
```json
{
  "key": "KAN-12",
  "id": "10042"
}
```

### 3. Orchestrator Agent

**Technology:** Python script with LangChain (optional)

**Responsibilities:**
- Coordinates workflow between K8sGPT and JIRA agents
- Executes kubectl commands
- Parses K8sGPT output
- Formats JIRA tickets
- Verifies fixes

**Tools:**
```python
- analyze_k8s()      → Calls K8sGPT Agent
- create_jira()      → Calls JIRA Agent
- update_jira()      → Calls JIRA Agent
- apply_fix()        → Executes kubectl
- verify_fix()       → Executes kubectl
```

## Step-by-Step Execution Guide

### Prerequisites

1. **K8s Cluster Running**
   ```bash
   kubectl cluster-info
   ```

2. **k8sgpt CLI Installed**
   ```bash
   k8sgpt version
   ```

3. **JIRA Credentials Configured**
   ```bash
   source ~/.env.jira
   ```

4. **K8sGPT Agent Running**
   ```bash
   /usr/bin/python3 k8sgpt_agent_simple.py &
   ```

### Test Single Issue

```bash
# Clean up any existing test resources
./cleanup_all.sh

# Run single test
./run_single_test.sh pod_wrong_image
```

### Available Test Scenarios

| Scenario | Resource Type | Issue | Fix |
|----------|--------------|-------|-----|
| `pod_wrong_image` | Pod | ImagePullBackOff | Delete pod |
| `pod_crashloop` | Pod | CrashLoopBackOff | Delete pod |
| `service_no_endpoints` | Service | No endpoints | Delete service |
| `pvc_pending` | PVC | Pending state | Delete PVC |
| `secret_unused` | Secret | Unused resource | Delete secret |
| `cronjob_failed` | CronJob | Failed jobs | Delete cronjob |

### Test All Scenarios

```bash
./run_all_tests.sh
```

## Detailed Example: Pod with Wrong Image

### 1. Error Injection
```bash
kubectl run broken-image-pod --image=nginx:nonexistent --restart=Never
```

**Result:** Pod created with non-existent image

### 2. Error Manifestation (15 seconds)
```bash
kubectl get pod broken-image-pod
# STATUS: ImagePullBackOff
```

**Result:** Pod enters error state

### 3. Detection via K8sGPT Agent

**Orchestrator sends:**
```
POST http://localhost:8002/analyze_cluster
```

**K8sGPT Agent executes:**
```bash
k8sgpt analyze --output=json
```

**K8sGPT Agent returns:**
```json
{
  "kind": "Pod",
  "name": "default/broken-image-pod",
  "error": [{
    "Text": "Back-off pulling image \"nginx:nonexistent\": ErrImagePull"
  }]
}
```

**Orchestrator parses:** Finds specific pod "broken-image-pod"

### 4. JIRA Ticket Creation

**Orchestrator sends to JIRA Agent:**
```python
project = "KAN"
summary = "Pod broken-image-pod issue"
description = """
Issue Type: Pod with wrong image
Detected by: K8sGPT Agent

Resource Details:
- Kind: Pod
- Name: default/broken-image-pod
- Error: Back-off pulling image "nginx:nonexistent"

K8sGPT Analysis:
{full JSON}
"""
```

**JIRA Agent creates:** Ticket KAN-12

**Result:** https://sudeep-batra.atlassian.net/browse/KAN-12

### 5. Apply Fix

**Orchestrator executes:**
```bash
kubectl delete pod broken-image-pod
```

**Output:**
```
pod "broken-image-pod" deleted
```

**Result:** Pod removed from cluster

### 6. Verify Fix

**Orchestrator executes:**
```bash
kubectl get pod broken-image-pod
```

**Expected output:**
```
Error from server (NotFound): pods "broken-image-pod" not found
```

**Result:** Confirmed pod no longer exists

### 7. Update JIRA

**Orchestrator sends to JIRA Agent:**
```python
issue_key = "KAN-12"
comment = """
Fix Applied by Orchestrator Agent

📋 Issue: Pod with wrong image
🔧 Action Taken: kubectl delete pod broken-image-pod
📊 Result: Fix applied successfully
✓ Verification: ✅ Verified - issue resolved

🤖 Workflow:
- Detected by: K8sGPT Agent
- Fixed by: Orchestrator Agent (kubectl command)
- Verified by: Orchestrator Agent
"""
```

**Result:** Comment added to KAN-12

### 8. Close JIRA

**Orchestrator sends to JIRA Agent:**
```python
issue_key = "KAN-12"
comment = """
✅ Issue Resolved

📝 Summary:
- Issue Type: Pod with wrong image
- Resource: Pod broken-image-pod
- Root Cause: Back-off pulling image "nginx:nonexistent"

🔄 Resolution Workflow:
1. K8sGPT Agent detected the issue
2. JIRA Agent created ticket KAN-12
3. Orchestrator Agent applied fix: kubectl delete pod broken-image-pod
4. Orchestrator Agent verified resolution
5. JIRA Agent closed ticket

✓ Final Status: ✅ Verified - issue resolved
"""
status = "Done"
```

**Result:** Ticket KAN-12 closed

## Agent Interaction Summary

```
User/Script
    │
    ├─► Creates K8s issue
    │
    ▼
Orchestrator Agent
    │
    ├─► Calls K8sGPT Agent (A2A) ──► Analyzes cluster
    │                                 Returns issues
    │
    ├─► Calls JIRA Agent (A2A) ────► Creates ticket
    │                                 Returns issue key
    │
    ├─► Executes kubectl ──────────► Applies fix
    │
    ├─► Executes kubectl ──────────► Verifies fix
    │
    ├─► Calls JIRA Agent (A2A) ────► Updates ticket
    │
    └─► Calls JIRA Agent (A2A) ────► Closes ticket
```

## Key Features

✅ **Automated Detection** - K8sGPT finds issues automatically
✅ **Issue Tracking** - JIRA maintains complete audit trail
✅ **Automated Remediation** - Orchestrator applies fixes
✅ **Verification** - Confirms issues are resolved
✅ **Multi-Agent** - Three specialized agents working together
✅ **Protocol Agnostic** - A2A for K8sGPT, REST for JIRA
✅ **Extensible** - Easy to add new issue types

## Files Reference

- `k8sgpt_agent_simple.py` - K8sGPT A2A server
- `jira_real.py` - JIRA REST client
- `test_scenarios.py` - Issue definitions
- `test_single_issue.py` - Orchestrator workflow
- `run_single_test.sh` - Test runner
- `cleanup_all.sh` - Resource cleanup

## Troubleshooting

**K8sGPT Agent not running:**
```bash
/usr/bin/python3 k8sgpt_agent_simple.py &
```

**JIRA credentials not loaded:**
```bash
source ~/.env.jira
```

**Issue not detected:**
- Wait longer (some issues take time to manifest)
- Check k8sgpt can detect the issue type
- Verify resource name matches

**Fix verification fails:**
- Check kubectl access
- Verify resource was actually deleted
- Check namespace if applicable
