#!/usr/bin/env python3
"""Quick test of streaming solution endpoint"""
import requests
import json
import sys

print("Testing K8sGPT streaming solution endpoint...")
print("=" * 60)

try:
    resp = requests.post(
        "http://localhost:8002/get_solution_stream",
        json={},
        stream=True,
        timeout=150
    )
    
    for line in resp.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data = json.loads(line_str[6:])
                status = data.get('status')
                
                if status == 'analyzing':
                    elapsed = data.get('elapsed', 0)
                    print(f"\r⏱️  Analyzing: {elapsed}s elapsed...", end='', flush=True)
                elif status == 'complete':
                    print(f"\r✅ Complete!" + " " * 40)
                    solution = json.loads(data.get('solution', '{}'))
                    print(f"\nResults found: {len(solution.get('results', []))}")
                    for result in solution.get('results', [])[:2]:
                        print(f"\n📋 {result.get('kind')} {result.get('name')}")
                        if result.get('details'):
                            print(f"   Solution: {result['details'][:200]}...")
                    break
                elif status == 'error':
                    print(f"\r❌ Error: {data.get('error')}")
                    sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Streaming test successful!")
    
except Exception as e:
    print(f"\n❌ Test failed: {e}")
    sys.exit(1)
