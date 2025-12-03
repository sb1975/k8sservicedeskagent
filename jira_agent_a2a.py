"""JIRA Agent exposed via Agent2Agent Protocol"""
from flask import Flask, jsonify, request
import requests
import os
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

# JIRA Configuration
JIRA_URL = os.getenv('JIRA_URL', 'https://sudeep-batra.atlassian.net')
JIRA_EMAIL = os.getenv('JIRA_EMAIL', 'batrasudeep@gmail.com')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN', '')

@app.route('/.well-known/agent-card.json')
def agent_card():
    return jsonify({
        "name": "jira_agent",
        "description": "JIRA agent for issue management via Atlassian REST API",
        "url": "http://localhost:8003",
        "skills": [
            {"name": "create_issue", "description": "Create JIRA issue"},
            {"name": "update_issue", "description": "Update JIRA issue with comment"},
            {"name": "close_issue", "description": "Close JIRA issue"}
        ]
    })

@app.route('/create_issue', methods=['POST'])
def create_issue():
    data = request.json
    project = data.get('project', 'KAN')
    summary = data.get('summary', '')
    description = data.get('description', '')
    
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    url = f"{JIRA_URL}/rest/api/3/issue"
    payload = {
        "fields": {
            "project": {"key": project},
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": description}]
                }]
            },
            "issuetype": {"name": "Bug"}
        }
    }
    
    try:
        resp = requests.post(url, json=payload, auth=auth, headers={"Content-Type": "application/json"}, timeout=30)
        if resp.status_code in [200, 201]:
            result = resp.json()
            return jsonify({"key": result.get('key'), "id": result.get('id')})
        else:
            return jsonify({"error": resp.text}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update_issue', methods=['POST'])
def update_issue():
    data = request.json
    issue_key = data.get('issue_key', '')
    comment = data.get('comment', '')
    
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/comment"
    payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [{
                "type": "paragraph",
                "content": [{"type": "text", "text": comment}]
            }]
        }
    }
    
    try:
        resp = requests.post(url, json=payload, auth=auth, headers={"Content-Type": "application/json"}, timeout=30)
        if resp.status_code in [200, 201]:
            return jsonify({"status": "comment_added"})
        else:
            return jsonify({"error": resp.text}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/close_issue', methods=['POST'])
def close_issue():
    data = request.json
    issue_key = data.get('issue_key', '')
    comment = data.get('comment', '')
    
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    
    # Add final comment
    if comment:
        comment_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/comment"
        comment_payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": comment}]
                }]
            }
        }
        requests.post(comment_url, json=comment_payload, auth=auth, headers={"Content-Type": "application/json"}, timeout=30)
    
    # Get transitions
    trans_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/transitions"
    try:
        resp = requests.get(trans_url, auth=auth, headers={"Content-Type": "application/json"}, timeout=30)
        if resp.status_code == 200:
            transitions = resp.json().get('transitions', [])
            trans_id = None
            for t in transitions:
                if t['name'].lower() == 'done' or t['to']['name'].lower() == 'done':
                    trans_id = t['id']
                    break
            
            if trans_id:
                payload = {"transition": {"id": trans_id}}
                resp = requests.post(trans_url, json=payload, auth=auth, headers={"Content-Type": "application/json"}, timeout=30)
                if resp.status_code == 204:
                    return jsonify({"status": "closed"})
        
        return jsonify({"error": "Could not close issue"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='localhost', port=8003)
