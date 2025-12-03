#!/bin/bash
# Run all test scenarios one by one

export JIRA_URL=https://sudeep-batra.atlassian.net
export JIRA_EMAIL=batrasudeep@gmail.com
export JIRA_API_TOKEN=ATATT3xFfGF0YTIx1kjJuLGKX1HmG1FnLoG5hko1VbxZwgtZB4jeswbDRiVKcu-PB-fLv6Vfha3LefaaW2sz60YpFtuXDyhDKS6UKnw4syeHoXi6XwcQKExpZltiEhXTmQ2Go3YaTSqMZmtEl9y3N86fkqY14YLL9F408-_A5jKHusza0__DLE8=6475A3D3

echo "🚀 Starting K8sGPT Agent..."
/usr/bin/python3 k8sgpt_agent_simple.py > /tmp/k8sgpt_agent.log 2>&1 &
K8S_PID=$!
sleep 3

SCENARIOS=(
    "pod_wrong_image"
    "pod_crashloop"
    "service_no_endpoints"
    "pvc_pending"
    "secret_unused"
    "cronjob_failed"
)

for scenario in "${SCENARIOS[@]}"; do
    echo ""
    echo "========================================"
    echo "Testing: $scenario"
    echo "========================================"
    /usr/bin/python3 test_single_issue.py "$scenario"
    echo ""
    read -p "Press ENTER to continue to next scenario..."
done

echo ""
echo "Stopping K8sGPT Agent..."
kill $K8S_PID 2>/dev/null

echo ""
echo "✅ All tests complete!"
