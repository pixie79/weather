variable "log_level" {
  type        = string
  default     = "INFO"
  description = "Log level for lambda"
  validation {
    condition     = contains(["INFO", "WARNING", "ERROR", "CRITICAL", "DEBUG"], var.log_level)
    error_message = "Allowed values for LOG_LEVEL are \"INFO\", \"WARNING\", \"ERROR\", \"DEBUG\" or \"CRITICAL\"."
  }
}

variable "windy_api_key" {
  type        = string
  description = "value of windy token"
  sensitive   = true
}

variable "wunderground_station_id_0" {
  type        = string
  description = "value of wunderground station id 0"
}

variable "wunderground_station_id_1" {
  type        = string
  description = "value of wunderground station id 1"
}

variable "wunderground_station_key_0" {
  type        = string
  description = "value of wunderground station key 0"
}

variable "wunderground_station_key_1" {
  type        = string
  description = "value of wunderground station key 1"
}
