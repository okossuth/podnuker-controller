import time
import logging
import kubernetes
from kubernetes.client.rest import ApiException


kubernetes.config.load_incluster_config()

logging.basicConfig(level=logging.INFO)

api_instance = kubernetes.client.CoreV1Api()

namespaces=["default", "keda"]

while True: 
    for namespace in namespaces:
        try:
            ret = api_instance.list_namespaced_pod(namespace, watch=False)
        except ApiException as e:
            #print("Exception when calling CoreV1Api->list_namespaced_pod: %s\n" % e)
            logging.info(f"Exception when calling CoreV1Api->list_namespaced_pod: %s\n", e)
            break

        for i in ret.items:
            if i.status.reason == "Evicted":
                #print (i.metadata.name, i.status.reason)
                logging.info(f"Pod: %s - Status: %s", i.metadata.name, i.status.reason)
                try:
                    #print("Deleting Evicted Pod %s" % i.metadata.name)
                    logging.info(f"Deleting Evicted Pod %s", i.metadata.name)
                    api_response = api_instance.delete_namespaced_pod(i.metadata.name, namespace)
                    print(api_response)
                except ApiException as e:
                    #print("Exception when calling CoreV1Api->delete_namespaced_pod: %s\n" % e)
                    logging.info(f"Exception when calling CoreV1Api->delete_namespaced_pod: %s\n", e)
        logging.info(f"All pods are running fine in namespace %s", namespace)
        
    time.sleep(1800)
