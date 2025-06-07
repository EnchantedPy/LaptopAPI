
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from elasticsearch import AsyncElasticsearch

from config.settings import Settings


# es = AsyncElasticsearch(hosts=[Settings.elastic_url], basic_auth=(Settings.elastic_user, Settings.elastic_password), verify_certs=False, headers={
#             "Accept": "application/vnd.elasticsearch+json; compatible-with=8",
#             "Content-Type": "application/vnd.elasticsearch+json; compatible-with=8"
#         })


class ElasticClient:
    def __init__(self):
        self.client = AsyncElasticsearch(
            hosts=[Settings.elastic_url],
            basic_auth=(Settings.elastic_user, Settings.elastic_password),
            verify_certs=False,
				headers={
                    "Accept": "application/vnd.elasticsearch+json; compatible-with=8",
						  "Content-Type": "application/vnd.elasticsearch+json; compatible-with=8"
            })

    async def __call__(self) -> AsyncElasticsearch:
        return self.client
	
elastic_client = ElasticClient()