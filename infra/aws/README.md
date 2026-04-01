# AWS Infra Blueprint for Customer Journey

This folder provides a practical baseline to deploy `bitenex-api` stack on AWS with:

- Terraform: provisioning cloud resources
- Ansible: post-provision configuration on EC2 hosts

## Proposed Architecture

- Networking
- VPC across 2 AZs
- 2 public subnets
- 1 Ubuntu EC2 host in public subnet for Docker Compose workloads

- Docker Compose stack on host
- `api` (FastAPI)
- `redis`
- `n8n`
- `sonarqube`

- Data layer
- RDS PostgreSQL (private subnet, no Postgres container on EC2)

- Host tooling installed by Ansible
- Docker Engine + Docker Compose plugin
- Jenkins
- Git
- Java 17 (OpenJDK)
- net-tools

- Traffic and access
- Security Group opens: `22`, `80`, `443`, `8000`, `5678`, `8080`, `9000`
- Tighten `22` with `allowed_ssh_cidr`
- ALB is optional in this phase (recommended when you need TLS offload, path routing, autoscaling, or zero-downtime rollout)

## Folder Layout

- `terraform/`: VPC + Ubuntu EC2 host provisioning template
- `ansible/`: server bootstrap and Docker Compose deployment automation

## Terraform Quick Start

```bash
cd infra/aws/terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

## Ansible Quick Start

1. Export AWS profile/credentials and region.
2. Update `ansible/group_vars/all.yml` with your repository URL/branch.
3. Ensure `.env` and `.env.docker` are present in `bitenex-api` path on server.
4. Set app database env to RDS endpoint from Terraform output (`rds_postgres_endpoint`).
5. Run Ansible using dynamic inventory plugin:

```bash
cd infra/aws/ansible
ansible-playbook -i inventory/aws_ec2.yml playbooks/bootstrap.yml
```

## Notes

- This scaffold is intentionally minimal and safe-by-default.
- For production, add remote Terraform state (S3 + DynamoDB lock), backup/monitoring for RDS, and secrets management.
