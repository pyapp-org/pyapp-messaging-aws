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

.. _pyapp.aiobotocore: https://github.com/pyapp-org/pyapp.aiobotocore

This package provides the following connection interfaces:

- ``pyapp_ext.messaging_aws.aio.SQSSender``
    .. code-block:: python

        SEND_MESSAGE_QUEUES = {
            "sqs": (
                "pyapp_ext.messaging_aws.aio.SQSSender",
                {"queue_name": "my-queue"},
            )
        }

- ``pyapp_ext.messaging_aws.aio.SQSReceiver``
    .. code-block:: python

        RECEIVE_MESSAGE_QUEUES = {
            "sqs": (
                "pyapp_ext.messaging_aws.aio.SQSReceiver",
                {"queue_name": "my-queue"},
            )
        }

- ``pyapp_ext.messaging_aws.aio.SNSSender``
    .. code-block:: python

        SEND_MESSAGE_QUEUES = {
            "sns": (
                "pyapp_ext.messaging_aws.aio.SNSSender",
                # Topic name can also be an ARN
                {"topic_name": "my-topic"},
            )
        }

- ``pyapp_ext.messaging_aws.aio.SNSSender``
    Creates a SQS queue that is subscribed to the SNS topic to receive messages.

    .. code-block:: python

        RECEIVE_MESSAGE_QUEUES = {
            "sns": (
                "pyapp_ext.messaging_aws.aio.SNSReceiver",
                {"topic_name": "my-topic"},
            )
        }
