# ==========================================
# 🌌 Terraform Input Variables
# ==========================================

variable "project_id" {
  description = "The Google Cloud Platform (GCP) Project ID to deploy resources in"
  type        = string
}

variable "region" {
  description = "The GCP region to deploy resources (e.g. us-central1)"
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "The name of the Cloud Run microservice"
  type        = string
  default     = "l200-study-hub"
}

variable "repository_id" {
  description = "The Artifact Registry repository ID to store container images"
  type        = string
  default     = "l200-images"
}

variable "firestore_db_name" {
  description = "The name of the Firestore Database instance (e.g. (default) or custom name)"
  type        = string
  default     = "(default)"
}

variable "firestore_location" {
  description = "The geographic location of the Firestore Database instance"
  type        = string
  default     = "nam5" # Multi-region US, or use specific single region like us-central1
}
