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
