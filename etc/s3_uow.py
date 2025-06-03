class S3UoW:
    def __init__(self):
        self._client_factory = s3_client_maker

    async def __aenter__(self):
        try:
            self._client_context = await self._client_factory()
            self._client = await self._client_context.__aenter__()
            self.s3 = S3Repository(self._client)
            return self
        except NoCredentialsError as e:
            logger.error(f"No credentials error in S3UoW during __aenter__: {e}")
            raise S3NoCredentialsException

        except EndpointConnectionError as e:
            logger.error(f"Endpoint connection error in S3UoW during __aenter__: {e}")
            raise S3ConnectionException

        except BotoCoreError as e:
            logger.error(f"Botocore error during S3UoW __aenter__: {e}")
            raise S3Exception

        except Exception as e:
            logger.critical(f"Critical unexpected error in S3UoW during __aenter__: {e}", exc_info=True)
            raise S3Exception

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        try:
            if self._client_context:
                await self._client_context.__aexit__(exc_type, exc_value, exc_tb)

        except ClientError as e:
            logger.error(f"Client error in S3UoW: {e}")
            raise S3ClientException

        except NoCredentialsError as e:
            logger.error(f"No credentials error in S3UoW: {e}")
            raise S3NoCredentialsException

        except EndpointConnectionError as e:
            logger.error(f"Endpoint connection error in S3UoW: {e}")
            raise S3ConnectionException

        except ParamValidationError as e:
            logger.error(f"Param validation error in S3UoW: {e}")
            raise S3ParameterValidationException

        except BotoCoreError as e:
            logger.error(f"Unexpected S3 error occurred: {e}")
            raise S3Exception

        except Exception as e:
            logger.critical(f"Critical unexpected error in S3UoW: {e}")
            raise S3Exception