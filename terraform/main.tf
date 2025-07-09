terraform {
  required_providers {
    render = {
      source  = "render-oss/render"
      version = "~> 1.0"
    }
  }
  
  cloud {
    organization = "khaldi-ameur"
    
    workspaces {
      name = "rsa-global-cover-letter-builder"
    }
  }
}

provider "render" {
  api_key = var.render_api_key
  owner_id = "tea-d1mlv72li9vc73chfh6g"
}

# PostgreSQL Database
resource "render_postgres" "main_db" {
  name = "${var.app_name}-db"
  plan = "free"
  version = "14"
  region = "oregon"
}

# Backend Web Service
resource "render_web_service" "backend" {
  name = "${var.app_name}-backend"
  plan = "starter"
  region = "oregon"
  
  runtime_source = {
    docker = {
      branch = "main"
      repo_url = "https://github.com/${var.github_username}/${var.repo_name}.git"
      context = "./backend"
      dockerfile_path = "./Dockerfile"
    }
  }
  
  env_vars = {
    APP_NAME = { value = var.app_name }
    APP_VERSION = { value = var.app_version }
    DEBUG = { value = var.debug }
    LOG_LEVEL = { value = var.log_level }
    DATABASE_URL = { value = render_postgres.main_db.connection_info.external_connection_string }
    GEMINI_API_KEY = { value = var.gemini_api_key }
    TEMPORAL_API_KEY = { value = var.temporal_api_key }
    TEMPORAL_ADDRESS = { value = var.temporal_address }
    TEMPORAL_NAMESPACE = { value = var.temporal_namespace }
  }
  
  health_check_path = "/api/health"
}

# Frontend Static Site
resource "render_static_site" "frontend" {
  name = "${var.app_name}-frontend"
  repo_url = "https://github.com/${var.github_username}/${var.repo_name}.git"
  branch = "main"
  build_command = "cd frontend && npm ci && npm run build"
  publish_path = "frontend/build"
  auto_deploy = true
  root_directory = "."
  
  env_vars = {
    REACT_APP_API_URL = { value = render_web_service.backend.url }
    NODE_ENV = { value = "production" }
  }
}

# Temporal Worker Service
resource "render_private_service" "temporal_worker" {
  name = "${var.app_name}-worker"
  plan = "starter"
  region = "oregon"
  
  runtime_source = {
    docker = {
      branch = "main"
      repo_url = "https://github.com/${var.github_username}/${var.repo_name}.git"
      context = "./backend"
      dockerfile_path = "./Dockerfile.worker"
    }
  }
  
  env_vars = {
    APP_NAME = { value = var.app_name }
    LOG_LEVEL = { value = var.log_level }
    DATABASE_URL = { value = render_postgres.main_db.connection_info.external_connection_string }
    TEMPORAL_API_KEY = { value = var.temporal_api_key }
    TEMPORAL_ADDRESS = { value = var.temporal_address }
    TEMPORAL_NAMESPACE = { value = var.temporal_namespace }
    GEMINI_API_KEY = { value = var.gemini_api_key }
  }
  
  start_command = "python -m app.worker"
}