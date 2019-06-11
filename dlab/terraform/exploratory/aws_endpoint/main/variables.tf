variable "access_key_var" {}

variable "secret_key_var" {}

variable "env_name" {
  default = "test"
}

variable "region_var" {
  default = "us-west-2"
}

variable "zone_var" {
  default = "us-west-2a"
}

variable "product_name" {
  default = "dlab"
}

variable "cidr_range" {
  default = "172.31.1.0/24"
}

variable "instance_shape" {
  default = "t2.micro"
}

variable "key_name_var" {}

variable "ami" {
  type = "map"
  default = {
    "debian" = "ami-08692d171e3cf02d6" #258751437250/ami-ubuntu-18.04-1.13.0-00-1543963388
    "redhat" = "ami-223f945a" #RHEL-7.4_HVM-20180103-x86_64-2-Hourly2-GP2
  }
}

variable "env_os" {}