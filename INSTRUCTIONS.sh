az acr create --resource-group rgmisron --name misronacr --sku Basic

az acr login -n misronacr

docker tag researchassistant:latest misronacr.azurecr.io/researchassistant:v1

docker push misronacr.azurecr.io/researchassistant:v1

RESOURCE_GROUP="rgmisron"
LOCATION="eastus"
LOG_ANALYTICS_WORKSPACE="ra-logs"
CONTAINERAPPS_ENVIRONMENT="ra-env"

az monitor log-analytics workspace create --resource-group $RESOURCE_GROUP --workspace-name $LOG_ANALYTICS_WORKSPACE

LOG_ANALYTICS_WORKSPACE_CLIENT_ID=$(az monitor log-analytics workspace show --resource-group $RESOURCE_GROUP --workspace-name $LOG_ANALYTICS_WORKSPACE --query customerId -o tsv)


LOG_ANALYTICS_WORKSPACE_CLIENT_SECRET=$(az monitor log-analytics workspace get-shared-keys --query primarySharedKey -g $RESOURCE_GROUP -n $LOG_ANALYTICS_WORKSPACE --out tsv)

az containerapp env create --name $CONTAINERAPPS_ENVIRONMENT  --resource-group $RESOURCE_GROUP --logs-workspace-id $LOG_ANALYTICS_WORKSPACE_CLIENT_ID --logs-workspace-key $LOG_ANALYTICS_WORKSPACE_CLIENT_SECRET --location $LOCATION 

az acr update -n misronacr --admin-enabled true

password=$(az acr credential show --name misronacr --query passwords[0].value --output tsv)

az containerapp create --name misronchat --resource-group $RESOURCE_GROUP --environment $CONTAINERAPPS_ENVIRONMENT --image misronacr.azurecr.io/researchassistant:v1 --registry-login-server misronacr.azurecr.io --registry-username misronacr --registry-password $password --target-port 8000 --ingress 'external' --query configuration.ingress.fqdn