output "vpc_id" {
  value = aws_vpc.main.id
}

output "compose_host_instance_id" {
  value = aws_instance.bitenex_compose_host.id
}

output "compose_host_public_ip" {
  value = aws_instance.bitenex_compose_host.public_ip
}

output "compose_host_public_dns" {
  value = aws_instance.bitenex_compose_host.public_dns
}

output "rds_postgres_endpoint" {
  value = aws_db_instance.postgres.address
}

output "rds_postgres_port" {
  value = aws_db_instance.postgres.port
}

output "admin_frontend_bucket_name" {
  value = aws_s3_bucket.admin_frontend.bucket
}

output "admin_cloudfront_distribution_id" {
  value = aws_cloudfront_distribution.admin_frontend.id
}

output "admin_cloudfront_domain_name" {
  value = aws_cloudfront_distribution.admin_frontend.domain_name
}

output "admin_frontend_certificate_arn" {
  value = try(aws_acm_certificate.admin_frontend[0].arn, "")
}

output "admin_frontend_certificate_validation_records" {
  value = try([
    for dvo in aws_acm_certificate.admin_frontend[0].domain_validation_options : {
      name  = dvo.resource_record_name
      type  = dvo.resource_record_type
      value = dvo.resource_record_value
    }
  ], [])
}
