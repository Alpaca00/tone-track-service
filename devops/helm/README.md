## Deployment to Kubernetes

This configuration utilizes Helm to deploy the application to a Kubernetes cluster and retrieve the necessary image from the [Docker Hub repository](https://hub.docker.com/repository/docker/alpaca00/tone-track-image/general).

### Prerequisites
- Ensure you have [Helm](https://helm.sh/docs/intro/install/) `>= v3.16.2` installed on your system.

### Installation Steps

1. **Update Values (Optional)**

- Edit the [values.yaml](values.yaml) or [configmap.yaml](templates/configmap.yaml) files to configure the necessary environment variables 
and any custom configurations or ConfigMaps you want to use in the deployment for Nginx, Redis, PostgreSQL, and your application.
This allows for easier management and customization of your deployment settings.

2. **Generate Environment Variables (Optional)**

- Run the following command to generate the environment variables to be used in the deployment:

```bash
chmod +x ./generate_env.sh
./generate_env.sh
```

3. **Install the Helm Chart**

- Use the following command to install the Helm chart along with the necessary environment variables.

Replace `VALUE_FROM_ENV_FILE` with actual values from the .env file, generated in step 2 below.

Replace `VALUE_FROM_SLACK_BOT_SETTINGS` with the actual values for the Slack signing secret and bot OAuth token.

```bash
helm install tone-track ./devops/helm \
--namespace tone-track --create-namespace \
--set env.SLACK_SIGNING_SECRET="VALUE_FROM_SLACK_BOT_SETTINGS" \
--set env.SLACK_BOT_OAUTH_TOKEN="VALUE_FROM_SLACK_BOT_SETTINGS" \
--set env.SECRET_KEY="VALUE_FROM_ENV_FILE" \
--set env.API_KEY="VALUE_FROM_ENV_FILE" \
--set env.SPS="VALUE_FROM_ENV_FILE" \
--set env.POSTGRES_USER="root" \
--set env.POSTGRES_PASSWORD="VALUE_FROM_ENV_FILE" \
--set env.REDIS_PASSWORD="VALUE_FROM_ENV_FILE"
```

- Ensure you replace the placeholder values with actual values from your '.env' file and the appropriate Slack settings.

4. **Verify the Installation**

- Check the status of the deployment using the following command:

```bash
kubectl -n tone-track get pods
kubectl -n tone-track get services
```

5. **Accessing the Application**

- Once the deployment is successful, you can access the application using the service URL or the external IP address.

To check the health status of the service, run the following command:

```bash
curl --location 'https://<cluster IP>:<nginx-service PORT>/api/v1/health'
```


##### Additional configurations can be made to the deployment by modifying necessary values in the [deployment.yaml](templates/deployment.yaml) and [values.yaml](values.yaml) files, such as resource limits, ingress settings, etc.

---

**Updating the Deployment**

- To update the deployment with new configurations or changes, use the following command:

```bash
helm upgrade tone-track ./devops/helm \
--namespace tone-track --create-namespace \
--set env.SLACK_SIGNING_SECRET="VALUE_FROM_SLACK_BOT_SETTINGS" \
--set env.SLACK_BOT_OAUTH_TOKEN="VALUE_FROM_SLACK_BOT_SETTINGS" \
--set env.SECRET_KEY="VALUE_FROM_ENV_FILE" \
--set env.API_KEY="VALUE_FROM_ENV_FILE" \
--set env.SPS="VALUE_FROM_ENV_FILE" \
--set env.POSTGRES_USER="root" \
--set env.POSTGRES_PASSWORD="VALUE_FROM_ENV_FILE" \
--set env.REDIS_PASSWORD="VALUE_FROM_ENV_FILE"
```

**Uninstalling the Deployment**

- To uninstall the deployment, use the following command:

```bash
helm uninstall tone-track
```
