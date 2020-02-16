# Summary

This is an example of two python microservices communicating with each other via gRPC using Consul as service registry.

## Features

* Service registration
* gRPC health checking
* HTTP or DNS service names resolution

# Prerequisites

* Python 2.7+ or 3.4+
* Python packages: grpcio, grpcio-tools, dnspython, requests, grpc-health-checking
* Consul binary (https://www.consul.io/downloads.html)

# Setup

1. Compile protobuf services definitions: `python -m grpc_tools.protoc --python_out=. --grpc_python_out=. todolist.proto`
2. Run Consul binary: `consul agent -dev -enable-script-checks -config-dir=./consul.d`
3. Run calculator service: `python todolist_service.py`
4. Run calculator client: `python web_server.py [--resolver {dns,http,grpc-dns}]`

# Usage

* Access `http://localhost:50052` from your browser and have fun!
* Monitor services from Consul UI running at`http://localhost:8500`
