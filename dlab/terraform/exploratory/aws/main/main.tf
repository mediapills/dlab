provider "aws" {
  access_key = "${var.access_key_var}"
  secret_key = "${var.secret_key_var}"
  region = "${var.region_var}"
}

module "notebook" {
  source = "../modules/notebook"
  project_tag = "${var.project_tag}"
  endpoint_tag = "${var.endpoint_tag}"
  user_tag = "${var.user_tag}"
  custom_tag = "${var.custom_tag}"
  notebook_name = "${var.notebook_name}"
  region = "${var.region_var}"
  zone = "${var.zone_var}"
  product = "${var.product_name}"
  vpc = "${var.vpc_id}"
  cidr_range = "${var.cidr_range}"
  traefik_cidr = "${var.traefik_cidr}"
  ami = "${var.ami}"
  env_os = "${var.env_os}"
  instance_type = "${var.instance_type}"
}

module "data_engine" {
  source = "../modules/data_engine"
  project_tag = "${var.project_tag}"
  endpoint_tag = "${var.endpoint_tag}"
  user_tag = "${var.user_tag}"
  custom_tag = "${var.custom_tag}"
  notebook_name = "${var.notebook_name}"
  region = "${var.region_var}"
  zone = "${var.zone_var}"
  product = "${var.product_name}"
  vpc = "${var.vpc_id}"
  cidr_range = "${var.cidr_range}"
  traefik_cidr = "${var.traefik_cidr}"
  ami = "${var.ami}"
  env_os = "${var.env_os}"
  instance_type = "${var.instance_type}"
  slave_count = "${var.slave_count}"
  subnet_id = "${module.notebook.}"
}