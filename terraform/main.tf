# ==========================================
# 🌌 Gemini L200 Study Hub GCP Infrastructure
# ==========================================
# This Terraform configuration provisions the complete, production-grade cloud resources
# required to deploy the Gemini L200 Agentic Study Hub to Google Cloud Platform (GCP).

terraform {
  required_version = ">= 1.3.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ==========================================
# 🛠️ GCP Service Enablement
# ==========================================
# Enable necessary APIs for the architecture
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",             # Cloud Run
    "firestore.googleapis.com",       # Firestore
    "artifactregistry.googleapis.com", # Artifact Registry
    "secretmanager.googleapis.com",   # Secret Manager
    "aiplatform.googleapis.com"       # Vertex AI (Gemini API)
  ])
  project            = var.project_id
  service            = each.key
  disable_on_destroy = false
}

# ==========================================
# 📦 Artifact Registry
# ==========================================
# Create a repository to securely house our Docker container images
resource "google_artifact_registry_repository" "l200_repo" {
  depends_on    = [google_project_service.apis]
  location      = var.region
  repository_id = var.repository_id
  description   = "Docker repository for the Gemini L200 Study Hub"
  format        = "DOCKER"

  docker_config {
    immutable_tags = false
  }
}

# ==========================================
# 🔥 Firestore Database (Native Mode)
# ==========================================
# Provision a Firestore database in Native mode to house persistent multi-student progress
resource "google_firestore_database" "l200_db" {
  depends_on                  = [google_project_service.apis]
  project                     = var.project_id
  name                        = var.firestore_db_name
  location_id                 = var.firestore_location
  type                        = "FIRESTORE_NATIVE"
  concurrency_mode            = "OPTIMISTIC"
  app_engine_integration_mode = "DISABLED"
}

# ==========================================
# 🔑 Secret Manager (Gemini API Key)
# ==========================================
# Provisions a secure container for the Gemini API Key to avoid any environment hardcoding
resource "google_secret_manager_secret" "gemini_key" {
  depends_on = [google_project_service.apis]
  secret_id  = "l200-gemini-api-key"

  replication {
    auto {}
  }
}

# ==========================================
# 🛡️ Service Account for Cloud Run
# ==========================================
# Dedicated minimal-privilege service account for running our Cloud Run microservice
resource "google_service_account" "cloud_run_sa" {
  account_id   = "l200-hub-runner"
  display_name = "L200 Study Hub Cloud Run Runner"
}

# Grant Firestore User role to the runner service account
resource "google_project_iam_member" "firestore_access" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Grant Vertex AI User role to the runner service account
resource "google_project_iam_member" "vertex_access" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Grant Secret Manager Secret Accessor to the runner service account
resource "google_secret_manager_secret_iam_member" "secret_access" {
  secret_id = google_secret_manager_secret.gemini_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# ==========================================
# ⚡ Google Cloud Run Service
# ==========================================
# Serves the containerized FastAPI backend, securing it behind HTTPS with automatic TLS.
resource "google_cloud_run_v2_service" "l200_service" {
  depends_on = [
    google_project_service.apis,
    google_artifact_registry_repository.l200_repo
  ]
  name     = var.service_name
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.cloud_run_sa.email

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.l200_repo.repository_id}/${var.service_name}:latest"
      
      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "1024Mi"
        }
      }

      # Mount the GEMINI_API_KEY securely from Secret Manager
      env {
        name = "GEMINI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.gemini_key.secret_id
            version = "latest"
          }
        }
      }

      # Standard environment variables
      env {
        name  = "PORT"
        value = "8080"
      }
    }
  }
}

# Allow unauthenticated (public) traffic to the frontend
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  location = google_cloud_run_v2_service.l200_service.location
  name     = google_cloud_run_v2_service.l200_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
