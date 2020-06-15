from unittest import mock

import pytest
import botocore.exceptions

from pyapp_ext.messaging.exceptions import ClientError
from pyapp_ext.messaging_aws.aio import sqs


class TestSQSBase:
    @pytest.mark.asyncio
    async def test_open(self, monkeypatch):
        """
        Valid option request
        """

        mock_client = mock.AsyncMock(
            get_queue_url=mock.AsyncMock(return_value={"QueueUrl": "http://example.com/my_queue"})
        )
        mock_factory = mock.AsyncMock(return_value=mock_client)
        monkeypatch.setattr(sqs, "aio_create_client", mock_factory)

        target = sqs.SQSBase(queue_name="my_queue", aws_config="my_config")

        await target.open()

        mock_factory.assert_awaited_with("sqs", "my_config")
        mock_client.get_queue_url.assert_awaited_with(QueueName="my_queue")
        mock_client.close.assert_not_called()
        assert target._client is mock_client
        assert target._queue_url == "http://example.com/my_queue"

    @pytest.mark.asyncio
    async def test_open__queue_not_found(self, monkeypatch):
        """
        A queue was not found

        Ensure the client is closed.
        """

        mock_client = mock.AsyncMock(
            get_queue_url=mock.AsyncMock(
                side_effect=botocore.exceptions.ClientError({
                    "Error": {"Code": "AWS.SimpleQueueService.NonExistentQueue"}
                }, "getQueueUrl")
            )
        )
        mock_factory = mock.AsyncMock(return_value=mock_client)
        monkeypatch.setattr(sqs, "aio_create_client", mock_factory)

        target = sqs.SQSBase(queue_name="my_queue", aws_config="my_config")

        with pytest.raises(sqs.QueueNotFound):
            await target.open()

        mock_client.close.assert_called()
        assert target._client is None
        assert target._queue_url is None

    @pytest.mark.asyncio
    async def test_open__client_error(self, monkeypatch):
        """
        Handle if an unknown client error is raised.

        Ensure the client is closed.
        """

        mock_client = mock.AsyncMock(
            get_queue_url=mock.AsyncMock(
                side_effect=botocore.exceptions.ClientError({
                    "Error": {"Code": "AWS.SimpleQueueService.AccessDeniedException"}
                }, "getQueueUrl")
            )
        )
        mock_factory = mock.AsyncMock(return_value=mock_client)
        monkeypatch.setattr(sqs, "aio_create_client", mock_factory)

        target = sqs.SQSBase(queue_name="my_queue", aws_config="my_config")

        with pytest.raises(ClientError):
            await target.open()

        mock_client.close.assert_called()
        assert target._client is None
        assert target._queue_url is None

    @pytest.mark.asyncio
    async def test_open__other_error(self, monkeypatch):
        """
        Ensure any other errors cause the client to be closed.
        """

        mock_client = mock.AsyncMock(
            get_queue_url=mock.AsyncMock(
                side_effect=botocore.exceptions.BotoCoreError()
            )
        )
        mock_factory = mock.AsyncMock(return_value=mock_client)
        monkeypatch.setattr(sqs, "aio_create_client", mock_factory)

        target = sqs.SQSBase(queue_name="my_queue", aws_config="my_config")

        with pytest.raises(ClientError):
            await target.open()

        mock_client.close.assert_called()
        assert target._client is None
        assert target._queue_url is None

    @pytest.mark.asyncio
    async def test_close__not_opened(self):
        """
        Test close called if there is no open client.
        """
        target = sqs.SQSBase(queue_name="my_queue", aws_config="my_config")
        target._queue_url = "eek!"

        await target.close()

        assert target._queue_url is None

    @pytest.mark.asyncio
    async def test_close(self):
        """
        Ensure the client is closed and set to None
        """
        target = sqs.SQSBase(queue_name="my_queue", aws_config="my_config")
        target._client = mock_client = mock.AsyncMock()
        target._queue_url = "eek!"

        await target.close()

        mock_client.close.assert_awaited()
        assert target._client is None
        assert target._queue_url is None

    @pytest.mark.asyncio
    async def test_configure(self, monkeypatch):
        """

        """
        mock_session = mock.AsyncMock(
            create_queue=mock.AsyncMock(
                return_value={"QueueUrl": "http://example.com/my_queue"}
            )
        )
        mock_session.__aenter__.return_value = mock_session
        mock_factory = mock.AsyncMock(return_value=mock_session)
        monkeypatch.setattr(sqs, "aio_create_client", mock_factory)

        target = sqs.SQSBase(queue_name="my_queue", aws_config="my_config")

        actual = await target.configure()

        assert actual == "http://example.com/my_queue"
        mock_session.__aenter__.assert_called()
        mock_session.__aexit__.assert_called()

    @pytest.mark.asyncio
    async def test_configure__client_error(self, monkeypatch):
        mock_session = mock.AsyncMock(
            create_queue=mock.AsyncMock(
                side_effect=ClientError({
                    "Error": {"Code": "AWS.SimpleQueueService.QueueDeletedRecently"}
                }, "getQueueUrl")
            ),
        )
        mock_session.__aenter__.return_value = mock_session
        mock_factory = mock.AsyncMock(return_value=mock_session)
        monkeypatch.setattr(sqs, "aio_create_client", mock_factory)

        target = sqs.SQSBase(queue_name="my_queue", aws_config="my_config")

        with pytest.raises(ClientError):
            await target.configure()

        mock_session.__aenter__.assert_called()
        mock_session.__aexit__.assert_called()


class TestSQSSender:
    @pytest.mark.asyncio
    async def test_send_raw(self):
        target = sqs.SQSSender(queue_name="my_queue", aws_config="my_config")
        target._queue_url = "http://example.com/my_queue"
        target._client = client = mock.AsyncMock(
            send_message=mock.AsyncMock(return_value={"MessageId": "abc"})
        )

        actual = await target.send_raw(
            b"SomeData",
            content_type="application/json",
            content_encoding=None
        )

        assert actual == "abc"
        client.send_message.assert_awaited_with(
            QueueUrl="http://example.com/my_queue",
            MessageBody=b"SomeData",
            MessageAttributes={
                "ContentType": {
                    "DataType": "String",
                    "StringValue": "application/json"
                }
            }
        )


class TestSQSReceiver:
    @pytest.mark.asyncio
    async def test_receive_raw(self):
        target = sqs.SQSReceiver(queue_name="my_queue", aws_config="my_config")
        target._client = client = mock.AsyncMock(
            receive_message=mock.AsyncMock(
                side_effect=[
                    {
                        "Messages": []
                    },
                    {},
                    {
                        "Messages": [
                            {"Body": b"SomeData1"},
                            {
                                "Body": b"SomeData2",
                                "MessageAttributes": {
                                    "ContentType": {
                                        "DataType": "String",
                                        "StringValue": "application/json"
                                    }
                                }
                            },
                        ]
                    }
                ]
            )
        )

        data = []
        async for message in target.receive_raw():
            data.append(message)
            if len(data) == 2:
                break

        actual1, actual2 = data

        assert actual1.body == b"SomeData1"
        assert actual1.queue is target
        assert actual1.content_type is None
        assert actual1.content_encoding is None

        assert actual2.body == b"SomeData2"
        assert actual2.queue is target
        assert actual2.content_type == "application/json"
        assert actual2.content_encoding is None
