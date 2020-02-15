import logging
import sys

import grpc

import example_pb2
import example_pb2_grpc

port = 50051

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logging.info('Starting calculator client configuration...')

    # channel = grpc.insecure_channel('localhost:{}'.format(port))
    channel = grpc.insecure_channel('dns:///127.0.0.1:8600/calculator.service.consul.:50001')
    # channel = grpc.insecure_channel('http://localhost:8500/v1/catalog/service/calculator')
    stub = example_pb2_grpc.CalculatorStub(channel)

    while True:
        # logging.info('Enter the number and the power')
        # value = float(input())
        # power = float(input())

        value, power = 2, 3

        logging.info('Requesting {}^{} calculation'.format(value, power))

        result = stub.CalculatePower(
            example_pb2.Operands(num1=example_pb2.Number(value=value), num2=example_pb2.Number(value=power)))

        logging.info('Result: {}'.format(result.value))