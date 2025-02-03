az acr create --resource-group rgmisron --name misronacr --sku Basic

az acr login -n misronacr

docker tag researchassistant:latest misronacr.azurecr.io/researchassistant:v1

docker push misronacr.azurecr.io/researchassistant:v1