resource "google_cloud_run_v2_service" "main" {
  name     = var.service_name
  location = var.region

  template {
    service_account = google_service_account.cloud_run_sa.email
    timeout         = "3600s"
    containers {
      image = var.image_url
      ports {
        container_port = 8080
      }
      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      resources {
        limits = {
          cpu    = "8"
          memory = "32Gi"
        }
      }
    }
  }
}
