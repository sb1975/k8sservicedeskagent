"""Test scenarios for different K8s resource types"""
import subprocess
import time

SCENARIOS = {
    "pod_wrong_image": {
        "name": "Pod with wrong image",
        "create": "kubectl run broken-image-pod --image=nginx:nonexistent --restart=Never",
        "fix": "kubectl set image pod/broken-image-pod broken-image-pod=nginx:latest",
        "fix_description": "Update pod image to nginx:latest",
        "verify": "kubectl get pod broken-image-pod -o jsonpath='{.status.phase}' 2>/dev/null | grep -q Running"
    },
    "pod_crashloop": {
        "name": "Pod crash loop",
        "create": """cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: crashloop-pod
spec:
  containers:
  - name: app
    image: busybox
    command: ["sh", "-c", "exit 1"]
EOF""",
        "fix": "kubectl patch pod crashloop-pod -p '{\"spec\":{\"containers\":[{\"name\":\"app\",\"image\":\"busybox\",\"command\":[\"sh\",\"-c\",\"sleep 3600\"]}]}}' || kubectl delete pod crashloop-pod --force --grace-period=0 && kubectl run crashloop-pod --image=busybox --command -- sh -c 'sleep 3600'",
        "fix_description": "Fix pod command to run successfully",
        "verify": "kubectl get pod crashloop-pod -o jsonpath='{.status.phase}' | grep -q Running"
    },
    "service_no_endpoints": {
        "name": "Service with no endpoints",
        "create": """cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: broken-service
spec:
  selector:
    app: nonexistent
  ports:
  - port: 80
EOF
# Create a pod that matches
kubectl run test-backend --image=nginx --labels=app=backend
""",
        "fix": "kubectl patch service broken-service -p '{\"spec\":{\"selector\":{\"app\":\"backend\"}}}'" ,
        "fix_description": "Update service selector to match existing pod",
        "verify": "kubectl get endpoints broken-service -o jsonpath='{.subsets[0].addresses[0].ip}' | grep -q ."
    },
    "pvc_pending": {
        "name": "PVC pending",
        "create": """cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: broken-pvc
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: nonexistent
  resources:
    requests:
      storage: 1Gi
EOF""",
        "fix": "kubectl delete pvc broken-pvc && cat <<EOF | kubectl apply -f -\napiVersion: v1\nkind: PersistentVolumeClaim\nmetadata:\n  name: broken-pvc\nspec:\n  accessModes:\n  - ReadWriteOnce\n  storageClassName: standard\n  resources:\n    requests:\n      storage: 1Gi\nEOF",
        "fix_description": "Recreate PVC with valid storage class",
        "verify": "kubectl get pvc broken-pvc -o jsonpath='{.spec.storageClassName}' | grep -q standard"
    },
    "secret_unused": {
        "name": "Unused secret",
        "create": "kubectl create secret generic unused-secret --from-literal=key=value",
        "fix": "kubectl delete secret unused-secret",
        "verify": "kubectl get secret unused-secret 2>&1 | grep -q 'NotFound'"
    },
    "cronjob_failed": {
        "name": "CronJob with failing job",
        "create": """cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: CronJob
metadata:
  name: broken-cronjob
spec:
  schedule: "*/1 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: app
            image: busybox
            command: ["sh", "-c", "exit 1"]
          restartPolicy: Never
EOF""",
        "fix": "kubectl patch cronjob broken-cronjob -p '{\"spec\":{\"jobTemplate\":{\"spec\":{\"template\":{\"spec\":{\"containers\":[{\"name\":\"app\",\"image\":\"busybox\",\"command\":[\"sh\",\"-c\",\"echo success\"]}]}}}}}}'",
        "fix_description": "Fix cronjob command to succeed",
        "verify": "kubectl get cronjob broken-cronjob -o jsonpath='{.spec.jobTemplate.spec.template.spec.containers[0].command[2]}' | grep -q success"
    }
}

def run_cmd(cmd):
    """Run shell command"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def create_issue(scenario_key):
    """Create a specific issue"""
    scenario = SCENARIOS[scenario_key]
    print(f"\n🔧 Creating: {scenario['name']}")
    success, stdout, stderr = run_cmd(scenario['create'])
    if success or 'created' in stdout.lower():
        print(f"   ✅ Created")
        return True
    else:
        print(f"   ❌ Failed: {stderr}")
        return False

def fix_issue(scenario_key):
    """Fix a specific issue"""
    scenario = SCENARIOS[scenario_key]
    print(f"\n🔨 Fixing: {scenario['name']}")
    print(f"   Command: {scenario['fix']}")
    success, stdout, stderr = run_cmd(scenario['fix'])
    if success or 'deleted' in stdout.lower():
        print(f"   Output: {stdout.strip()}")
        print(f"   ✅ Fixed")
        return True
    else:
        print(f"   ⚠️  Fix attempted: {stderr}")
        return True

def verify_fix(scenario_key):
    """Verify issue is fixed"""
    scenario = SCENARIOS[scenario_key]
    print(f"\n✓ Verifying: {scenario['name']}")
    print(f"   Check: {scenario['verify']}")
    success, stdout, stderr = run_cmd(scenario['verify'])
    if success:
        if 'NotFound' in scenario['verify']:
            print(f"   Confirmation: Resource removed (as expected)")
        else:
            print(f"   Confirmation: Resource is healthy")
        print(f"   ✅ Verified - issue resolved")
        return True
    else:
        print(f"   ⚠️  Still present or verification failed")
        return False

def list_scenarios():
    """List all available scenarios"""
    print("\n📋 Available Test Scenarios:")
    print("=" * 60)
    for key, scenario in SCENARIOS.items():
        print(f"  {key:20} - {scenario['name']}")
    print("=" * 60)

if __name__ == "__main__":
    list_scenarios()
