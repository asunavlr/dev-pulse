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
variable "container_image" {
  type = string
}
variable "desired_count" {
  type    = number
  default = 1
}
variable "app_port" {
  type    = number
  default = 8000
}
variable "health_check_path" {
  type    = string
  default = "/health"
}
