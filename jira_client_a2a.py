"""JIRA Client using A2A Protocol"""
import requests

class JiraClient:
    def __init__(self, base_url="http://localhost:8003"):
        self.base_url = base_url
    
    def create_issue(self, project, summary, description, issue_type="Bug"):
        try:
            resp = requests.post(
                f"{self.base_url}/create_issue",
                json={
                    "project": project,
                    "summary": summary,
                    "description": description
                },
                timeout=30
            )
            if resp.status_code == 200:
                result = resp.json()
                print(f"   ✅ JIRA: Created {result.get('key')}")
                return result
            else:
                print(f"   ❌ JIRA Error: {resp.text}")
                return {"error": resp.text}
        except Exception as e:
            return {"error": str(e)}
    
    def update_issue(self, issue_key, comment=None, status=None):
        if comment:
            try:
                resp = requests.post(
                    f"{self.base_url}/update_issue",
                    json={"issue_key": issue_key, "comment": comment},
                    timeout=30
                )
                if resp.status_code == 200:
                    print(f"   ✅ JIRA: Added comment to {issue_key}")
            except Exception as e:
                print(f"   ❌ Comment error: {e}")
        
        if status and status.lower() == "done":
            try:
                resp = requests.post(
                    f"{self.base_url}/close_issue",
                    json={"issue_key": issue_key, "comment": ""},
                    timeout=30
                )
                if resp.status_code == 200:
                    print(f"   ✅ JIRA: Updated {issue_key} status to Done")
            except Exception as e:
                print(f"   ❌ Status error: {e}")
        
        return {"status": "updated"}
    
    def get_issue(self, issue_key):
        # Not implemented in A2A server yet
        return {"key": issue_key}
