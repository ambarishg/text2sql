# Define color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Define variables
RESOURCE_GROUP="rgmisron"
LOCATION="eastus"
LOG_ANALYTICS_WORKSPACE="ra-logs"
CONTAINERAPPS_ENVIRONMENT="ra-env"
ACR_NAME="misronacr"

# Create Log Analytics Workspace
echo -e "${BLUE}Creating Log Analytics Workspace...${NC}"
az monitor log-analytics workspace create --resource-group $RESOURCE_GROUP --workspace-name $LOG_ANALYTICS_WORKSPACE

# Retrieve Log Analytics Workspace Client ID and Secret
echo -e "${BLUE}Retrieving Log Analytics Workspace Client ID and Secret...${NC}"
LOG_ANALYTICS_WORKSPACE_CLIENT_ID=$(az monitor log-analytics workspace show --resource-group $RESOURCE_GROUP --workspace-name $LOG_ANALYTICS_WORKSPACE --query customerId -o tsv)
LOG_ANALYTICS_WORKSPACE_CLIENT_SECRET=$(az monitor log-analytics workspace get-shared-keys --query primarySharedKey -g $RESOURCE_GROUP -n $LOG_ANALYTICS_WORKSPACE --out tsv)

# Create Container Apps Environment with logging configuration
echo -e "${BLUE}Creating Container Apps Environment...${NC}"
az containerapp env create \
  --name $CONTAINERAPPS_ENVIRONMENT \
  --resource-group $RESOURCE_GROUP \
  --logs-workspace-id $LOG_ANALYTICS_WORKSPACE_CLIENT_ID \
  --logs-workspace-key $LOG_ANALYTICS_WORKSPACE_CLIENT_SECRET \
  --location $LOCATION \
  --logs-destination log-analytics

# Update Azure Container Registry to enable admin access
echo -e "${BLUE}Updating Azure Container Registry to enable admin access...${NC}"
az acr update -n $ACR_NAME --admin-enabled true

# Retrieve ACR password for authentication
echo -e "${BLUE}Retrieving ACR password...${NC}"
password=$(az acr credential show --name $ACR_NAME --query passwords[0].value --output tsv)

# Create Container App with specified resource limits
echo -e "${BLUE}Creating Container App 'misronchat' with resource limits...${NC}"
az containerapp create  --name misronchat --resource-group $RESOURCE_GROUP --environment $CONTAINERAPPS_ENVIRONMENT --image "$ACR_NAME.azurecr.io/researchassistant:v1"  --registry-server "$ACR_NAME.azurecr.io" --registry-username "$ACR_NAME" --registry-password "$password" --target-port 8000  --ingress 'external' --cpu 3 --memory 6Gi 
echo -e "${GREEN}Container App 'misronchat' created successfully!${NC}"
