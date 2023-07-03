import logging
import docker
from kubernetes import client, config
import datetime
from requests import HTTPError

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def restart_deployments_with_new_images():
    # Load the Kubernetes configuration from default location
    config.load_incluster_config()

    # Create an instance of the Kubernetes client
    v1 = client.AppsV1Api()

    # Create an instance of the Docker client
    docker_client = docker.from_env()
    v1Core = client.CoreV1Api()
    # Retrieve all deployments in the cluster
    pods = v1Core.list_pod_for_all_namespaces(watch=False).items
    updated = []

    for pod in pods:
        pod_name = pod.metadata.name
        pod_namespace = pod.metadata.namespace
        deployment = get_deployment_name(v1Core, v1, pod_name, namespace=pod_namespace)
        deployment_name = deployment["deployment_name"]
        deployment_type = deployment["deployment_type"]

        # Retrieve the current image and its SHA used by the deployment
        current_image = pod.spec.containers[0].image
        current_tag = current_image.split(":")[1]
        current_sha = None
        if len(pod.status.container_statuses) > 0 and 'sha256' in pod.status.container_statuses[0].image_id:
            current_sha = pod.status.container_statuses[0].image_id.split('sha256:')[1]

        # Check if a newer version of the image is available
        if deployment_name is not None and current_tag == "latest" and current_sha is not None and is_newer_image_available(docker_client, current_image, current_sha):
            logger.info(f"Newer image available for deployment: {deployment_name}")
            updated.append(deployment_name)

            # Patch the deployment to trigger a restart
            patch = {
                "spec": {
                    "template": {
                        "metadata": {
                            "annotations": {
                                "kubectl.kubernetes.io/restartedAt": str(datetime.datetime.now())
                            }
                        }
                    }
                }
            }
            if deployment_type == "ReplicaSet":
                v1.patch_namespaced_deployment(name=deployment_name, namespace=pod_namespace, body=patch)
            elif deployment_type == "StatefulSet":
                v1Core.delete_namespaced_pod(pod_name, pod_namespace)

            logger.info(f"Deployment {deployment_name} in namespace {pod.metadata.namespace} restarted.")


def get_deployment_name(v1Core, v1, pod_name, namespace='default'):
    pod = v1Core.read_namespaced_pod(pod_name, namespace)

    owner_references = pod.metadata.owner_references
    deployment_name = None
    deployment_type = None

    for owner_reference in owner_references:
        if owner_reference.kind == 'ReplicaSet':
            replica_set_name = owner_reference.name
            replica_set = v1.read_namespaced_replica_set(replica_set_name, namespace)
            deployment_name = replica_set.metadata.owner_references[0].name
            deployment_type = owner_reference.kind
            break
        if owner_reference.kind == 'StatefulSet':
            deployment_name = owner_reference.name
            deployment_type = owner_reference.kind
            break

    return {"deployment_name": deployment_name, "deployment_type": deployment_type}


def get_image_sha(docker_client, image):
    # Retrieve the Docker image object
    try:
        docker_client.images.pull(image)
    except HTTPError:
        logger.error(f"Error fetching {image}")
        return None
    image_obj = docker_client.images.get(image)

    # Retrieve the SHA of the image
    if image_obj and "RepoDigests" in image_obj.attrs:
        repo_digests = image_obj.attrs["RepoDigests"]
        if repo_digests:
            return repo_digests[0].split("@sha256:")[1]

    # Return None if the image SHA could not be retrieved
    return None


def is_newer_image_available(docker_client, current_image, current_sha):
    # Retrieve the SHA of the latest image
    latest_sha = get_image_sha(docker_client, current_image)
    logger.debug(f"Latest SHA for image {current_image} is {latest_sha}. Current one is {current_sha}.")
    if latest_sha == current_sha:
        logger.info(f"No update available for image {current_image}. Skipping")
    else:
        logger.info(f"Update available for image {current_image}")
    if latest_sha is None or current_sha is None:
        return False
    # Compare the SHA values
    return latest_sha and latest_sha != current_sha


def gotify_notify(updated):
    if 'GOTIFY_URL' not in os.environ:
        logger.info('Gotify URL not set, skipping notifications')
        return
    updated_string = ','.join(updated)
    gotify_url = os.environ.get('GOTIFY_URL')
    gotify_payload = {
            'title': f'Kube updater',
            'message': f'Applications {updated_string} were updated',
            'priority': 5, 
        }

    if not gotify_url:
        raise RuntimeError('Gotify URL not provided')

    try:
        response = requests.post(gotify_url, json=gotify_payload)
        response.raise_for_status()
        print('Message sent to Gotify successfully!')
    except requests.exceptions.RequestException as e:
        print(f'Failed to send message to Gotify: {e}')
        


if __name__ == '__main__':
    restart_deployments_with_new_images()
