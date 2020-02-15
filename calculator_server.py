import logging
import math
from concurrent import futures
import sys

import grpc

import example_pb2
import example_pb2_grpc

port = 50051

class CalculatorServices(example_pb2_grpc.CalculatorServicer):
    def __init__(self):
        pass

    def CalculatePower(self, request, context):
        value = request.num1.value
        power = request.num2.value
        result = math.pow(value, power)
        logging.info('Calculate {}^{}: {}'.format(value, power, result))
        return example_pb2.Number(value=result)


def serve():
    logging.info('Starting configuration...')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    example_pb2_grpc.add_CalculatorServicer_to_server(
        CalculatorServices(), server)
    server.add_insecure_port('[::]:{}'.format(port))
    server.start()
    logging.info('Started listening on port {}'.format(port))
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    serve()
