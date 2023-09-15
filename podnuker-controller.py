import time
import logging
import kubernetes
from kubernetes.client.rest import ApiException

# Load in-cluster configuration for accessing the Kubernetes API from within a pod running inside the cluster
kubernetes.config.load_incluster_config()

# Set the default configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Create api_instance object used to interact with the Kubernetes API for core resources
api_instance = kubernetes.client.CoreV1Api()

#Define K8s namespaces to monitor for evicted pods
namespaces=["default", "keda"]

# Main logic
while True: 
    for namespace in namespaces:
        try:
            # Get list of pods in namespace
            pods = api_instance.list_namespaced_pod(namespace, watch=False)
        except ApiException as e:
            logging.info(f"Exception when calling CoreV1Api->list_namespaced_pod: %s\n", e)
            break

        for pod in pods.items:
            # If pod status is Evicted
            if pod.status.reason == "Evicted" or pod.status.phase == "Failed": 
                logging.info(f"Pod: %s - Status: %s", pod.metadata.name, pod.status.reason)
                try:
                    logging.info(f"Deleting Evicted Pod %s", pod.metadata.name)
                    # Delete pod from namespace
                    api_response = api_instance.delete_namespaced_pod(pod.metadata.name, namespace)
                    logging.info(f"Deletion exit code: %s", api_response.status.message)
                except ApiException as e:
                    logging.info(f"Exception when calling CoreV1Api->delete_namespaced_pod: %s\n", e)
        logging.info(f"All pods are running fine in namespace %s", namespace)
       
    # Sleep for 30 minutes   
    time.sleep(1800)
