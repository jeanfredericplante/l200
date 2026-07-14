# ==========================================
# 🌌 Terraform Output Values
# ==========================================

output "cloud_run_url" {
  description = "The secure HTTPS public URL of the deployed Gemini L200 Study Hub"
  value       = google_cloud_run_v2_service.l200_service.uri
}

output "artifact_registry_repo" {
  description = "The absolute URL of the Artifact Registry repository for container image pushing"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.l200_repo.repository_id}"
}

output "firestore_db_id" {
  description = "The ID of the provisioned Firestore Native Database"
  value       = google_firestore_database.l200_db.id
}

output "secret_manager_secret" {
  description = "The secret ID for the Gemini API Key in Secret Manager"
  value       = google_secret_manager_secret.gemini_key.id
}
