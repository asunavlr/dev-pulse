# AWS deployment with Terraform

This stack deploys the DevPulse API and its dedicated monitoring worker to ECS Fargate.

## Architecture

- Public Application Load Balancer with ACM TLS certificate; HTTP redirects to HTTPS
- API ECS service in private subnets, autoscaled by average CPU
- Dedicated single-instance worker ECS service for recurring checks (avoids duplicate in-process schedulers when the API scales horizontally)
- Separate security groups: only the ALB reaches the API task port
- CloudWatch logs, Container Insights, CPU / ALB 5xx alarms and ECS deployment rollback
- API key and database URL injected from AWS Secrets Manager; the task execution role has read access only to those secret ARNs

## Prerequisites

- Existing VPC with at least two public and two private subnets across Availability Zones
- NAT gateway or the required VPC endpoints so private tasks can pull images, read secrets and send CloudWatch logs
- ACM certificate in the same region as the ALB
- Existing PostgreSQL database reachable from the task security group
- ECR image pushed for DevPulse
- Two Secrets Manager secrets: one containing the API key (at least 32 random characters), one containing a SQLAlchemy URL such as postgresql+psycopg://user:password@host:5432/devpulse
- Terraform >= 1.7 and AWS credentials

## Deploy

~~~bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# Replace all VPC, subnet, certificate, secret and image placeholders.
terraform init
terraform fmt -check -recursive
terraform validate
terraform plan
terraform apply
~~~

The API URL is returned as the Terraform output application_url. The worker runs exactly one scheduled instance; do not scale it horizontally without adding distributed scheduling/locking.

Destroy demo resources with terraform destroy when finished to avoid ongoing AWS charges. This stack does not create the PostgreSQL database, NAT gateway, ACM certificate, ECR repository or Secrets Manager values.

## Security and operational notes

- Tasks run in private subnets without public IPs. Egress currently relies on NAT or VPC endpoints; tighten egress to required destinations for a hardened environment.
- HTTP is redirected to HTTPS. Use a certificate whose DNS names match the hostname you point at the ALB.
- Use encrypted remote Terraform state with locking; never commit state or real tfvars.
- Configure alarms with SNS actions and add dashboards, log retention policy review, backup/restore drills, WAF, image scanning and vulnerability management.
- API-key protection and URL validation mitigate common misuse, but production monitoring still needs outbound firewall policy / DNS-rebinding controls and abuse limits.
- GitHub Actions validates Terraform only. It does not deploy AWS resources; configure a dedicated OIDC role and protected environment before enabling deployment.
