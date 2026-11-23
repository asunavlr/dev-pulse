# AWS deployment with Terraform

This stack provisions DevPulse on ECS Fargate behind an Application Load Balancer.

## Resources
- ECS cluster with Container Insights
- Fargate task definition and service
- Application Load Balancer and health-checked target group
- Security groups: public traffic reaches only the ALB; tasks accept the app port only from the ALB
- CloudWatch log group (30-day retention) and ECS task execution role

## Prerequisites
AWS credentials, existing VPC, at least two public subnets in distinct Availability Zones, an ECR image for DevPulse, Terraform >= 1.7.

## Deploy
```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit VPC, subnet IDs, region and immutable ECR image digest.
terraform init
terraform plan
terraform apply
```

Destroy demo resources with terraform destroy when finished to avoid ongoing AWS charges.

## Production hardening
This example exposes HTTP only. Add ACM + HTTPS and redirect HTTP before production. Prefer private subnets with NAT or VPC endpoints for tasks. Configure encrypted remote state and locking; never commit state or real tfvars. Add egress restrictions, WAF, secrets management, image scanning, autoscaling and alarms. The GitHub workflow validates Terraform only; it does not deploy. Add a GitHub OIDC role and protected environment before automated apply.
