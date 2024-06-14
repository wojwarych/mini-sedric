terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region = var.region
}

resource "aws_ecr_repository" "mini-sedric" {
  name = "mini-sedric-api"
}

resource "aws_ecs_cluster" "cluster" {
  name = "mini-sedric-cluster"
}

resource "aws_vpc" "mini_sedric" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "public_subnet" {
  count             = length(var.public_subnet_cidrs)
  vpc_id            = aws_vpc.mini_sedric.id
  cidr_block        = element(var.public_subnet_cidrs, count.index)
  availability_zone = element(var.azs, count.index)
}

resource "aws_subnet" "private_subnet" {
  count             = length(var.private_subnet_cidrs)
  vpc_id            = aws_vpc.mini_sedric.id
  cidr_block        = element(var.private_subnet_cidrs, count.index)
  availability_zone = element(var.azs, count.index)
}

resource "aws_internet_gateway" "gateway" {
  vpc_id = aws_vpc.mini_sedric.id
}

resource "aws_route_table" "second_rt" {
  vpc_id = aws_vpc.mini_sedric.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gateway.id
  }
}

resource "aws_route_table_association" "public_subnet_association" {
  count          = length(var.public_subnet_cidrs)
  subnet_id      = element(aws_subnet.public_subnet[*].id, count.index)
  route_table_id = aws_route_table.second_rt.id
}

module "container_definition" {
  source          = "cloudposse/ecs-container-definition/aws"
  version         = "0.61.1"
  container_name  = "mini-sedric-container"
  container_image = "827878376937.dkr.ecr.eu-central-1.amazonaws.com/mini-sedric-api:latest"
  port_mappings = [
    {
      containerPort = 80
      hostPort      = 80
      protocol      = "tcp"
    }
  ]
}

module "security_group" {
  source              = "terraform-aws-modules/security-group/aws//modules/http-80"
  name                = "mini-sedric-sg"
  vpc_id              = aws_vpc.mini_sedric.id
  ingress_cidr_blocks = ["0.0.0.0/0"]
}

module "alb" {
  source          = "terraform-aws-modules/alb/aws"
  version         = "~>9.9.0"
  name            = "mini-sedric-alb"
  vpc_id          = aws_vpc.mini_sedric.id
  subnets         = aws_subnet.public_subnet[*].id
  security_groups = [module.security_group.security_group_id]


  listeners = {
    http-listener = {
      port     = 80
      protocol = "HTTP"
      forward = {
        target_group_key = "ex-instance"
      }
    }
  }

  target_groups = {
    ex-instance = {
      name              = "mini-sedric-tg"
      port              = 80
      protocol          = "HTTP"
      target_type       = "ip"
      vpc_id            = aws_vpc.mini_sedric.id
      create_attachment = false
      health_check = {
        path    = "/docs"
        port    = "80"
        matcher = "200-399"
      }
    }
  }

}

module "ecs_alb_service_task" {
  source                            = "cloudposse/ecs-alb-service-task/aws"
  version                           = "0.75.0"
  namespace                         = "sdrc"
  stage                             = "dev"
  name                              = "mini-sedric"
  container_definition_json         = one(module.container_definition.*.json_map_encoded_list)
  ecs_cluster_arn                   = aws_ecs_cluster.cluster.arn
  launch_type                       = "FARGATE"
  vpc_id                            = aws_vpc.mini_sedric.id
  security_group_ids                = [module.security_group.security_group_id]
  subnet_ids                        = aws_subnet.public_subnet[*].id
  ignore_changes_task_definition    = false
  health_check_grace_period_seconds = 60
  ecs_load_balancers = [
    {
      target_group_arn = module.alb.target_groups.ex-instance.arn
      elb_name         = ""
      container_name   = "mini-sedric-container"
      container_port   = 80
    }
  ]
  assign_public_ip = true
}
