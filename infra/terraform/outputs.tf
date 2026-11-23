output "application_url" {
  value = "http://${aws_lb.app.dns_name}"
}
output "ecs_cluster_name" {
  value = aws_ecs_cluster.app.name
}
output "ecs_service_name" {
  value = aws_ecs_service.app.name
}
output "log_group_name" {
  value = aws_cloudwatch_log_group.app.name
}
