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
  version = "15"
  region = "oregon"
}

# Backend Web Service
resource "render_web_service" "backend" {
  name = "${var.app_name}-backend"
  plan = "free"
  region = "oregon"
  
  runtime = "docker"
  
  repo = {
    url = "https://github.com/${var.github_username}/${var.repo_name}"
    branch = "main"
    auto_deploy = true
    build_filter = {
      paths = ["backend/**"]
    }
  }
  
  docker = {
    context = "./backend"
    dockerfile_path = "./Dockerfile"
  }
  
  env_vars = {
    APP_NAME = var.app_name
    APP_VERSION = var.app_version
    DEBUG = var.debug
    LOG_LEVEL = var.log_level
    DATABASE_URL = render_postgres.main_db.connection_string
    GEMINI_API_KEY = var.gemini_api_key
    TEMPORAL_API_KEY = var.temporal_api_key
    TEMPORAL_ADDRESS = var.temporal_address
    TEMPORAL_NAMESPACE = var.temporal_namespace
  }
  
  health_check = {
    path = "/api/health"
  }
}

# Frontend Static Site
resource "render_static_site" "frontend" {
  name = "${var.app_name}-frontend"
  plan = "free"
  region = "oregon"
  
  repo = {
    url = "https://github.com/${var.github_username}/${var.repo_name}"
    branch = "main"
    auto_deploy = true
    build_filter = {
      paths = ["frontend/**"]
    }
  }
  
  build_command = "cd frontend && npm ci && npm run build"
  publish_path = "frontend/build"
  
  env_vars = {
    REACT_APP_API_URL = render_web_service.backend.url
    NODE_ENV = "production"
  }
}

# Temporal Worker Service
resource "render_private_service" "temporal_worker" {
  name = "${var.app_name}-worker"
  plan = "free"
  region = "oregon"
  
  runtime = "docker"
  
  repo = {
    url = "https://github.com/${var.github_username}/${var.repo_name}"
    branch = "main"
    auto_deploy = true
  }
  
  docker = {
    context = "./backend"
    dockerfile_path = "./Dockerfile.worker"
    command = "python -m app.worker"
  }
  
  env_vars = {
    APP_NAME = var.app_name
    LOG_LEVEL = var.log_level
    DATABASE_URL = render_postgres.main_db.connection_string
    TEMPORAL_API_KEY = var.temporal_api_key
    TEMPORAL_ADDRESS = var.temporal_address
    TEMPORAL_NAMESPACE = var.temporal_namespace
    GEMINI_API_KEY = var.gemini_api_key
  }
  
  # Add startup command
  start_command = "python -m app.worker"
}