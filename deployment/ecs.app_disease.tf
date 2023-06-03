# #################################################
# # An example file deploying a container service #
# #################################################

# Create a AWS ECS cluster
# - You should use ${var.group_name} as prefix to prevent naming conflicts
resource "aws_ecs_cluster" "app_disease" {
  name = "${var.group_name}_${terraform.workspace}_app_disease_cluster-4" # TODO: change here
}

# Define the task so that your cluster can create task instance later
# - You should use ${var.group_name} as the prefix of the family name
# - You can alter cpu and memory if you need more, cpu = 256 = 0.25 vCPU and
#     memory = 512M should be sufficient in general
# - If you have multiple containers for a task, you can fill them all in
resource "aws_ecs_task_definition" "app_disease" {
  family                   = "${var.group_name}_${terraform.workspace}_app_disease_task_def-4"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  container_definitions = jsonencode([
    {
      name      = "${var.group_name}_${terraform.workspace}_app_disease-4" # TODO: change here
      image     = "oak02/diseasehub-frontend:latest"                                   # TODO: change here
      essential = true
      portMappings = [
        {
          containerPort = 8888 # TODO: change here
          hostPort      = 8888 # TODO: change here
          appProtocol   = "http"
          name          = "app_disease-test-8888-tcp-4" # TODO: change here
        }
      ]
    }
  ])
}

# Fetch available subnets, shouldn't need to change this except the local
#   resource name.
# - var.vpc_id will be injected by the pipeline
data "aws_subnets" "app_disease" {
  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }
}

# Defines a service discovery namespace. Will be useful for service connect
# - You should use ${var.group_name} as the prefix of the name
resource "aws_service_discovery_http_namespace" "app_disease" {
  name = "${var.group_name}-${terraform.workspace}-discovery-namespace-app_disease-4" # TODO: change here
}

# Create a service instance using the task definition above
# - You should use ${var.group_name} as the prefix of the name
# - Usually you only need 1 service, but you may change this if need more
# - the port_name and discovery_name are corresponding to the configuration in
#     aws_ecs_task_definition above
resource "aws_ecs_service" "app_disease" {
  name            = "${var.group_name}-${terraform.workspace}-app_disease-ecs-service-4" # TODO: change here
  cluster         = aws_ecs_cluster.app_disease.id                           # TODO: change here
  task_definition = aws_ecs_task_definition.app_disease.arn                  # TODO: change here
  desired_count   = 1                                                      # TODO: change here
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.app_disease.ids # TODO: change here
    assign_public_ip = true
  }
  service_connect_configuration {
    enabled   = true
    namespace = aws_service_discovery_http_namespace.app_disease.arn # TODO: change here
    service {
      client_alias {
        port = 80 # TODO: change here
      }
      port_name      = "app_disease-test-8888-tcp-4" # TODO: change here
      discovery_name = aws_service_discovery_http_namespace.app_disease.name # TODO: change here
    }
  }
}

# Set up a service discovery service
data "aws_service_discovery_service" "app_disease" {
  name         = "app_disease-service-discovery-service-4"                               # TODO: change here
  namespace_id = aws_service_discovery_http_namespace.app_disease.id # TODO: change here

  depends_on = [
    aws_ecs_service.app_disease # TODO: change here
  ]
}

# # This bridges the route on the gateway and your service.
# # - The pipeline will inject var.gateway_api_id
# # - integration_method is not the same as the methods in the gateway, it
# #     should be ANY here.
# # - vpc_connection_id will be injected by the pipeline
# resource "aws_apigatewayv2_integration" "app_disease" {
#   api_id             = var.gateway_api_id
#   integration_type   = "HTTP_PROXY"
#   integration_method = "ANY"
#   integration_uri    = data.aws_service_discovery_service.app_disease.arn # TODO: change here
#   connection_type    = "VPC_LINK"
#   connection_id      = var.vpc_connection_id
#   # None needed
#   # request_parameters = {
#   #   "overwrite:path" = "/$request.path.subpath" # TODO: change here
#   # }
# }

# # This defines the route, linking the integration and the route
# # - You may use wildcard in the route key. e.g. POST /${var.group_name}/*
# # - You should add /${var.group_name}/ as prefix of your route key to prevent 
# #     conflictions in route key
# # - You may add parameter in the path. e.g. GET /${var.group_name}/{param}
# resource "aws_apigatewayv2_route" "app_disease" {
#   api_id    = var.gateway_api_id
#   route_key = "GET /${var.group_name}/ecs/app_disease"                      # TODO: change here
#   target    = "integrations/${aws_apigatewayv2_integration.app_disease.id}" # TODO: change here
# }
