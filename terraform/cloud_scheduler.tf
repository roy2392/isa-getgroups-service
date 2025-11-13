resource "google_cloud_scheduler_job" "job" {
  name        = "${var.service_name}-trigger"
  description = "Triggers the ${var.service_name} Cloud Run service daily"
  schedule    = "0 2 * * *" # Runs every day at 2:00 AM UTC

  http_target {
    uri = google_cloud_run_v2_service.main.uri
    http_method = "POST"
    oidc_token {
      service_account_email = google_service_account.cloud_scheduler_sa.email
    }
  }
}
