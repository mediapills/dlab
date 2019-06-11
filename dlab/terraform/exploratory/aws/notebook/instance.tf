
resource "aws_instance" "notebook" {
  ami           = "${var.ami[var.env_os]}"
  instance_type = "${var.instance_type}"
  subnet_id = "${aws_subnet.subnet.id}"
  security_groups = ["${aws_security_group.nb-sg.id}"]
  iam_instance_profile = "${aws_iam_instance_profile.nb_profile.name}"
  tags = {
    Name = "${var.project_tag}-${var.notebook_name}"
    Project_Tag = "${var.project_tag}"
    Endpoint_Tag = "${var.endpoint_tag}"
    User_Tag = "${var.user_tag}"
    Custom_Tag = "${var.custom_tag}"
  }
}