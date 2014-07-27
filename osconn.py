#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Main OpenStack connector class.
Should support Grizzly, Havana, Icehouse (Untested), etc.

For OpenStack
'''

import pprint
import logging
import importlib

__pyver__ = ['2.7.3']
__created__ = ['11.23.2013']
__authors__ = ['Toby <codenamekt@gmail.com>']
__shortdoc__ = 'Main connector class.'
0


class OpenStackConnector(object):
    """
    Main OpenStack connector class.
    """
    def __init__(self, auth_url, username, password, tenant_name):
        """
        Helper to determine module for service type.
        Adding NotImplementedError for anything we don't want yet.
        """
        # TODO(Toby): Pass this in as an argument for dependency injection.
        self._type_module = {
            "identity": "keystoneclient.v2_0.client",
            "s3": NotImplementedError,
            "ec2": NotImplementedError,
            "image": "glanceclient.v2.client",
            "volume": "cinderclient.v1.client",
            "volumev2": "cinderclient.v2.client",
            "compute": "novaclient.v1_1.client",
            "computev3": "novaclient.v3.client",
            # "metering": "ceilometerclient.v2.client",
            "metering": NotImplementedError,
            # "object-store": "swiftclient.client",
            "object-store": NotImplementedError,
            # "orchestration": "heatclient.v1.client"
            "orchestration": NotImplementedError,
            "cloudformation": NotImplementedError
        }
        # Service clients.
        self._clients = dict()
        # Init list of keystone clients.
        self._clients['identity'] = list()
        # Initialize first keystone client for "token" auth.
        self._clients['identity'].append(self._identity(
            auth_url, username, password, tenant_name))
        # See README.rst section Client Inconsistencies
        self._auth_kwargs = {
            "type": "defined",
            "auth_url": auth_url,
            "username": username,
            "api_key": password,
            "project_id": tenant_name
        }
        self._token_kwargs = {
            "type": "token",
            "endpoint": None,
            "token": None,
        }
        # Helper for kwargs to initialize service client.
        self._type_kwargs = {
            "identity": {
                "type": "defined",
                "auth_url": auth_url,
                "username": username,
                "password": password,
                "tenant_name": tenant_name
            },
            "image": self._token_kwargs,
            "volume": self._auth_kwargs,
            "compute": self._auth_kwargs,
            "volumev2": self._auth_kwargs,
            "metering": self._token_kwargs,
            "computev3": {
                "type": "defined",
                "auth_url": auth_url,
                "username": username,
                "password": password,
                "project_id": tenant_name
            },
            "orchestration": self._token_kwargs,
        }
        # Sevice objects.
        self._services = self._disc_services()
        # Instantiate all services with their respective clients.
        self._init_clients()

    def _identity(self, auth_url, username, password, tenant_name):
        """
        Get credentials. (ex. username, pass, etc)
        Return keystone client object.
        """
        serv_type = "identity"
        module = self._type_module[serv_type]
        this_client = importlib.import_module(module)
        return this_client.Client(auth_url=auth_url,
                                  username=username,
                                  password=password,
                                  tenant_name=tenant_name)

    def _disc_services(self):
        """
        Return list of service objects.
        ex.
        <Service {u'type': u'volumev2',
                  u'description': u'Cinder Volume Service V2',
                  u'name': u'cinder',
                  u'id': u'f9336b58ecd649b9908b5a92ecaa2626'}>
        """
        return self._clients['identity'][0].service_catalog.get_endpoints()

    def _init_clients(self):
        """
        Traverse discovered services and instantiate clients for each service
        endpoint.
        """
        for service in self._services:
            # Add service to client dictionary if key does not exist
            if service not in self._clients:
                self._clients[service] = list()

            module = self._type_module[service]
            if module == NotImplementedError:
                msg = "Service %s not yet implemented." % (service)
                logging.warning(msg)
            else:
                this_client = importlib.import_module(module)
                ident = self._clients['identity'][0]
                scat = ident.service_catalog
                endpoints = scat.get_endpoints(service)[service]
                for endpoint in endpoints:
                    if self._type_kwargs[service]['type'] == "token":
                        this_kwargs = self._type_kwargs[service].copy()
                        # Remove type keyword when passing kwargs to client.
                        del(this_kwargs["type"])
                        this_kwargs['endpoint'] = endpoint['publicURL']
                        this_kwargs['token'] = ident.auth_token
                        self._clients[service].append(
                            this_client.Client(**this_kwargs))
                    elif self._type_kwargs[service]["type"] == "defined":
                        this_kwargs = self._type_kwargs[service].copy()
                        # Remove type keyword when passing kwargs to client.
                        del(this_kwargs["type"])
                        self._clients[service].append(
                            this_client.Client(**this_kwargs))
                    else:
                        msg = ("Authentication type %s not supported." %
                               self._type_kwargs[service]["type"])
                        raise NotImplementedError(msg)


class ConnectorExample(OpenStackConnector):
    """
    Example of using the clients from a Connector class. The lines of
    code necessary to interface with the clients is minimal.
    """

    def flavors(self):
        """
        Returns a list of all flavors from all nova services.
        """
        master_flavor_list = list()
        for client in self._clients['compute']:
            for flavor in client.flavors.list():
                master_flavor_list.append(flavor)
        return master_flavor_list

    def images(self):
        """
        Returns a list of all images from all glance services.
        """
        master_image_list = list()
        for client in self._clients['image']:
            for image in client.images.list():
                master_image_list.append(image)
        return master_image_list


if __name__ == '__main__':
    """
    Example Usage
    """

    AUTH_URL = "http://example.com:5000/v2.0"
    AUTH_USER = "toby"
    AUTH_PASS = "password"
    AUTH_TENANT = "toby_project"

    CONN = ConnectorExample(
        auth_url=AUTH_URL,
        username=AUTH_USER,
        password=AUTH_PASS,
        tenant_name=AUTH_TENANT)

    PP = pprint.PrettyPrinter(indent=2)
    PP.pprint(CONN.flavors())
    PP.pprint(CONN.images())
