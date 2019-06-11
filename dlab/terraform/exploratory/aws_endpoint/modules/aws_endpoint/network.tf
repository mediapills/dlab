locals {
  subnet_name = "${var.env_name}-subnet"
  sg_name = "${var.env_name}-sg"
}

resource "aws_vpc" "vpc" {
  cidr_block = "${var.cidr_range}"
}

resource "aws_internet_gateway" "gw" {
  vpc_id = "${aws_vpc.vpc.id}"

  tags = {
    Name = "main"
  }
}

resource "aws_subnet" "endpoint_subnet" {
  vpc_id     = "${aws_vpc.vpc.id}"
  cidr_block = "${var.cidr_range}"
  tags = {
    Name = "${local.subnet_name}"
    "${var.env_name}-Tag" = "${local.subnet_name}"
    product = "${var.product}"
    "user:tag" = "${var.env_name}:${local.subnet_name}"
  }
}

resource "aws_security_group" "endpoint_sec_group" {
  name        = "endpoint_sec_group"
  vpc_id      = "${aws_vpc.vpc.id}"
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