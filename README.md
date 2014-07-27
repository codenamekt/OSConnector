OSConnector
=================


Objective:

1.   Reduce the lines of code to maintain.
2.   Auto discover all services and service endpoints available to tenant.
3.   Instantiate clients with their respective credential signatures as they
vary from client to client.
4.   Easily add new clients for new services as they become available. (ex.
Oslo, Heat, etc.)


I've provided two public methods (`ConnectorExample.flavors()` and
`ConnectorExample.images()`) that provide a decent chunk of cloud data with
minimal coding.


To Run
------


From OSConn directory:

```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements
```

Open osconn and change AUTH\_URL, AUTH\_USER, AUTH\_PASS, AUTH\_TENANT to
point to your cloud and tenant.

`python osconn.py`


Client Inconsistencies
----------------------


See code:

```python
OpenStackConnector.\_auth\_kwargs
OpenStackConnector.\_token\_kwargs
OpenStackConnector.\_type\_kwargs
```

The OpenStack clients vary in what type of arguments are needed to
instantiate them. This is an area that the community could improve upon.
Two types of authentication for service clients: "auth": Authentice service
through Keystone. "token": Authenticate using token provided by Keystone.
\*\*Password keyword argument also varies in auth type clients.

TODO
----

*   FIXME(Toby): Setup testing with tox. Write tests.
*   FIXME(Toby): Object-store uses a different method for instantiating a client.
*   FIXME(Toby): Discover Keystone API version like others. Regex AUTH\_URL for
/v2.0/?
*   FIXME(Toby): Support regions by allowing tenant to specify priority which can
translate to how we sort the list of clients. Glance and Heat may be the
only two that support this. Clients for other services go through
Keystone. Does Keystone select regions internally?
*   FIXME(Toby): Try..except.. When a region in the list fails try next region.
