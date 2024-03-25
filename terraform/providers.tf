provider "aws" {
  region = "eu-west-2"
  default_tags {
    tags = {
      Environment = "Test"
      Name        = "Pixie Weather"
    }
  }
}

terraform {
  required_version = "1.7.4"
  backend "s3" {
    bucket = "pixie79-terraform"
    key    = "weather.tfstate"
    region = "eu-west-2"
  }
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = ">=2.5.1"
    }
    aws = {
      source  = "hashicorp/aws"
      version = ">=4.42.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = ">=2.4.2"
    }
  }
  #  backend "s3" {
  #  }
}
