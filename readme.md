# Summary

This is an example of two python microservices communicating with each other using Consul.

## Features

* Service registration
* gRPC health checking
* HTTP or DNS service names resolution

# Prerequisites

* Python 2.7+ or 3.4+
* Python packages: grpcio, grpcio-tools, dnspython, requests, grpc-health-checking
* Consul binary (https://www.consul.io/downloads.html)

# Setup

1. Compile protobuf services definitions: python -m grpc_tools.protoc --python_out=. --grpc_python_out=. example.proto
2. Run calculator service: python calculator_server.py
3. Run Consul binary
4. Run calculator client: python calculator_client.py