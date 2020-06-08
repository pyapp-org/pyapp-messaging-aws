from .sqs import SQSSender, SQSReceiver
from .sns import SNSSender

__all__ = ("SQSSender", "SQSReceiver", "SNSSender")


class Extension:
    """
    pyApp AWS AIO Messaging extension
    """
