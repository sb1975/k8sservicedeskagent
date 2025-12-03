"""K8sGPT Agent - Simple Flask A2A Server"""
from flask import Flask, jsonify, request, Response
import subprocess
import json
import threading
import time

app = Flask(__name__)

@app.route('/.well-known/agent-card.json')
def agent_card():
    return jsonify({
        "name": "k8sgpt_agent",
        "description": "K8sGPT agent for cluster analysis",
        "url": "http://localhost:8002",
        "skills": [
            {"name": "analyze_cluster", "description": "Analyze K8s cluster for issues"},
            {"name": "get_solution", "description": "Get solution for K8s issue"}
        ]
    })

@app.route('/analyze_cluster', methods=['POST'])
def analyze_cluster():
    try:
        result = subprocess.run(
            ["k8sgpt", "analyze", "--output=json"],
            capture_output=True, text=True, timeout=30
        )
        output = result.stdout if result.stdout.strip() else result.stderr
        if not output.strip():
            output = '{"status":"No issues found","results":[]}'
        return jsonify({"result": output})
    except subprocess.TimeoutExpired:
        return jsonify({"error": "k8sgpt timeout"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_solution', methods=['POST'])
def get_solution():
    data = request.get_json() or {}
    resource_filter = data.get('filter', 'Pod')  # Default to Pod for speed
    result_data = {"solution": None, "error": None}
    
    def run_k8sgpt():
        try:
            cmd = ["k8sgpt", "analyze", "--explain", "--output=json"]
            if resource_filter:
                cmd.extend(["--filter", resource_filter])
            result = subprocess.run(
                cmd,
                capture_output=True, text=True, timeout=120
            )
            lines = result.stdout.split('\n')
            clean_lines = [l for l in lines if not l.startswith('W') and not l.startswith('Debug:')]
            output = '\n'.join(clean_lines).strip()
            result_data["solution"] = output if output and result.returncode == 0 else '{"results":[]}'
        except subprocess.TimeoutExpired:
            result_data["error"] = "Solution timeout"
        except Exception as e:
            result_data["error"] = str(e)
    
    thread = threading.Thread(target=run_k8sgpt)
    thread.start()
    
    # Wait with progress indication
    for i in range(120):
        if not thread.is_alive():
            break
        time.sleep(1)
    
    thread.join(timeout=1)
    
    if result_data["error"]:
        return jsonify({"error": result_data["error"]}), 500
    return jsonify({"solution": result_data["solution"]})

@app.route('/get_solution_stream', methods=['POST'])
def get_solution_stream():
    data = request.get_json() or {}
    resource_filter = data.get('filter', 'Pod')  # Default to Pod for speed
    
    def generate():
        result_data = {"solution": None, "error": None, "done": False}
        
        def run_k8sgpt():
            try:
                cmd = ["k8sgpt", "analyze", "--explain", "--output=json"]
                if resource_filter:
                    cmd.extend(["--filter", resource_filter])
                result = subprocess.run(
                    cmd,
                    capture_output=True, text=True, timeout=120
                )
                lines = result.stdout.split('\n')
                clean_lines = [l for l in lines if not l.startswith('W') and not l.startswith('Debug:')]
                output = '\n'.join(clean_lines).strip()
                result_data["solution"] = output if output and result.returncode == 0 else '{"results":[]}'
            except Exception as e:
                result_data["error"] = str(e)
            finally:
                result_data["done"] = True
        
        thread = threading.Thread(target=run_k8sgpt)
        thread.start()
        
        elapsed = 0
        while not result_data["done"] and elapsed < 120:
            yield f"data: {{\"status\": \"analyzing\", \"elapsed\": {elapsed}}}\n\n"
            time.sleep(2)
            elapsed += 2
        
        if result_data["error"]:
            yield f"data: {{\"status\": \"error\", \"error\": \"{result_data['error']}\"}}\n\n"
        else:
            solution_json = json.dumps(result_data["solution"])
            yield f"data: {{\"status\": \"complete\", \"solution\": {solution_json}}}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='localhost', port=8002)
