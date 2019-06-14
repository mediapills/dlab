provider "aws" {
  access_key = var.access_key_var
  secret_key = var.secret_key_var
  region     = var.region_var
}

module "aws_endpoint" {
  source         = "../modules/aws_endpoint"
  env_name       = var.env_name
  region         = var.region_var
  zone_var       = var.zone_var
  product        = var.product_name
  cidr_range     = var.cidr_range
  instance_shape = var.instance_shape
  key_name_var   = var.key_name_var
  ami            = var.ami
  env_os         = var.env_os
  vpc_id_existed = var.vpc_id_existed
  subnet_id      = var.subnet_id
  network_type   = var.network_type
}