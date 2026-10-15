# CityCare Appointments

Standalone repository for Question 3.
Read the accompanying Word report for full setup and evidence instructions.

Linux Jenkins agent: bash, Git, Python 3, Docker CLI/engine and kubectl.
Agent label: docker-kubectl. Credentials: dockerhub-creds (username/token), kubeconfig (secret file).
Public Docker Hub image assumed; private images require an imagePullSecret.
Docker Hub namespace defaults to majorazor in Jenkins build parameters.
Unique image tags use build number plus Git commit. Do not overwrite tags.

Kubernetes manifests are templates. Do not apply them before rendering.
Export APP=hospital, REPLICAS=3, NODEPORT=30083, IMAGE=yourname/hospital:v1.
Build with: docker build --build-arg RELEASE="$IMAGE" -t "$IMAGE" .
Test with: bash scripts/test.sh
Push with: docker push "$IMAGE"
Deploy with: bash scripts/deploy.sh
NodePort: http://localhost:30083

For v2 copy versions/index-v2.html over index.html and commit/push.
For failure demonstration run Jenkins with FAULTY_RELEASE=true after a healthy release.
The real image passes container tests; its Kubernetes readiness path deliberately returns 404.
The failed Jenkins build is intentional even when recovery succeeds.
Reset FAULTY_RELEASE=false before the next healthy build.
Never execute the fault demo against a shared production cluster.
