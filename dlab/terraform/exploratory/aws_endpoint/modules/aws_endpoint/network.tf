# Local vars for tags
locals {
  subnet_name = "${var.env_name}-subnet"
  sg_name = "${var.env_name}-sg"
}




# Getting id from VPC, which already exists
data "aws_vpc" "existed" {
  id = "${var.vpc_id_existed}"
  count = "${var.vpc_check}"
}

# Creating VPC, which not exists
resource "aws_vpc" "vpc_create" {
  cidr_block = "${var.cidr_range}"
  count = "${1 - var.vpc_check}"
}

#Creating Gateway for VPC, if VPC NOT exists
resource "aws_internet_gateway" "gw" {
  vpc_id = "${aws_vpc.vpc_create[count.index].id}"

  tags = {
    Name = "main"
  }
  count = "${1 - var.vpc_check}"
}

#Creating Subnet in VPC, if VPC NOT exists
resource "aws_subnet" "endpoint_subnet" {
  vpc_id = "${aws_vpc.vpc_create[count.index].id}"
  cidr_block = "${var.cidr_range}"
  tags = {
    Name = "${local.subnet_name}"
    "${var.env_name}-Tag" = "${local.subnet_name}"
    product = "${var.product}"
    "user:tag" = "${var.env_name}:${local.subnet_name}"
  }
  count = "${1 - var.vpc_check}"
}

#Creating Security group in VPC, if VPC NOT exists
resource "aws_security_group" "endpoint_sec_group" {
  name        = "endpoint_sec_group"
  vpc_id      = "${aws_vpc.vpc_create[count.index].id}"
  count = "${1 - var.vpc_check}"
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
  Name = "${local.sg_name}"
  product = "${var.product}"
  "user:tag" = "${var.env_name}:${local.sg_name}"
  }
}

#Creating Subnet for VPC, if VPC exists
resource "aws_subnet" "endpoint_subnet1" {
  vpc_id = "${data.aws_vpc.existed[count.index].id}"
  cidr_block = "${var.cidr_range}"
  tags = {
    Name = "${local.subnet_name}"
    "${var.env_name}-Tag" = "${local.subnet_name}"
    product = "${var.product}"
    "user:tag" = "${var.env_name}:${local.subnet_name}"
  }
  count = "${var.vpc_check}"
}

#Creating Security group in VPC, if VPC exists
resource "aws_security_group" "endpoint_sec_group1" {
  name        = "endpoint_sec_group"
  vpc_id      = "${data.aws_vpc.existed[count.index].id}"
  count = "${var.vpc_check}"
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
  Name = "${local.sg_name}"
  product = "${var.product}"
  "user:tag" = "${var.env_name}:${local.sg_name}"
  }
}