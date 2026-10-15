# Hospital portal

Vidhanshu 24MIS0483 Assessment IX.

Windows Jenkins pipeline with Clone Code, Build Docker Image, Test Application, Push Image and Deploy Health Check and Automatic Rollback stages.

Jenkins credentials: docker (majorazor registry username and token) and kuberconfig (current Docker Desktop kubeconfig secret file). Existing IDs are reused. Python 3, Git, Docker and kubectl must be available to Jenkins. The Jenkinsfile includes the Docker Desktop tools path used on this laptop.

Image tags combine build number and Git commit. /release.txt stores that exact image identity. Container tests verify HTTP, content and identity. Kubernetes has 3 replicas, readiness and liveness probes, revision history and a NodePort Service on 30083 in devops-assignment.

Initial page is release v1. index-v2.html is the prepared feature update; copy it over index.html and commit. The pipeline checks GitHub every minute with pollSCM and also supports githubPush for a configured reachable webhook.

Run a healthy release before the deliberate failure demo. Build with FAULTY_RELEASE=true selects Dockerfile.faulty. The defect in nginx-faulty.conf returns 503 to kube-probe user agents. Local smoke tests pass, but Kubernetes health probes fail. deploy.py detects failure and restores the stable Deployment or food Service selector. It verifies HTTP and the exact stable release afterward. The faulty Jenkins build intentionally remains FAILURE.

Food uses two color slots with three replicas in each prepared slot. The inactive candidate is verified through a separate preview Service before the public selector changes. Failed candidates cannot receive public traffic.

The Docker Desktop kind network on this laptop does not directly publish NodePorts to Windows. local_access.py creates a loopback-only Nginx bridge to the real node ports and starts separate local containers on 8091 to 8093. It requires Docker access plus KUBECONFIG and can be run through Jenkins. The bridge preserves the actual Kubernetes NodePort path.

Do not commit kubeconfig files or registry tokens. Public Docker Hub images are assumed.
