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
- `sonarqube-db` (local Postgres only for SonarQube)
- `nginx` on the host as the public reverse proxy

- Data layer
- RDS PostgreSQL (private subnet, used by `api`)
- Local Postgres container in Docker network only for `sonarqube`

- Host tooling installed by Ansible
- Docker Engine + Docker Compose plugin
- Jenkins
- Git
- Java 17 (OpenJDK)
- net-tools

- Traffic and access
- Security Group opens: `22`, `80`, `443`
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
2. Update `ansible/group_vars/all.yml` with your repository URL/branch, domains, and RDS endpoint from Terraform output (`rds_postgres_endpoint`).
3. Create `ansible/vault.yml` from `ansible/vault.yml.example` and encrypt it with `ansible-vault encrypt ansible/vault.yml`.
4. Ansible will render `.env` and `.env.docker` into `bitenex-api` on the server from those vars.
5. Run Ansible using dynamic inventory plugin:

```bash
cd infra/aws/ansible
ansible-playbook -i inventory/aws_ec2.yml playbooks/bootstrap.yml
```

## Notes

- This scaffold is intentionally minimal and safe-by-default.
- For production, add remote Terraform state (S3 + DynamoDB lock), backup/monitoring for RDS, and secrets management.
