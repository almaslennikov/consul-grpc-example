import logging
import math
from concurrent import futures
import sys

import grpc

import example_pb2
import example_pb2_grpc

from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

port = 50051
health_check_servicer = None

class CalculatorServices(example_pb2_grpc.CalculatorServicer):
    def __init__(self):
        pass

    def CalculatePower(self, request, context):
        value = request.num1.value
        power = request.num2.value
        result = math.pow(value, power)
        logging.info('Calculate {}^{}: {}'.format(value, power, result))
        return example_pb2.Number(value=result)

HealthCheckStatus = health_pb2.HealthCheckResponse

def set_health_check_status(status):
    health_check_servicer.set('', status)


def serve():
    logging.info('Starting configuration...')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    example_pb2_grpc.add_CalculatorServicer_to_server(
        CalculatorServices(), server)

    set_health_check_status(HealthCheckStatus.UNKNOWN)
    health_pb2_grpc.add_HealthServicer_to_server(health_check_servicer, server)

    server.add_insecure_port('[::]:{}'.format(port))
    server.start()
    logging.info('Started listening on port {}'.format(port))
    set_health_check_status(HealthCheckStatus.SERVING)

    server.wait_for_termination()
    set_health_check_status(HealthCheckStatus.NOT_SERVING)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    # Implementation of gRPC health checking
    # https://github.com/grpc/grpc/blob/master/doc/health-checking.md
    # Consul can be configured to execute this check to track the service's health status
    # https://www.consul.io/docs/agent/checks.html
    health_check_servicer = health.HealthServicer()

    serve()
