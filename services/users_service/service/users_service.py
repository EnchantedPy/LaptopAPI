from functools import wraps
from fastapi import FastAPI, Request, Response, Security, HTTPException
from pydantic import EmailStr
from services.auth_service.service.depends import auth_required
from services.users_service.kafka.producer import users_kafka_producer
from backend.src.utils.logger import laptop_logger
from etc.cache import wait_for_response
import json
from services.users_service.service.schemas import (
PasswordUpdateSchema,
EmailUpdateSchema,
UserNameUpdateSchema
)
import uuid

users_service_holder = FastAPI(title='Users Service')

async def get_user_id(request: Request):

    request_id = str(uuid.uuid4())
    topic_key = 'get_user_id'
    
    cookies = dict(request.cookies)
    message = {'http_request_cookies': cookies, 'request_id': request_id}

    try:
        async with users_kafka_producer as producer:
            await producer.send_message(topic_key, message)
            laptop_logger.debug(f"User id get request sent to Kafka with request_id: {request_id}")

        response_data = await wait_for_response(request_id)
        laptop_logger.info(f"Response from cache in auth: {response_data}")

        if isinstance(response_data, str):
            try:
                res = json.loads(response_data)
                laptop_logger.info(f"Parsed JSON: {res}")
            except json.JSONDecodeError as e:
                laptop_logger.error(f"Failed to parse JSON: {e}")
                raise HTTPException(status_code=500, detail="Internal parsing error")
        else:
            res = response_data
            laptop_logger.info(f"Using response as is: {res}")

        user_id = res
      
        if not user_id:
            laptop_logger.warning(f"No user_id found in response: {res}")
            raise HTTPException(status_code=422, detail="Invalid user_id in response")
        
        return user_id

    except Exception as e:
        laptop_logger.exception(f"Error fetching user_id: {e}")
        raise HTTPException(status_code=500, detail="Error fetching user_id")
    


