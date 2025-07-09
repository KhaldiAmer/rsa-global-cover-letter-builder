variable "app_name" {
  type = string
  default = "rsa-global-cover-letter-builder"
  description = "Application name"
}

variable "app_version" {
  type = string
  description = "Application version"
}

variable "debug" {
  type = string
  default = "false"
  description = "Debug mode"
}

variable "log_level" {
  type = string
  default = "INFO"
  description = "Log level"
}

variable "gemini_api_key" {
  type = string
  sensitive = true
  description = "Google Gemini API key"
}

variable "temporal_api_key" {
  type = string
  sensitive = true
  description = "Temporal Cloud API key"
}

variable "temporal_address" {
  type = string
  description = "Temporal Cloud address"
}

variable "temporal_namespace" {
  type = string
  default = "default"
  description = "Temporal namespace"
}

variable "render_api_key" {
  type = string
  sensitive = true
  description = "Render API key"
}

// Removed render_email variable - not needed for provider configuration

variable "terraform_organization" {
  type = string
  description = "Terraform Cloud organization"
}

variable "github_username" {
  type = string
  description = "GitHub username"
}

variable "repo_name" {
  type = string
  default = "rsa-global-cover-letter-builder"
  description = "GitHub repository name"
}