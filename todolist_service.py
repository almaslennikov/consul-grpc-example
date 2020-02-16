import logging
import sys
import uuid
from concurrent import futures

import grpc
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

import todolist_pb2
import todolist_pb2_grpc

port = 50051
health_check_servicer = None


class TodoListServicer(todolist_pb2_grpc.TodoListServicer):
    def __init__(self):
        self.items = []

    def AddItem(self, request, context):
        name = request.name
        id = str(uuid.uuid4())

        logging.info('Add item ({}, {})'.format(name, id))

        self.items.append({
            'name': name,
            'id': id
        })

        return todolist_pb2.Id(id=id)

    def GetItems(self, request, context):
        logging.info('Get items: {}'.format(self.items))

        return todolist_pb2.Items(items=map(lambda item: todolist_pb2.Item(name=todolist_pb2.Name(name=item['name']),
                                                                           id=todolist_pb2.Id(id=item['id'])),
                                            self.items))

    def RemoveItem(self, request, context):
        logging.info('Remove item ({})'.format(request.id))

        self.items = list(filter(lambda item: item['id'] != request.id, self.items))
        return todolist_pb2.Stub()


HealthCheckStatus = health_pb2.HealthCheckResponse


def set_health_check_status(status):
    health_check_servicer.set('', status)


def serve():
    logging.info('Starting configuration...')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    todolist_pb2_grpc.add_TodoListServicer_to_server(
        TodoListServicer(), server)

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
