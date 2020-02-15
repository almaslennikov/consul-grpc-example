import logging
import sys

import grpc

import example_pb2
import example_pb2_grpc

from argparse import ArgumentParser
import requests

consul_port = None
resolver = None


# The default (most popular) way of name resolving in grpc is through DNS protocol.
# This function is a dirty hack meant to workaround the issue with grpc being unable to resolve
# DNS queries with authorities (couldn't find any meaningful info in the web).
def resolve_service_address(service_name):
    # Query string parameter 'passing' filters the query to look for only healthy instances
    response = requests.get('http://127.0.0.1:{}/v1/catalog/service/{}?passing'.format(consul_port, service_name))
    if response.status_code is not 200:
        raise requests.HTTPError('Failed to find service: {}'.format(response.text))

    service_info = response.json()[0]
    return '{}:{}'.format(service_info['Address'], service_info['ServicePort'])


def get_service_channel(service_name):
    if resolver == 'dns':
        # To retrieve service port from DNS query we need to request SRV record
        # Link below leads to gRPC proposal that makes use of DNS SRV records
        # https://github.com/grpc/proposal/blob/master/A5-grpclb-in-dns.md
        # gRPC doc article about name resolution
        # https://github.com/grpc/grpc/blob/master/doc/naming.md
        service_uri = 'dns:///127.0.0.1:{port}/_{service_name}.service.consul'.format(port=consul_port,
                                                                                      service_name=service_name)
    elif resolver == 'http':
        service_uri = resolve_service_address(service_name)

    return grpc.insecure_channel(service_uri)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    parser = ArgumentParser()
    parser.add_argument('--resolver', type=str,
                        help='Method of resolving service names from consul: DNS (default) or HTTP (workaround)',
                        choices=['dns', 'http'], default='dns')
    args = parser.parse_args()
    resolver = args.resolver
    # 8600 - Consul DNS interface port
    # 8500 - Consul HTTP API port
    consul_port = 8600 if resolver == 'dns' else 8500

    logging.info('Starting calculator client configuration...')

    calculator_stub = example_pb2_grpc.CalculatorStub(get_service_channel('calculator'))

    while True:
        # logging.info('Enter the number and the power')
        # value = float(input())
        # power = float(input())

        value, power = 2, 3

        logging.info('Requesting {}^{} calculation'.format(value, power))

        result = calculator_stub.CalculatePower(
            example_pb2.Operands(num1=example_pb2.Number(value=value), num2=example_pb2.Number(value=power)))

        logging.info('Result: {}'.format(result.value))
