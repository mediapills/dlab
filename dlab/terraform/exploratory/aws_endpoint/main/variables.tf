# Main vars
variable "access_key_var" {}

variable "secret_key_var" {}
# Environment name
variable "env_name" {
  default = "test"
}

variable "region_var" {
  default = "us-west-2"
}

variable "zone_var" {
  default = "us-west-2a"
}
# Do not change
variable "product_name" {
  default = "dlab"
}
# Do not change
variable "cidr_range" {
  default = "172.31.1.0/24"
}

variable "instance_shape" {
  default = "t2.micro"
}
# Key name, existed in AWS account
variable "key_name_var" {}

# AMI of Ubuntu and RedHat. Ubuntu 18.04.1 (long term support), RedHat ???
variable "ami" {
  type = "map"
  default = {
    "debian" = "ami-08692d171e3cf02d6" #258751437250/ami-ubuntu-18.04-1.13.0-00-1543963388
    "redhat" = "ami-223f945a" #RHEL-7.4_HVM-20180103-x86_64-2-Hourly2-GP2
  }
}

# Variable used to import OS for EC2 (debian or redhat)
variable "env_os" {}

# Variable for check VPC existence (1 - if existed, 0 - if NOT existed and require creating)
variable "vpc_check" {}

# ID of existed VPC
variable "vpc_id_existed" {}

