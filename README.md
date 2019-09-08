# SimpleTOTP
A lightweight time based OTP (One Time Password) service

# Overview
This is a tiny runnable program to generate time based OTP. It creates a random password which is activated for specified time. The password can be validated or used after.

# Prerequisites
This program requires Python 3.7.x and TinyDB to run. 
Sample installation in Ubuntu:
`apt-get install python3`
`pip install tinydb`
This service has 3 operations: create, validate, and use. 

# Create OTP
This service is provided to create time based OTP. See this sample below.
See this file named createOTP.json below.
```
  { "ApplicationId": "Mobile", 
  "OTPDuration": 300,
  "OTPLength": 6, 
  "OTPContentType": "integer",
  "OTPIdentifier": "103980480AFFS", 
  "MaxValidation": 3}
```
Then invoke the service, using curl.
```
  curl -d @createOTP.json http://localhost:8000/create
```
Then you will get this response:
```
  {"ApplicationId": "Mobile", "OTPIdentifier": "103980480AFFS", "OTPValue": "544348", "errorCode": "200"}
```
# Validate OTP
This service is provided for OTP Validation. OTP is valid until it get expired or reaching the maximum validation retries. See this sample payload below. 
Create a file to store the payload, validateOTP.json. 
```
  {"ApplicationId": "Mobile",
  "OTPIdentifier": "103980480AFFS", 
  "OTPChallenge": "544348"}
```
Then invoke the service, using curl.
```
  curl -d @validateOTP.json http://localhost:8000/validate
```
Then you will get this response:
```
  {"OTPResult": "OTP Valid", "errorCode": "200", "ValidationRetries": 1, "ApplicationId": "Mobile", "OTPIdentifier": "103980480AFFS", "OTPChallenge": "544348"}
```
 # Use OTP
This service is provided for validating OTP and then make it used. This operation make your OTP is not valid anymore. See this sample payload below. 
Create a file to store the payload, useOTP.json. 
```
{"ApplicationId": "Mobile",
  "OTPIdentifier": "103980480AFFS", 
  "OTPChallenge": "544348"}
```
Then invoke the service, using curl.
```
  curl -d @useOTP.json http://localhost:8000/use
```
Then you will get this response:
```
  {"OTPResult": "OTP Valid", "errorCode": "200", "ValidationRetries": 1, "ApplicationId": "Mobile", "OTPIdentifier": "103980480AFFS", "OTPChallenge": "544348"}
```
# Response & Error Codes
```
  200 The operation is successfully executed
  500 Service not available
  401 OTP is not valid
  402 OTP validation is reaching maximum
  403 OTP is expired
  404 OTP is not found
```

  
  
