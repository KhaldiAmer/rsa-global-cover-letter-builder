output "frontend_url" {
  value = render_static_site.frontend.url
  description = "Frontend application URL"
}

output "backend_url" {
  value = render_web_service.backend.url
  description = "Backend API URL"
}

output "database_connection_string" {
  value = render_postgres.main_db.connection_string
  sensitive = true
  description = "Database connection string"
}

output "deployment_info" {
  value = {
    frontend_service = render_static_site.frontend.name
    backend_service = render_web_service.backend.name
    worker_service = render_private_service.temporal_worker.name
    database_service = render_postgres.main_db.name
  }
  description = "Deployment service names"
}