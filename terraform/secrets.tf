resource "google_secret_manager_secret" "telegram_api_id" {
  secret_id = "telegram-api-id"
  replication {
    auto {}
  }
  provisioner "local-exec" {
    when    = destroy
    command = "gcloud secrets delete ${self.secret_id} --project=${self.project} --quiet"
  }
}

resource "google_secret_manager_secret" "telegram_api_hash" {
  secret_id = "telegram-api-hash"
  replication {
    auto {}
  }
  provisioner "local-exec" {
    when    = destroy
    command = "gcloud secrets delete ${self.secret_id} --project=${self.project} --quiet"
  }
}

resource "google_secret_manager_secret" "gemini_api_key" {
  secret_id = "gemini-api-key"
  replication {
    auto {}
  }
  provisioner "local-exec" {
    when    = destroy
    command = "gcloud secrets delete ${self.secret_id} --project=${self.project} --quiet"
  }
}
