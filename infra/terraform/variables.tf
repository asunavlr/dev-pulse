variable "aws_region" {
  type    = string
  default = "eu-west-1"
}
variable "project_name" {
  type    = string
  default = "devpulse"
}
variable "vpc_id" {
  type = string
}
variable "public_subnet_ids" {
  type = list(string)
  validation {
    condition     = length(var.public_subnet_ids) >= 2
    error_message = "Provide at least two public subnets in distinct availability zones."
  }
}
variable "private_subnet_ids" {
  type = list(string)
  validation {
    condition     = length(var.private_subnet_ids) >= 2
    error_message = "Provide at least two private subnets in distinct availability zones."
  }
}
variable "certificate_arn" {
  type        = string
  description = "ACM certificate ARN in the same region as the ALB"
}
variable "container_image" {
  type        = string
  description = "Immutable container image URI (prefer an ECR digest)"
}
variable "desired_count" {
  type    = number
  default = 1
}
variable "min_capacity" {
  type    = number
  default = 1
}
variable "max_capacity" {
  type    = number
  default = 3
}
variable "task_cpu" {
  type    = number
  default = 256
}
variable "task_memory" {
  type    = number
  default = 512
}
variable "app_port" {
  type    = number
  default = 8000
}
variable "health_check_path" {
  type    = string
  default = "/ready"
}

variable "api_key_secret_arn" {
  type        = string
  description = "Secrets Manager ARN containing the DevPulse API key as its SecretString"
}
variable "database_url_secret_arn" {
  type        = string
  description = "Secrets Manager ARN containing the production SQLAlchemy DATABASE_URL"
}
