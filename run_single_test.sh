#!/bin/bash
# Run single issue test

if [ -z "$1" ]; then
    echo "Usage: ./run_single_test.sh <scenario>"
    echo ""
    echo "Available scenarios:"
    echo "  pod_wrong_image      - Pod with wrong image"
    echo "  pod_crashloop        - Pod crash loop"
    echo "  service_no_endpoints - Service with no endpoints"
    echo "  pvc_pending          - PVC pending"
    echo "  secret_unused        - Unused secret"
    echo "  cronjob_failed       - CronJob with failing job"
    exit 1
fi

export JIRA_URL=https://sudeep-batra.atlassian.net
export JIRA_EMAIL=batrasudeep@gmail.com
export JIRA_API_TOKEN=ATATT3xFfGF0YTIx1kjJuLGKX1HmG1FnLoG5hko1VbxZwgtZB4jeswbDRiVKcu-PB-fLv6Vfha3LefaaW2sz60YpFtuXDyhDKS6UKnw4syeHoXi6XwcQKExpZltiEhXTmQ2Go3YaTSqMZmtEl9y3N86fkqY14YLL9F408-_A5jKHusza0__DLE8=6475A3D3

# Check if K8sGPT agent is running
if ! curl -s http://localhost:8002/.well-known/agent-card.json > /dev/null 2>&1; then
    echo "🚀 Starting K8sGPT Agent..."
    /usr/bin/python3 k8sgpt_agent_simple.py > /tmp/k8sgpt_agent.log 2>&1 &
    K8S_PID=$!
    echo "   PID: $K8S_PID"
    sleep 2
    STARTED_K8S=1
else
    echo "✅ K8sGPT Agent already running"
    STARTED_K8S=0
fi

# Check if JIRA agent is running
if ! curl -s http://localhost:8003/.well-known/agent-card.json > /dev/null 2>&1; then
    echo "🚀 Starting JIRA Agent..."
    /usr/bin/python3 jira_agent_a2a.py > /tmp/jira_agent.log 2>&1 &
    JIRA_PID=$!
    echo "   PID: $JIRA_PID"
    sleep 2
    STARTED_JIRA=1
else
    echo "✅ JIRA Agent already running"
    STARTED_JIRA=0
fi

echo ""
/usr/bin/python3 test_single_issue.py "$1"

if [ $STARTED_K8S -eq 1 ]; then
    echo ""
    echo "Stopping K8sGPT Agent..."
    kill $K8S_PID 2>/dev/null
fi

if [ $STARTED_JIRA -eq 1 ]; then
    echo "Stopping JIRA Agent..."
    kill $JIRA_PID 2>/dev/null
fi
