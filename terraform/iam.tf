# Grant GitHub Actions service account permission to act as the Cloud Run service account
resource "google_service_account_iam_member" "github_actions_sa_user" {
  service_account_id = "projects/${var.project_id}/serviceAccounts/telegram-groups-classifier-sa@pwcnext-sandbox01.iam.gserviceaccount.com"
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${var.github_actions_sa}"
}
