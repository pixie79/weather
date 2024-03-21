# Environ Weather Proxy

This is an AWS Lambda proxy for the EnvironW Weather Board to send data to Windy.com

To save costs it does not use a secrets manager (although it should) but instead uses an
environment variable called WINDY_API_KEY to store the authentication token for the 
submission of data to windy.com.