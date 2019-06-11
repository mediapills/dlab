locals {
  ec2_name = "${var.env_name}-endpoint"
  eip_name = "${var.env_name}-endpoint-EIP"
}

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
  subnet_id = "${aws_subnet.endpoint_subnet.id}"
  security_groups = ["${aws_security_group.endpoint_sec_group.id}"]

}

resource "aws_eip" "e_ip" {
  instance = "${aws_instance.endpoint.id}"
  vpc      = true
  tags = {
    Name = "${local.eip_name}"
    "${var.env_name}-Tag" = "${local.eip_name}"
    product = "${var.product}"
    "user:tag" = "${var.env_name}:${local.eip_name}"
  }
}

