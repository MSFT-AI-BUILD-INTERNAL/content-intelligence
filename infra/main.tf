terraform {
  required_version = ">= 1.5"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# ──────────────────────────────────────────────
# Resource Group (기존 리소스 그룹 참조)
# ──────────────────────────────────────────────
data "azurerm_resource_group" "main" {
  name = var.resource_group_name
}

# ──────────────────────────────────────────────
# App Service Plan (Linux)
# ──────────────────────────────────────────────
resource "azurerm_service_plan" "main" {
  name                = "plan-${var.project_name}"
  location            = data.azurerm_resource_group.main.location
  resource_group_name = data.azurerm_resource_group.main.name
  os_type             = "Linux"
  sku_name            = var.app_service_sku
}

# ──────────────────────────────────────────────
# Linux Web App
# ──────────────────────────────────────────────
resource "azurerm_linux_web_app" "main" {
  name                = "app-${var.project_name}"
  location            = data.azurerm_resource_group.main.location
  resource_group_name = data.azurerm_resource_group.main.name
  service_plan_id     = azurerm_service_plan.main.id

  https_only = true

  identity {
    type = "SystemAssigned"
  }

  site_config {
    always_on = true

    application_stack {
      python_version = var.python_version
    }

    app_command_line = "python -m uvicorn web.app:app --host 0.0.0.0 --port 8000"
  }

  app_settings = {
    # Azure AI service endpoints
    CONTENT_UNDERSTANDING_ENDPOINT = var.content_understanding_endpoint
    AZURE_OPENAI_ENDPOINT          = var.azure_openai_endpoint
    LLM_DEPLOYMENT                 = var.llm_deployment
    DOCUMENT_INTELLIGENCE_ENDPOINT = var.document_intelligence_endpoint

    # App Service uses port 8000 (uvicorn default)
    WEBSITES_PORT = "8000"

    # 컨테이너 시작 제한 시간 (기본 230초 → 600초)
    WEBSITES_CONTAINER_START_TIME_LIMIT = "600"

    # Oryx 빌드 활성화
    SCM_DO_BUILD_DURING_DEPLOYMENT = "true"
  }
}

