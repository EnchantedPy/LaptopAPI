# FastAPI
from fastapi import FastAPI, Security

# External libraries
import uuid
import json

# Internal services and dependencies
from services.admin_service.kafka.producer import admin_kafka_producer
from services.auth_service.service.depends import admin_required
from services.admin_service.service.schemas import SearchUserByIdSchema, SearchUserByNameSchema, SearchUserByEmailSchema
from services.admin_service.service.depends import PaginationDep

# Integrations
from etc.cache import wait_for_response, cache_result

# Configurations
from backend.src.utils.logger import laptop_logger
from config.settings import SAppSettings



admin_service_holder = FastAPI(title='Admin Service')

TOPICS = SAppSettings.kafka_topics


@admin_service_holder.get('/users/all', tags=['Admin Routes'], dependencies=[Security(admin_required)])
@cache_result
async def get_all_users(pagination: PaginationDep):
    try:
        offset = pagination.offset
        limit = pagination.limit
        laptop_logger.info(f"Offset: {offset}, Limit: {limit}")

        request_id = str(uuid.uuid4())
        message = {'request_id': request_id, 'limit': limit, 'offset': offset}
        topic_key = 'admin_get_all_users'

        async with admin_kafka_producer as producer:
            await producer.send_message(topic_key, message)
            laptop_logger.info('Message sent to kafka')

        response_data = await wait_for_response(request_id)
        laptop_logger.info(f"Response from cache in admin: {response_data}")

        if isinstance(response_data, str):
            try:
                res = json.loads(response_data)
            except:
                return {'status': 'success', 'data': response_data}

        elif isinstance(response_data, list):
            res = []
            for user in response_data:
                try:
                    user_dict = json.loads(user)
                    res.append(user_dict)
                except:
                    res.append(user)
            return {'status': 'success', 'data': res}

        else:
            return {'status': 'error', 'message': 'Invalid response format'}

    except Exception as e:
        laptop_logger.error(f"Error when fetching all users: {e}")
        raise  # GetAllUsersException


    


@admin_service_holder.post('/users/search/name', tags=['Admin Routes'], dependencies=[Security(admin_required)])
@cache_result
async def search_users_name(data: SearchUserByNameSchema, pagination: PaginationDep):
    try:
        request_id = str(uuid.uuid4())
        limit = pagination.limit
        offset = pagination.offset
        message = {'request_id': request_id, 'search_query': data.search_query, 'search_type': 'name', 'limit': limit, 'offset': offset}
        topic_key = 'admin_search_users'
        
        async with admin_kafka_producer as producer:
            await producer.send_message(topic_key, message)
            laptop_logger.info('Message sent to kafka')

        response_data = await wait_for_response(request_id)
        laptop_logger.info(f"Response from cache in admin: {response_data}")
        
        if isinstance(response_data, str):
            try:
                res = json.loads(response_data)
            except:
                return {'status': 'success', 'data': response_data}
        
        elif isinstance(response_data, list):
            res = []
            for user in response_data:
                try:
                    user_dict = json.loads(user)
                    res.append(user_dict)
                except:
                    res.append(user)
            return {'status': 'success', 'data': res}
        
        else:
            return {'status': 'error', 'message': 'Invalid response format'}
    
    except Exception as e:
        laptop_logger.error(f"Error when searching users by name: {e}")
        raise  # GetUsersByNameException



@admin_service_holder.post('/users/search/email', tags=['Admin Routes'], dependencies=[Security(admin_required)])
@cache_result
async def search_users_email(data: SearchUserByEmailSchema, pagination: PaginationDep):
    try:
        request_id = str(uuid.uuid4())
        limit = pagination.limit
        offset = pagination.offset

        message = {
            'request_id': request_id,
            'search_query': data.search_query,
            'search_type': 'email',
            'limit': limit,
            'offset': offset
        }

        topic = 'admin_search_users'

        async with admin_kafka_producer as producer:
            await producer.send_message(topic, message)
            laptop_logger.info('Message sent to kafka')

        response_data = await wait_for_response(request_id)
        laptop_logger.info(f"Response from cache in admin: {response_data}")
        laptop_logger.info(f"Type of response_data: {type(response_data)}")

        if response_data is None:
            laptop_logger.error("Response data is None!")
            return {'status': 'error', 'message': 'No response from service'}

        if isinstance(response_data, str):
            try:
                res = json.loads(response_data)
            except Exception as e:
                laptop_logger.error(f"Error parsing response data: {e}")
                return {'status': 'success', 'data': response_data}

        elif isinstance(response_data, list):
            res = []
            for user in response_data:
                try:
                    user_dict = json.loads(user)
                    res.append(user_dict)
                except:
                    res.append(user)
            return {'status': 'success', 'data': res}

        else:
            return {'status': 'error', 'message': 'Invalid response format'}

    except Exception as e:
        laptop_logger.error(f"Error when searching users by email: {e}")
        raise  # GetUsersByEmailException

    

@admin_service_holder.post('/users/search/id', tags=['Admin Routes'], dependencies=[Security(admin_required)])
@cache_result
async def search_users_id(data: SearchUserByIdSchema, pagination: PaginationDep):
    try:
        request_id = str(uuid.uuid4())
        limit = pagination.limit
        offset = pagination.offset

        message = {
            'request_id': request_id,
            'search_query': data.search_query,
            'search_type': 'id',
            'limit': limit,
            'offset': offset
        }

        topic = 'admin_search_users'

        async with admin_kafka_producer as producer:
            await producer.send_message(topic, message)

        response_data = await wait_for_response(request_id)
        laptop_logger.info(f"Response from cache in admin: {response_data}")
        laptop_logger.info(f"Type of response_data: {type(response_data)}")

        if response_data is None:
            laptop_logger.error("Response data is None!")
            return {'status': 'error', 'message': 'No response from service'}

        if isinstance(response_data, str):
            try:
                res = json.loads(response_data)
                return {'status': 'success', 'data': res}
            except Exception:
                return {'status': 'success', 'data': response_data}

        elif isinstance(response_data, list):
            res = []
            for user in response_data:
                try:
                    user_dict = json.loads(user)
                    res.append(user_dict)
                except Exception:
                    res.append(user)
            return {'status': 'success', 'data': res}

        else:
            return {'status': 'error', 'message': 'Invalid response format'}

    except Exception as e:
        laptop_logger.error(f"Error when searching users by id: {e}")
        raise  # GetUsersByIdException