variable "project_name" {
  description = "Base name for all resources"
  type        = string
  default     = "content-intelligence"
}

variable "resource_group_name" {
  description = "Name of the existing resource group to deploy into"
  type        = string
  default     = "ai-build"
}

variable "python_version" {
  description = "Python runtime version for App Service"
  type        = string
  default     = "3.12"
}

variable "app_service_sku" {
  description = "App Service Plan SKU name"
  type        = string
  default     = "B1"
}

# --- Azure AI service endpoints (passed as app settings) ---

variable "content_understanding_endpoint" {
  description = "Azure AI Foundry Content Understanding endpoint"
  type        = string
}

variable "azure_openai_endpoint" {
  description = "Azure AI Foundry OpenAI endpoint"
  type        = string
}

variable "llm_deployment" {
  description = "LLM deployment name"
  type        = string
  default     = "gpt-5.2-chat"
}

variable "document_intelligence_endpoint" {
  description = "Azure AI Document Intelligence endpoint"
  type        = string
}
