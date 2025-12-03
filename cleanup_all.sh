#!/bin/bash
echo "🧹 Cleaning up all test resources..."

kubectl delete pod broken-image-pod --ignore-not-found
kubectl delete pod crashloop-pod --ignore-not-found
kubectl delete pod resource-limit-pod --ignore-not-found
kubectl delete pod test-backend --ignore-not-found
kubectl delete service broken-service --ignore-not-found
kubectl delete pvc broken-pvc --ignore-not-found
kubectl delete deployment crashloop-deployment --ignore-not-found
kubectl delete secret unused-secret --ignore-not-found
kubectl delete cronjob broken-cronjob --ignore-not-found

echo "✅ All test resources cleaned up"
