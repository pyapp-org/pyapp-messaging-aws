import logging

from botocore.exceptions import ClientError

LOGGER = logging.getLogger(__name__)


def botocore_errors(func):
    """
    Wrapper for methods that can generate botocore exceptions
    """
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ClientError as ex:
            error_code = ex.response["Error"]["Code"]
            LOGGER.error("Client error: %s", error_code)
            raise

    return wrapper
