variable "access_key_var" {}

variable "secret_key_var" {}

variable "project_tag" {
  default = "dem-test-terraform5"
}

variable "endpoint_tag" {
  default = "dem_endpoint"
}

variable "user_tag" {
  default = "demyan_mysakovets@epam.com"
}

variable "custom_tag" {
  default = ""
}

variable "notebook_name" {
  default = "jup"
}

variable "region_var" {
  default = "us-west-2"
}

variable "zone_var" {
  default = "us-east1-c"
}

variable "product_name" {
  default = "dlab"
}

variable "vpc_id" {
  default = "vpc-83c469e4"
}

variable "cidr_range" {
  default = "172.31.134.0/24"
}

variable "traefik_cidr" {
  default = "172.31.135.0/28"
}

variable "ami" {
  type = "map"
  default = {
     "debian" = "ami-0dc34f4b016c9ce49" #ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-arm64-server-20190212.1
     "redhat" = "ami-223f945a" #RHEL-7.4_HVM-20180103-x86_64-2-Hourly2-GP2
  }
}

variable "env_os" {
  default = "debian"
}

variable "instance_type" {
  default = "t2.micro"
}

variable "slave_count" {
  default = 2
}
