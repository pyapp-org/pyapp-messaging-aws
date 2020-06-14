"""
AWS SQS Interfaces
~~~~~~~~~~~~~~~~~~

"""
import logging
from typing import Dict, Any, Optional, AsyncGenerator

import botocore.exceptions
from pyapp_ext.aiobotocore import aio_create_client
from pyapp_ext.messaging.aio import MessageSender, MessageReceiver, Message
from pyapp_ext.messaging.exceptions import QueueNotFound, ClientError

from .utils import parse_attributes, build_attributes

LOGGER = logging.getLogger(__name__)


class SQSBase:
    """
    Base Message Queue
    """

    __slots__ = ("queue_name", "aws_config", "client_args", "_client", "_queue_url", "loop")

    def __init__(
            self,
            *,
            queue_name: str,
            aws_config: str = None,
            client_args: Dict[str, Any] = None,
    ):
        self.queue_name = queue_name
        self.aws_config = aws_config
        self.client_args = client_args or {}

        self._client = None
        self._queue_url: Optional[str] = None

    def __repr__(self):
        return f"{type(self).__name__}(queue_name={self.queue_name!r})"

    async def open(self):
        """
        Open queue
        """
        client = await aio_create_client("sqs", self.aws_config, **self.client_args)

        try:
            response = await client.get_queue_url(QueueName=self.queue_name)

        except botocore.exceptions.ClientError as ex:
            await client.close()

            error_code = ex.response["Error"]["Code"]
            if error_code == "AWS.SimpleQueueService.NonExistentQueue":
                raise QueueNotFound(f"Unable to find queue `{self.queue_name}`")

            raise ClientError(error_code) from ex

        except Exception as ex:
            await client.close()
            raise ClientError() from ex

        self._client = client
        self._queue_url = response["QueueUrl"]

    async def close(self):
        """
        Close the queue
        """
        if self._client:
            await self._client.close()
            self._client = None

        self._queue_url = None

    async def configure(self):
        """
        Define any send queues
        """
        async with await aio_create_client("sqs", self.aws_config, **self.client_args) as client:
            try:
                response = await client.create_queue(QueueName=self.queue_name)

            except botocore.exceptions.ClientError as ex:
                error_code = ex.response["Error"]["Code"]
                raise ClientError(error_code) from ex

            except Exception as ex:
                raise ClientError() from ex

            return response["QueueUrl"]


class SQSSender(SQSBase, MessageSender):
    """
    Message sending interface for SQS
    """

    __slots__ = ()

    async def send_raw(self, body: bytes, *, content_type: str = None, content_encoding: str = None) -> str:
        """
        Publish a raw message (message is raw bytes)
        """
        attributes = build_attributes(
            ContentType=content_type, ContentEncoding=content_encoding
        )
        response = await self._client.send_message(
            QueueUrl=self._queue_url, MessageBody=body, MessageAttributes=attributes
        )
        return response["MessageId"]


class SQSReceiver(SQSBase, MessageReceiver):
    """
    Message receiving for SQS
    """

    __slots__ = ("wait_time",)

    def __init__(self, *, wait_time: int = 10, **kwargs):
        super().__init__(**kwargs)
        self.wait_time = wait_time

    async def receive_raw(self) -> AsyncGenerator[Message, None]:
        """
        Start receiving raw responses from the queue
        """
        queue_name = self.queue_name
        client = self._client
        queue_url = self._queue_url

        LOGGER.debug("Starting SQS Listener: %s", queue_name)

        while True:
            response = await client.receive_message(
                QueueUrl=queue_url,
                WaitTimeSeconds=self.wait_time,
                MessageAttributeNames=["ContentType", "ContentEncoding"],
            )

            if "Messages" in response:
                for msg in response["Messages"]:
                    try:
                        attrs = parse_attributes(
                            msg.pop("MessageAttributes")
                        )
                    except KeyError:
                        attrs = {}

                    yield Message(
                        msg.pop("Body"),
                        attrs.get("ContentType"),
                        attrs.get("ContentEncoding"),
                        msg,
                        self
                    )

            else:
                LOGGER.debug("No messages in queue %s", queue_name)

    async def delete(self, message: Message):
        """
        Delete a message from the queue (eg after successfully processing)
        """
        await self._client.delete_message(
            QueueUrl=self._queue_url,
            ReceiptHandle=message.raw["ReceiptHandle"]
        )
