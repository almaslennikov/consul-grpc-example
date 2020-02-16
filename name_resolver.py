import dns.resolver
import grpc
import requests

LOCALHOST = '127.0.0.1'

CONSUL_HTTP_PORT = 8500
CONSUL_DNS_PORT = 8600

# The default (most popular) way of name resolving in grpc is through DNS protocol.
# This function makes use of Consul's HTTP API to workaround the issue with grpc being unable to resolve
# DNS queries with authorities (couldn't find any meaningful info in the web).
def _resolve_service_fqdn_via_http(service_name):
    # Query string parameter 'passing' filters the query to look for only healthy instances
    response = requests.get('http://{}:{}/v1/catalog/service/{}?passing'.format(LOCALHOST, CONSUL_HTTP_PORT, service_name))
    if response.status_code is not 200:
        raise requests.HTTPError('Failed to find service: {}'.format(response.text))

    service_info = response.json()[0]
    return '{}:{}'.format(service_info['Address'], service_info['ServicePort'])


# Use dnspython library to resolve service fqdn
def _resolve_service_fqdn_via_dns(service_name):
    resolver = dns.resolver.Resolver()
    # Set up resolving via Consul's DNS server
    resolver.nameservers = [LOCALHOST]
    resolver.nameserver_ports[LOCALHOST] = CONSUL_DNS_PORT

    dns_query = '{}.service.consul'.format(service_name)
    name_answer = resolver.query(dns_query)
    srv_answer = resolver.query(dns_query, dns.rdatatype.SRV)
    return '{}:{}'.format(name_answer[0], srv_answer[0].port)


# gRPC team is discussing adding custom resolvers in python.
# Function below is a workaround until this feature is released.
def get_service_channel(service_name, resolver='dns'):
    service_uri = ''
    if resolver == 'dns':
        service_uri = _resolve_service_fqdn_via_dns(service_name)
    elif resolver == 'grpc-dns':
        # To retrieve service port from DNS query we need to request SRV record
        # Link below leads to gRPC proposal that makes use of DNS SRV records
        # https://github.com/grpc/proposal/blob/master/A5-grpclb-in-dns.md
        # gRPC doc article about name resolution
        # https://github.com/grpc/grpc/blob/master/doc/naming.md
        service_uri = 'dns:///127.0.0.1:{port}/{service_name}.service.consul'.format(port=CONSUL_DNS_PORT,
                                                                                     service_name=service_name)
    elif resolver == 'http':
        service_uri = _resolve_service_fqdn_via_http(service_name)

    return grpc.insecure_channel(service_uri)
