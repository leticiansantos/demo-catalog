#!/bin/bash
set -euo pipefail

# =============================================================================
# Cria um workspace Databricks via FE Vending Machine (template AWS Stable Classic).
# Para mudar/criar outro workspace no futuro: altere DEPLOY_WORKSPACE_NAME e execute.
# O Terraform continua a usar o workspace de teste (terraform/terraform.tfvars).
# =============================================================================

FEVM_CLIENT="/Users/leticia.santos/.claude/plugins/cache/fe-vibe/fe-databricks-tools/1.0.6/skills/databricks-fe-vm-workspace-deployment/resources/fe_vm_client.py"
ENV_MANAGER="/Users/leticia.santos/.claude/plugins/cache/fe-vibe/fe-databricks-tools/1.0.6/skills/databricks-fe-vm-workspace-deployment/resources/environment_manager.py"

# Nome do workspace a CRIAR via Vending Machine (editar quando for mudar de workspace)
DEPLOY_WORKSPACE_NAME="${DEPLOY_WORKSPACE_NAME:-leticia-demo-catalog}"
REGION="us-east-1"
LIFETIME=30

echo "=== Databricks Workspace Deployment (FE Vending Machine) ==="
echo "Name:     $DEPLOY_WORKSPACE_NAME"
echo "Template: AWS Stable Classic (E2)"
echo "Region:   $REGION"
echo "Lifetime: ${LIFETIME} days"
echo ""

# Step 1: Check if workspace already exists
echo "Step 1: Checking for existing workspaces..."
EXISTING=$(python3 "$ENV_MANAGER" list 2>&1 || true)
if echo "$EXISTING" | grep -q "$DEPLOY_WORKSPACE_NAME"; then
  echo "Workspace '$DEPLOY_WORKSPACE_NAME' already exists:"
  echo "$EXISTING" | grep -A3 "$DEPLOY_WORKSPACE_NAME"
  echo ""
  read -p "Continue with new deployment? (y/N) " -n 1 -r
  echo ""
  [[ ! $REPLY =~ ^[Yy]$ ]] && echo "Cancelled." && exit 0
fi

# Step 2: Check authentication
echo "Step 2: Checking FEVM authentication..."
AUTH_STATUS=$(python3 "$FEVM_CLIENT" check-auth 2>&1 || true)
if echo "$AUTH_STATUS" | grep -q '"authenticated": false'; then
  echo "ERROR: Not authenticated with FE Vending Machine."
  echo ""
  echo "To authenticate, you need to:"
  echo "  1. Open https://vending-machine-main-2481552415672103.aws.databricksapps.com/"
  echo "  2. Log in via SSO"
  echo "  3. Extract the __Host-databricksapps cookie from your browser"
  echo "  4. Run: python3 $(dirname "$FEVM_CLIENT")/browser_auth.py save-cookie \"<cookie_value>\""
  echo ""
  exit 1
fi
echo "Authenticated successfully."
echo ""

# Step 3: Check quota
echo "Step 3: Checking quota..."
python3 "$FEVM_CLIENT" quota
echo ""

# Step 4: Deploy
echo "Step 4: Deploying workspace..."
read -p "Proceed with deployment? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Cancelled."
  exit 0
fi

RESULT=$(python3 "$FEVM_CLIENT" deploy-classic \
  --name "$DEPLOY_WORKSPACE_NAME" \
  --region "$REGION" \
  --lifetime "$LIFETIME" \
  --json)

echo "$RESULT" | python3 -m json.tool

# Extract run URL for status tracking
RUN_URL=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('github_run_url',''))" 2>/dev/null || true)
SUCCESS=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null || true)

if [ "$SUCCESS" != "True" ]; then
  echo "ERROR: Deployment request failed."
  exit 1
fi

echo ""
echo "Deployment started!"
if [ -n "$RUN_URL" ]; then
  RUN_ID=$(echo "$RUN_URL" | sed 's/.*\///')
  echo "GitHub Run: $RUN_URL"
  echo ""

  # Step 5: Wait for completion
  read -p "Wait for deployment to complete? (~15-20 min for classic) (y/N) " -n 1 -r
  echo ""
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Waiting for deployment (timeout: 30 min)..."
    python3 "$FEVM_CLIENT" wait --run-id "$RUN_ID" --timeout 30

    echo ""
    echo "=== Deployment Complete ==="
    python3 "$FEVM_CLIENT" refresh-cache
    echo ""
    echo "Workspace URL: https://fevm-${DEPLOY_WORKSPACE_NAME}.cloud.databricks.com"
    echo "Catalog name:  ${DEPLOY_WORKSPACE_NAME//-/_}_catalog"
    echo ""
    echo "To authenticate via CLI:"
    echo "  databricks auth login --host https://fevm-${DEPLOY_WORKSPACE_NAME}.cloud.databricks.com"
  else
    echo ""
    echo "You can check status later with:"
    echo "  python3 $FEVM_CLIENT status --run-id $RUN_ID"
  fi
fi
