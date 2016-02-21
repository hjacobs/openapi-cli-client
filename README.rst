==========================
OpenAPI/Swagger CLI Client
==========================

Python command line client for REST APIs defined with `OpenAPI-Spec`_/Swagger-Spec.

This tool maps REST API operations to `Click`_ CLI commands.

**WORK IN PROGRESS**


Usage
=====

.. code-block:: bash

    $ sudo pip3 install -U openapi-cli-client
    $ openapi-cli-client http://petstore.swagger.io/v2/swagger.json pet get myid


.. _OpenAPI-Spec: https://github.com/OAI/OpenAPI-Specification/
.. _Click: http://click.pocoo.org/
