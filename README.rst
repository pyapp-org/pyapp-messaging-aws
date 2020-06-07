#######################
pyApp - Messaging - AWS
#######################

*Let us handle the boring stuff!*

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/ambv/black
      :alt: Once you go Black...

`pyApp Messaging`_ support for AWS SQS and SNS. Currently only ASyncIO interfaces
are implemented.

.. _pyApp Messaging: https://github.com/pyapp-org/pyapp-messaging


Installation
============

Install using *pip*::

    pip install pyapp-messaging-aws

Install using *pipenv*::

    pipenv install pyapp-messaging-aws


Usage
=====

Interaction with AWS is via pyapp.aiobotocore_ extension, configuration of your
AWS credentials is required.

This package provides the following connection interfaces:

- ``pyapp_ext.messaging_aws.aio.SQSSender``::

    SEND_MESSAGE_QUEUES = {
        "aws": (
            "pyapp_ext.messaging_aws.aio.SQSSender",
            {"queue_name": "my-queue"},
        )
    }

- ``pyapp_ext.messaging_aws.aio.SQSReceiver``::

    RECEIVE_MESSAGE_QUEUES = {
        "aws": (
            "pyapp_ext.messaging_aws.aio.SQSSender",
            {"queue_name": "my-queue"},
        )
    }

- ``pyapp_ext.messaging_aws.aio.SNSSender``


The following example obtains an S3 client::

    from pyapp_ext.aiobotocore import create_client

    s3 = create_client("S3")


.. _pyapp.aiobotocore: https://github.com/pyapp-org/pyapp.aiobotocore

API
===

`pyapp_ext.aiobotocore.create_client(service_name: str, *, credentials: str = None, **client_kwargs)`

    Get an async botocore service client instance.


`pyapp_ext.aiobotocore.get_session(default: str = None) -> Session`

    Get named `Session` instance.
