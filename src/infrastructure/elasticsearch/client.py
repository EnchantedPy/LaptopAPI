
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from elasticsearch import AsyncElasticsearch

from config.settings import Settings


es = AsyncElasticsearch(hosts=[Settings.elastic_url], basic_auth=(Settings.elastic_user, Settings.elastic_password), verify_certs=False, headers={
            "Accept": "application/vnd.elasticsearch+json; compatible-with=8",
            "Content-Type": "application/vnd.elasticsearch+json; compatible-with=8"
        })

class EsClientFactory:
	def __init__(self, hosts=[Settings.elastic_url], basic_auth=(Settings.elastic_user, Settings.elastic_password), verify_certs=False, headers={
            "Accept": "application/vnd.elasticsearch+json; compatible-with=8",
            "Content-Type": "application/vnd.elasticsearch+json; compatible-with=8"
        }):
		self.client = AsyncElasticsearch(hosts, basic_auth, verify_certs, headers)

	@asynccontextmanager
	async def get_es_client(self) -> AsyncGenerator[AsyncElasticsearch, None]:
		yield es

	async def __call__(self) -> AsyncElasticsearch:
		return self.__call__()
	
es_clientfactory = EsClientFactory()