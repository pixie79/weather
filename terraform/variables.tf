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
