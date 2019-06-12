# Local vars for EC2-endpoint
locals {
  ec2_name = "${var.env_name}-endpoint"
  eip_name = "${var.env_name}-endpoint-EIP"
}

#Creating EC2-endpoint, if VPC NOT exists
resource "aws_instance" "endpoint" {
  ami = "${var.ami[var.env_os]}"
  instance_type = "${var.instance_shape}"
  key_name = "${var.key_name_var}"
  tags = {
    Name = "${local.ec2_name}"
    "${var.env_name}-Tag" = "${local.ec2_name}"
    product = "${var.product}"
    "user:tag" = "${var.env_name}:${local.ec2_name}"
  }
  associate_public_ip_address = "true"
  subnet_id = "${aws_subnet.endpoint_subnet[0].id}"
  security_groups = ["${aws_security_group.endpoint_sec_group[0].id}"]
  count = "${1 - var.vpc_check}"
}

#Creating Elastic IP, if VPC NOT exists
resource "aws_eip" "e_ip" {
  instance = "${aws_instance.endpoint[0].id}"
  vpc      = true
  tags = {
    Name = "${local.eip_name}"
    "${var.env_name}-Tag" = "${local.eip_name}"
    product = "${var.product}"
    "user:tag" = "${var.env_name}:${local.eip_name}"
  }
  count = "${1 - var.vpc_check}"
}


#Creating EC2-endpoint, if VPC exists
resource "aws_instance" "endpoint1" {
  ami = "${var.ami[var.env_os]}"
  instance_type = "${var.instance_shape}"
  key_name = "${var.key_name_var}"
  tags = {
    Name = "${local.ec2_name}"
    "${var.env_name}-Tag" = "${local.ec2_name}"
    product = "${var.product}"
    "user:tag" = "${var.env_name}:${local.ec2_name}"
  }
  associate_public_ip_address = "true"
  subnet_id = "${aws_subnet.endpoint_subnet1[0].id}"
  security_groups = ["${aws_security_group.endpoint_sec_group1[0].id}"]
  count = "${var.vpc_check}"

}

#Creating Elastic IP, if VPC exists
resource "aws_eip" "e_ip1" {
  instance = "${aws_instance.endpoint1[0].id}"
  vpc      = true
  tags = {
    Name = "${local.eip_name}"
    "${var.env_name}-Tag" = "${local.eip_name}"
    product = "${var.product}"
    "user:tag" = "${var.env_name}:${local.eip_name}"
  }
  count = "${var.vpc_check}"
}