@users_service_holder.get('/get_profile', tags=['User Account Management'], dependencies=[Security(auth_required)])
async def get_profile(request: Request) -> dict:
    
    user_id = await get_user_id(request)
	 
    request_id = str(uuid.uuid4())
    topic_key = 'user_get_profile'
    message = {'user_id': user_id, 'request_id': request_id}

    try:
        async with users_kafka_producer as producer:
            await producer.send_message(topic_key, message)
            laptop_logger.info(f"Profile get request sent to Kafka with request_id: {request_id}")

        response_data = await wait_for_response(request_id)
        laptop_logger.info(f"Response from cache in auth: {response_data}")

        if isinstance(response_data, str):
            try:
                res = json.loads(response_data)
                laptop_logger.info(f"Parsed JSON: {res}")
            except json.JSONDecodeError as e:
                laptop_logger.error(f"Failed to parse JSON: {e}")
                raise HTTPException(status_code=500, detail="Internal parsing error")
        else:
            res = response_data
            laptop_logger.info(f"Using response as is: {res}")

        if res:
            return res
        else:
            laptop_logger.error(f"Some issue with user data: {res}, {request_id}")
            raise HTTPException(status_code=422, detail="User data issue")

    except Exception as e:
        laptop_logger.exception(f"Error fetching user profile: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    


@users_service_holder.delete('/delete_account', tags=['User Account Management'], dependencies=[Security(auth_required)])
async def delete_account(request: Request, response: Response) -> dict:
    
    user_id = await get_user_id(request)
    
    request_id = str(uuid.uuid4())
    
    topic_key = 'delete_user_account'
    
    message = {'request_id': request_id, 'user_id': user_id}
    try:
        async with users_kafka_producer as producer:
            await producer.send_message(topic_key, message)
            laptop_logger.info(f'Sent message with id {request_id} for user {user_id} account deletion')
            
        response_data = await wait_for_response(request_id)
        laptop_logger.info(f"Response from cache in users: {response_data}")
        laptop_logger.info(f"Type of response_data: {type(response_data)}")

        if not isinstance(response_data, str):
            raise HTTPException(status_code=502, detail='Recieved invalid response to delete-account request')
        
        res = response_data
            
        if res == 'valid':
             laptop_logger.info('Successful account deletion')
             try:
                  response.delete_cookie(
                      key='my_token',
                      path='/',
                      secure=False,
                      httponly=True
                             )
                  laptop_logger.info('Someone successfully logged out after deleting account')
                  return {'status': 'success'}
             
             except Exception as e:
                  laptop_logger.error(f'Unexpected error during logout after deleting account: {e}')
                  raise HTTPException(status_code=500, detail='An error with token while logging out coz of account deletion')
             
        else:
            laptop_logger.error('Some error with response from cache')
            raise HTTPException(status_code=502, detail='Invalid response for delete-account request')
            
        
    except Exception as e:
        laptop_logger.error(f'Error when trying to delete user account: {e}')
        raise HTTPException(status_code=500, detail='Cannot delete user account dur to an error')
    

@users_service_holder.put('/update_username', tags=['User Account Management'], dependencies=[Security(auth_required)])
async def update_username(data: UserNameUpdateSchema, request: Request):
    user_id = await get_user_id(request)
    request_id = str(uuid.uuid4())
    new_name = data.new_name
    topic_key = 'update_username'
    message = {'request_id': request_id, 'user_id': user_id, 'new_name': new_name}
    try:
        async with users_kafka_producer as producer:
             await producer.send_message(topic_key, message)
             laptop_logger.info('Sent username-update request')
             
        response_data = await wait_for_response(request_id)
        laptop_logger.info(f"Response from cache in users: {response_data}")

        if not isinstance(response_data, str):
            raise HTTPException(status_code=502, detail='Recieved invalid response to update-username request')
        
        res = response_data
        
        if res == 'valid':
            laptop_logger.info('Successful username update')
            return {'status': 'success'}
        
    except Exception as e:
        laptop_logger.error(f'Error when trying to update user (users service): {e}')
        raise HTTPException(status_code=500, detail='Error when trying to update username f')
        
    

@users_service_holder.put('/change_password', tags=['User Account Management'], dependencies=[Security(auth_required)])
async def change_sensitive_info(
    data: PasswordUpdateSchema,
    request: Request):
    
    user_id = await get_user_id(request)
        
    request_id = str(uuid.uuid4())
    
    message = {'request_id': request_id, 'user_id': user_id, 'current_password': data.current_password}
    
    topic_key = 'check_user_password'
    
    async with users_kafka_producer as producer:
        await producer.send_message(topic_key, message)
        
    response_data = await wait_for_response(request_id)
    laptop_logger.info(f"Response from cache in users ch-password: {response_data}")
    

    if not isinstance(response_data, str):
            raise HTTPException(status_code=502, detail='Recieved invalid response to update-username request')
    

    res = response_data
    
    if res == 'valid':
            
            laptop_logger.info('Successful password check')
            request_id = str(uuid.uuid4())
            
            topic_key = 'update_user_password'
            
            message = {'request_id': request_id, 'user_id': user_id, 'new_password': data.new_password}
            
            laptop_logger.debug('Configured message for password change')
                 
            async with users_kafka_producer as producer:
                 await producer.send_message(topic_key, message)
                 laptop_logger.info('Sent message for changing password')
                 
            response_data = await wait_for_response(request_id)
            laptop_logger.info(f"Response from cache in users change-password: {response_data}")
            laptop_logger.info(f"Type of response_data: {type(response_data)}")
            
            if not isinstance(response_data, str):
                 raise HTTPException(status_code=502, detail='Recieved invalid response to update-username request')
            
            res_1 = response_data
            
            if res_1 == 'valid':
                laptop_logger.info('Successfull password change')
                return {'status': 'success'}
            



@users_service_holder.put('/change_email', tags=['User Account Management'])
async def change_sensitive_info(
    data: EmailUpdateSchema,
    request: Request):
    
    user_id = await get_user_id(request)
    
    
    request_id = str(uuid.uuid4())
    
    message = {'request_id': request_id, 'user_id': user_id, 'current_password': data.current_password}
    
    topic_key = 'check_user_password'
    
    async with users_kafka_producer as producer:
        await producer.send_message(topic_key, message)
        
    response_data = await wait_for_response(request_id)
    laptop_logger.info(f"Response from cache in users ch-password: {response_data}")
    

    if not isinstance(response_data, str):
            raise HTTPException(status_code=502, detail='Recieved invalid response to update-username request')
    

    res = response_data
    
    if res == 'valid':
            
            laptop_logger.info('Successful password check')
            request_id = str(uuid.uuid4())
            
            topic_key = 'update_user_email'
            
            if data.new_email:
                 message = {'request_id': request_id, 'user_id': user_id, 'new_email': data.new_email}
                 laptop_logger.info('Configured message for email change')
                 
            async with users_kafka_producer as producer:
                 await producer.send_message(topic_key, message)
                 laptop_logger.info('Sent message for changing email')
                 
            response_data = await wait_for_response(request_id)
            laptop_logger.info(f"Response from cache in users change-email: {response_data}")
            
            if not isinstance(response_data, str):
                 raise HTTPException(status_code=502, detail='Recieved invalid response to update-username request')
            
            res_1 = response_data
            
            if res_1 == 'valid':
                laptop_logger.info('Successfull sensitive data change')
                return {'status': 'success'}