"""Test single issue workflow"""
import sys
import time
import requests
from jira_client_a2a import JiraClient
from test_scenarios import SCENARIOS, create_issue, fix_issue, verify_fix
import json

def test_single_issue_workflow(scenario_key):
    """Test complete workflow for a single issue type"""
    
    if scenario_key not in SCENARIOS:
        print(f"❌ Unknown scenario: {scenario_key}")
        print("Available:", list(SCENARIOS.keys()))
        return False
    
    scenario = SCENARIOS[scenario_key]
    print("\n" + "="*60)
    print(f"Testing: {scenario['name']}")
    print("="*60)
    
    # Step 1: Create the issue
    print("\n[Step 1] Creating K8s Issue")
    print("-" * 60)
    if not create_issue(scenario_key):
        return False
    
    print("\n⏳ Waiting for issue to manifest", end='', flush=True)
    for i in range(15):
        print('.', end='', flush=True)
        time.sleep(1)
    print(" Done!")
    
    input("\nPress ENTER to continue to analysis...")
    
    # Step 2: Analyze with K8sGPT
    print("\n[Step 2] Analyzing with K8sGPT Agent")
    print("-" * 60)
    print("🤖 Agent: K8sGPT Agent")
    print("📤 Input: analyze_cluster")
    
    try:
        resp = requests.post("http://localhost:8002/analyze_cluster", timeout=60)
        result = resp.json()
        analysis = result.get('result', '{}')
        print(f"📥 Output: {len(analysis)} chars")
        
        # Parse and find our specific issue
        analysis_json = json.loads(analysis)
        found_issue = None
        
        # Extract expected resource name from scenario
        if 'broken-image-pod' in scenario['create']:
            expected_name = 'broken-image-pod'
        elif 'crashloop-pod' in scenario['create']:
            expected_name = 'crashloop-pod'
        elif 'broken-service' in scenario['create']:
            expected_name = 'broken-service'
        elif 'broken-pvc' in scenario['create']:
            expected_name = 'broken-pvc'
        elif 'unused-secret' in scenario['create']:
            expected_name = 'unused-secret'
        elif 'broken-cronjob' in scenario['create']:
            expected_name = 'broken-cronjob'
        else:
            expected_name = scenario_key.replace('_', '-')
        
        # Search for the specific resource
        for item in analysis_json.get('results', []):
            item_name = item.get('name', '').lower()
            if expected_name in item_name:
                found_issue = item
                print(f"   Matched: {item['kind']} {item['name']}")
                break
        
        if found_issue:
            issue_text = found_issue['error'][0]['Text'] if found_issue.get('error') else 'Issue detected'
            print(f"✅ Found issue: {found_issue['kind']} {found_issue['name']}")
            print(f"   Error: {issue_text}")
            print(f"   Details: Resource in error state, requires remediation")
        else:
            print(f"❌ Specific issue not found in K8sGPT analysis")
            print(f"   Expected: {scenario['name']}")
            print(f"   K8sGPT found {len(analysis_json.get('results', []))} other issues")
            print(f"\n💡 Possible reasons:")
            print(f"   - Issue hasn't manifested yet (wait longer)")
            print(f"   - K8sGPT doesn't detect this issue type")
            print(f"   - Resource name mismatch")
            print(f"\n🛑 Stopping workflow - cannot proceed without detecting the issue")
            return False
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        print(f"   Raw output: {result.get('result', 'N/A')[:200]}")
        return False
    
    input("\nPress ENTER to continue to get solution...")
    
    # Step 3: Get Solution from K8sGPT
    print("\n[Step 3] Getting Solution from K8sGPT Agent")
    print("-" * 60)
    print("🤖 Agent: K8sGPT Agent")
    print(f"📤 Input: get_solution for {found_issue.get('kind')}")
    print("   Method: AI-powered analysis with --explain flag")
    print("⏳ Analyzing with AI model (streaming progress)...")
    
    try:
        # Try streaming endpoint first for live progress
        try:
            # Pass resource kind as filter to speed up analysis
            resource_kind = found_issue.get('kind', 'Pod')
            resp = requests.post(
                "http://localhost:8002/get_solution_stream",
                json={"filter": resource_kind},
                stream=True,
                timeout=150
            )
            
            solution_text = None
            for line in resp.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data = json.loads(line_str[6:])
                        if data.get('status') == 'analyzing':
                            elapsed = data.get('elapsed', 0)
                            print(f"\r   ⏱️  Elapsed: {elapsed}s - AI model processing...", end='', flush=True)
                        elif data.get('status') == 'complete':
                            solution_text = data.get('solution')
                            print("\r   ✅ Analysis complete!" + " " * 40)
                            break
                        elif data.get('status') == 'error':
                            print(f"\r   ❌ Error: {data.get('error')}" + " " * 40)
                            raise Exception(data.get('error'))
        except:
            # Fallback to regular endpoint
            print("\r   Using standard endpoint...", end='', flush=True)
            resource_kind = found_issue.get('kind', 'Pod')
            resp = requests.post(
                "http://localhost:8002/get_solution",
                json={"filter": resource_kind},
                timeout=150
            )
            solution_result = resp.json()
            solution_text = solution_result.get('solution', '{}')
            print(" Done!")
        
        if not solution_text:
            solution_result = resp.json() if hasattr(resp, 'json') else {}
            solution_text = solution_result.get('solution', '{}')
        # Parse solution
        try:
            if isinstance(solution_text, str):
                solution_json = json.loads(solution_text)
            else:
                solution_json = solution_text
            if solution_json.get('results'):
                for res in solution_json['results']:
                    if found_issue.get('name', '') in res.get('name', ''):
                        solution_details = res.get('details', 'No detailed solution')
                        break
                else:
                    solution_details = solution_json['results'][0].get('details', 'No solution') if solution_json['results'] else 'No solution'
            else:
                solution_details = 'No solution available'
        except:
            solution_details = solution_text[:500] if solution_text else 'No solution'
        
        print(f"📥 Output: Solution received")
        print(f"   Recommendation: {solution_details[:200]}...")
        
    except Exception as e:
        print(f"\n⚠️  Solution retrieval failed: {e}")
        solution_details = "Manual investigation required"
    
    input("\nPress ENTER to continue to JIRA creation...")
    
    # Step 4: Create JIRA (was Step 3)
    print("\n[Step 3] Creating JIRA Issue")
    print("-" * 60)
    print("🤖 Agent: JIRA Agent")
    
    # Create concise title
    resource_name = found_issue.get('name', 'unknown').split('/')[-1]
    kind = found_issue.get('kind', 'Resource')
    title = f"{kind} {resource_name} issue"
    
    print(f"📤 Input:")
    print(f"   Project: KAN")
    print(f"   Summary: {title}")
    
    jira = JiraClient()
    jira_result = jira.create_issue(
        project="KAN",
        summary=title,
        description=f"""Issue Type: {scenario['name']}
Detected by: K8sGPT Agent

Resource Details:
- Kind: {found_issue.get('kind', 'Unknown')}
- Name: {found_issue.get('name', 'Unknown')}
- Error: {found_issue.get('error', [{}])[0].get('Text', 'No error text') if found_issue.get('error') else 'No error details'}

K8sGPT Recommended Solution:
{solution_details[:800]}

K8sGPT Analysis:
{json.dumps(found_issue, indent=2)}

Note: This issue is specific to {scenario['name']}. Total cluster issues detected: {analysis_json.get('problems', 'unknown')}"""
    )
    
    if "error" in jira_result:
        print(f"❌ JIRA creation failed: {jira_result['error']}")
        return False
    
    issue_key = jira_result.get('key')
    print(f"📥 Output: {issue_key}")
    print(f"✅ JIRA created: https://sudeep-batra.atlassian.net/browse/{issue_key}")
    
    input("\nPress ENTER to continue to fix...")
    
    # Step 5: Apply Fix (was Step 4)
    print("\n[Step 4] Applying Fix")
    print("-" * 60)
    print("🤖 Agent: Orchestrator")
    print(f"📤 Input: {scenario['fix']}")
    print(f"   Method: {scenario.get('fix_description', 'Apply fix to resolve issue')}")
    print(f"   Expected: Resource will be corrected")
    
    if fix_issue(scenario_key):
        print("✅ Fix applied successfully")
        print(f"   Action: Executed '{scenario['fix']}'")
        print(f"   Result: Fix completed")
        fix_details = f"Fix applied: {scenario['fix']}"
    else:
        print("⚠️  Fix may have failed")
        fix_details = f"Fix attempted: {scenario['fix']}"
    
    input("\nPress ENTER to continue to verification...")
    
    # Step 6: Verify Fix (was Step 5)
    print("\n[Step 5] Verifying Fix")
    print("-" * 60)
    print("🤖 Agent: Orchestrator")
    print(f"📤 Input: {scenario['verify']}")
    print(f"   Method: Check resource health status")
    
    # Extract resource type and name for display
    resource_type = found_issue.get('kind', 'Resource')
    resource_name = found_issue.get('name', 'unknown').split('/')[-1]
    
    if verify_fix(scenario_key):
        verification = "✅ Verified - issue resolved"
        if 'NotFound' in scenario['verify']:
            print(f"   Result: {resource_type} '{resource_name}' removed from cluster")
        else:
            print(f"   Result: {resource_type} '{resource_name}' is now healthy")
        print(f"   Status: Issue successfully resolved")
    else:
        verification = "⚠️  Verification incomplete"
        print(f"   Result: Resource may still have issues")
    
    print(verification)
    
    input("\nPress ENTER to continue to JIRA update...")
    
    # Step 7: Update JIRA (was Step 6)
    print("\n[Step 6] Updating JIRA")
    print("-" * 60)
    print("🤖 Agent: JIRA Agent")
    print(f"📤 Input: Update {issue_key}")
    
    jira.update_issue(
        issue_key=issue_key,
        comment=f"""Fix Applied by Orchestrator Agent

📋 Issue: {scenario['name']}
💡 K8sGPT Recommendation: {solution_details[:300]}
🔧 Action Taken: {scenario['fix']}
📊 Result: {fix_details}
✓ Verification: {verification}

🤖 Workflow:
- Detected by: K8sGPT Agent
- Solution by: K8sGPT Agent (AI-powered)
- Fixed by: Orchestrator Agent (kubectl command)
- Verified by: Orchestrator Agent
"""
    )
    print("✅ JIRA updated")
    
    input("\nPress ENTER to close JIRA...")
    
    # Step 8: Close JIRA (was Step 7)
    print("\n[Step 7] Closing JIRA")
    print("-" * 60)
    print("🤖 Agent: JIRA Agent")
    
    jira.update_issue(
        issue_key=issue_key,
        comment=f"""✅ Issue Resolved

📝 Summary:
- Issue Type: {scenario['name']}
- Resource: {found_issue.get('kind', 'Unknown')} {found_issue.get('name', 'Unknown').split('/')[-1]}
- Root Cause: {found_issue.get('error', [{}])[0].get('Text', 'N/A')[:100] if found_issue.get('error') else 'N/A'}

💡 K8sGPT Solution:
{solution_details[:400]}

🔄 Resolution Workflow:
1. K8sGPT Agent detected the issue
2. K8sGPT Agent provided AI-powered solution
3. JIRA Agent created ticket {issue_key}
4. Orchestrator Agent applied fix: {scenario['fix']}
5. Orchestrator Agent verified resolution
6. JIRA Agent closed ticket

✓ Final Status: {verification}
""",
        status="Done"
    )
    print(f"✅ JIRA closed: https://sudeep-batra.atlassian.net/browse/{issue_key}")
    
    print("\n" + "="*60)
    print("✅ Workflow Complete!")
    print("="*60)
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_single_issue.py <scenario>")
        print("\nAvailable scenarios:")
        for key, scenario in SCENARIOS.items():
            print(f"  {key:20} - {scenario['name']}")
        sys.exit(1)
    
    scenario = sys.argv[1]
    test_single_issue_workflow(scenario)
