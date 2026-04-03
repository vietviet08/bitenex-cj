data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

locals {
  name                         = "${var.project_name}-${var.environment}"
  azs                          = slice(data.aws_availability_zones.available.names, 0, 2)
  admin_domain_name            = var.admin_domain_name != "" ? var.admin_domain_name : (var.domain_name != "" ? "admin.${var.domain_name}" : "")
  admin_bucket_name            = lower("${var.project_name}-${var.environment}-admin-${data.aws_caller_identity.current.account_id}")
  admin_use_custom_certificate = local.admin_domain_name != "" && var.admin_cloudfront_certificate_arn != ""
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${local.name}-vpc"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${local.name}-igw"
  }
}

resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone       = local.azs[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "${local.name}-public-${count.index + 1}"
    Tier = "public"
  }
}

resource "aws_subnet" "private_data" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 20)
  availability_zone = local.azs[count.index]

  tags = {
    Name = "${local.name}-private-data-${count.index + 1}"
    Tier = "private-data"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${local.name}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "server" {
  name        = "${local.name}-server-sg"
  description = "Security group for bitenex compose host"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "rds" {
  name        = "${local.name}-rds-sg"
  description = "Security group for RDS Postgres"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.server.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_subnet_group" "main" {
  name       = "${local.name}-db-subnets"
  subnet_ids = aws_subnet.private_data[*].id
}

resource "aws_db_instance" "postgres" {
  identifier             = "${var.project_name}-${var.environment}-postgres"
  engine                 = "postgres"
  engine_version         = "16"
  instance_class         = var.db_instance_class
  allocated_storage      = var.db_allocated_storage
  db_name                = var.db_name
  username               = var.db_username
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false
  multi_az               = var.db_multi_az
  skip_final_snapshot    = true
}

data "aws_iam_policy_document" "compose_host_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "compose_host" {
  name               = "${local.name}-compose-host-role"
  assume_role_policy = data.aws_iam_policy_document.compose_host_assume_role.json
}

data "aws_iam_policy_document" "compose_host_ecr" {
  statement {
    sid = "AllowEcrLogin"

    actions = [
      "ecr:GetAuthorizationToken",
    ]

    resources = ["*"]
  }

  statement {
    sid = "AllowPushPullBitenexApiRepository"

    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:BatchGetImage",
      "ecr:CompleteLayerUpload",
      "ecr:DescribeImages",
      "ecr:DescribeRepositories",
      "ecr:GetDownloadUrlForLayer",
      "ecr:InitiateLayerUpload",
      "ecr:ListImages",
      "ecr:PutImage",
      "ecr:UploadLayerPart",
    ]

    resources = [aws_ecr_repository.bitenex_api.arn]
  }
}

resource "aws_iam_role_policy" "compose_host_ecr" {
  name   = "${local.name}-compose-host-ecr"
  role   = aws_iam_role.compose_host.id
  policy = data.aws_iam_policy_document.compose_host_ecr.json
}

data "aws_iam_policy_document" "compose_host_admin_frontend" {
  statement {
    sid = "AllowAdminFrontendBucketList"

    actions = [
      "s3:GetBucketLocation",
      "s3:ListBucket",
    ]

    resources = [aws_s3_bucket.admin_frontend.arn]
  }

  statement {
    sid = "AllowAdminFrontendObjectDeploy"

    actions = [
      "s3:DeleteObject",
      "s3:GetObject",
      "s3:PutObject",
    ]

    resources = ["${aws_s3_bucket.admin_frontend.arn}/*"]
  }

  statement {
    sid = "AllowAdminFrontendCloudFrontInvalidation"

    actions = [
      "cloudfront:CreateInvalidation",
      "cloudfront:GetDistribution",
      "cloudfront:GetDistributionConfig",
    ]

    resources = [aws_cloudfront_distribution.admin_frontend.arn]
  }
}

resource "aws_iam_role_policy" "compose_host_admin_frontend" {
  name   = "${local.name}-compose-host-admin-frontend"
  role   = aws_iam_role.compose_host.id
  policy = data.aws_iam_policy_document.compose_host_admin_frontend.json
}

resource "aws_iam_instance_profile" "compose_host" {
  name = "${local.name}-compose-host-profile"
  role = aws_iam_role.compose_host.name
}

resource "aws_instance" "bitenex_compose_host" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.public[0].id
  vpc_security_group_ids      = [aws_security_group.server.id]
  iam_instance_profile        = aws_iam_instance_profile.compose_host.name
  key_name                    = var.key_name != "" ? var.key_name : null
  associate_public_ip_address = true

  root_block_device {
    volume_size = 30
    volume_type = "gp3"
  }

  tags = {
    Name = "${local.name}-bitenex-compose-host"
    Role = "bitenex-api-host"
  }
}

resource "aws_ecr_repository" "bitenex_api" {
  name                 = var.ecr_api_repository_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_s3_bucket" "admin_frontend" {
  bucket = local.admin_bucket_name
}

resource "aws_s3_bucket_public_access_block" "admin_frontend" {
  bucket                  = aws_s3_bucket.admin_frontend.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "admin_frontend" {
  bucket = aws_s3_bucket.admin_frontend.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "admin_frontend" {
  bucket = aws_s3_bucket.admin_frontend.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_cloudfront_origin_access_control" "admin_frontend" {
  name                              = "${local.name}-admin-oac"
  description                       = "Origin access control for bitenex-admin static site"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_acm_certificate" "admin_frontend" {
  count             = local.admin_domain_name != "" ? 1 : 0
  provider          = aws.us_east_1
  domain_name       = local.admin_domain_name
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_cloudfront_distribution" "admin_frontend" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "Static hosting for bitenex-admin"
  default_root_object = "index.html"
  price_class         = var.admin_cloudfront_price_class
  aliases             = local.admin_use_custom_certificate ? [local.admin_domain_name] : []

  origin {
    domain_name              = aws_s3_bucket.admin_frontend.bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.admin_frontend.id
    origin_id                = "admin-s3-origin"
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "admin-s3-origin"
    compress         = true

    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }

  custom_error_response {
    error_code            = 403
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 0
  }

  custom_error_response {
    error_code            = 404
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 0
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = !local.admin_use_custom_certificate
    acm_certificate_arn            = local.admin_use_custom_certificate ? var.admin_cloudfront_certificate_arn : null
    ssl_support_method             = local.admin_use_custom_certificate ? "sni-only" : null
    minimum_protocol_version       = local.admin_use_custom_certificate ? "TLSv1.2_2021" : "TLSv1"
  }
}

data "aws_iam_policy_document" "admin_frontend_bucket_policy" {
  statement {
    sid = "AllowCloudFrontServicePrincipalReadOnly"

    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    actions = ["s3:GetObject"]

    resources = ["${aws_s3_bucket.admin_frontend.arn}/*"]

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.admin_frontend.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "admin_frontend" {
  bucket = aws_s3_bucket.admin_frontend.id
  policy = data.aws_iam_policy_document.admin_frontend_bucket_policy.json
}
