variable "project_id" {
  description = "The GCP project ID."
  type        = string
}

variable "region" {
  description = "The GCP region to deploy resources in."
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "The name of the Cloud Run service."
  type        = string
  default     = "telegram-groups-classifier"
}

variable "image_url" {
  description = "The URL of the Docker image to deploy."
  type        = string
}

variable "github_actions_sa" {
  description = "The GitHub Actions service account email that deploys the service."
  type        = string
}