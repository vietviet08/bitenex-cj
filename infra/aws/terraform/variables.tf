variable "project_name" {
  type        = string
  description = "Project name prefix"
  default     = "bitenex-cj"
}

variable "environment" {
  type        = string
  description = "Environment name"
  default     = "stg"
}

variable "aws_region" {
  type        = string
  description = "AWS region"
  default     = "ap-southeast-1"
}

variable "vpc_cidr" {
  type        = string
  description = "VPC CIDR"
  default     = "10.30.0.0/16"
}

variable "instance_type" {
  type        = string
  description = "EC2 instance type for Ubuntu server"
  default     = "t3.large"
}

variable "key_name" {
  type        = string
  description = "Optional EC2 key pair name for SSH"
  default     = ""
}

variable "allowed_ssh_cidr" {
  type        = string
  description = "CIDR allowed to access SSH (22)"
  default     = "0.0.0.0/0"
}

variable "db_name" {
  type        = string
  description = "RDS PostgreSQL database name"
  default     = "bitenex"
}

variable "db_username" {
  type        = string
  description = "RDS PostgreSQL admin username"
  default     = "bitenex_admin"
}

variable "db_password" {
  type        = string
  description = "RDS PostgreSQL admin password"
  sensitive   = true
}

variable "db_instance_class" {
  type        = string
  description = "RDS instance class"
  default     = "db.t4g.micro"
}

variable "db_allocated_storage" {
  type        = number
  description = "RDS allocated storage in GB"
  default     = 30
}

variable "db_multi_az" {
  type        = bool
  description = "Enable Multi-AZ for RDS"
  default     = false
}

variable "domain_name" {
  type        = string
  description = "Primary domain name (optional, for future ALB/Route53 setup)"
  default     = ""
}
