import flask

app = flask.Flask(__name__)

import todolist_pb2
import todolist_pb2_grpc
from name_resolver import get_service_channel

from argparse import ArgumentParser
import logging
import json

todolist_stub = None

@app.route('/health', methods=['GET'])
def health():
    return 'I am alive!', 200


@app.route('/', methods=['GET'])
def serve_index_page():
    return flask.send_from_directory('assets', 'index.html')

@app.route('/api/items/<string:id>', methods=['DELETE'])
def remove_item(id):
    todolist_stub.RemoveItem(todolist_pb2.Id(id=id))
    return '', 200

@app.route('/api/items', methods=['GET', 'POST'])
def process_items():
    if flask.request.method == 'POST':
        name = flask.request.json['name']
        todolist_stub.AddItem(todolist_pb2.Name(name=name))
        return '', 200
    elif flask.request.method == 'GET':
        response = todolist_stub.GetItems(todolist_pb2.Stub())
        items = []
        for item in response.items:
            items.append({'name': item.name.name, 'id': item.id.id})

        return json.dumps({'items': items}), 200


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--resolver', type=str,
                        help='Method of resolving service names from consul: DNS (default) or HTTP (workaround)',
                        choices=['dns', 'http', 'grpc-dns'], default='dns')
    args = parser.parse_args()

    logging.info('Starting todo list web server configuration...')

    # Resolve service fqdn using Consul and create a channel to it
    grpc_channel = get_service_channel('todolist', args.resolver)
    todolist_stub = todolist_pb2_grpc.TodoListStub(grpc_channel)
    app.run(host='localhost', port=50052)
