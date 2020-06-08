"""
pyApp AsyncIO Messaging - AWS
~~~~~~~~~~~~~~~~~~~~~

Messaging integration with AWS SQS and SNS.

"""

from .sqs import SQSSender, SQSReceiver
from .sns import SNSSender, SNSReceiver

__all__ = ("SQSSender", "SQSReceiver", "SNSSender", "SNSReceiver")


class Extension:
    """
    pyApp AWS AIO Messaging extension
    """
