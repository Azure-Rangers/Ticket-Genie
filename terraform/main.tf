terraform {
  required_version = ">= 1.6.0"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "production"
}

output "environment" {
  description = "The selected deployment environment."
  value       = var.environment
}