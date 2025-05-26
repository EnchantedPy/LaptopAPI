# Standard Library Imports
import json

# Third-Party Imports
from fastapi import HTTPException
from aiokafka import AIOKafkaConsumer
from passlib.context import CryptContext

# Local Imports
from services.db_service.service.database_service import (
    add_user,
    get_user_by_id,
    delete_user,
    update_user_sensitive_data,
    update_username,
    get_all_users,
    check_data_coincidence,
    verify_user_credentials
)
from etc.cache import send_message_to_redis
from backend.src.utils.logger import laptop_logger
from services.db_service.service.schemas import UserAddSchema
from services.db_service.kafka.producer import db_kafka_producer
from config.settings import SAppSettings


LOCAL_TOPICS = {
	 'user-registration-topic': 'user-registration-topic',
	 'user-logging-in-topic': 'user-logging-in-topic',
	 'user-get-profile-topic': 'user-get-profile-topic',
	 'delete-user-account-topic': 'delete-user-account-topic',
	 'update-username-topic': 'update-username-topic',
	 'check-user-password-topic': 'check-user-password-topic',
	 'update-user-password-topic': 'update-user-password-topic',
	 'update-user-email-topic': 'update-user-email-topic',
	 'admin-get-all-users-topic': 'admin-get-all-users-topic',
	 'admin-search-users-topic': 'admin-search-users-topic'
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)




class KafkaConsumerClient:
    def __init__(self, topics: dict, broker_url: str = SAppSettings.kafka_broker_url):
        self.broker_url = broker_url
        self.topics = topics
        self.consumer = None

    async def start(self, topics: list):

        self.consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=self.broker_url,
            value_deserializer=self.deserializer
        )
        await self.consumer.start()

    async def stop(self):
        if self.consumer:
            await self.consumer.stop()

    def deserializer(self, serialized):
         if isinstance(serialized, dict):
               laptop_logger.info(f"Received msg as dict: {serialized}")
               return serialized
         elif isinstance(serialized, str):
               laptop_logger.info(f"Received msg as string: {serialized}")
               return json.loads(serialized)
         elif isinstance(serialized, bytes):
               decoded = serialized.decode('utf-8')
               laptop_logger.info(f"Received msg as bytes: {decoded}")
               return json.loads(decoded)
         else:
               laptop_logger.error(f"Unknown message type: {type(serialized)}")
               return None


    async def event_handler(self, value, topic: str):
        if topic == 'user-registration-topic':
            laptop_logger.info(f"Handling user registration: {value}")
            value = self.deserializer(value)
            await self.handle_user_registration(value)
        elif topic == 'user-logging-in-topic':
            laptop_logger.info(f"User login attempt: {value}")
            value = self.deserializer(value)
            await self.handle_user_login(value)
        elif topic == 'user-get-profile-topic':
            laptop_logger.info(f'Handling user profile request: {value}')
            value = self.deserializer(value)
            await self.handle_user_profile_request(value)
        elif topic == 'delete-user-account-topic':
            laptop_logger.info(f'User account deletion attempt: {value}')
            value = self.deserializer(value)
            await self.handle_account_deletion(value)
        elif topic == 'update-username-topic':
            laptop_logger.info(f'An attempt to change username, info: {value}')
            value = self.deserializer(value)
            await self.handle_update_username(value)
        elif topic == 'check-user-password-topic':
            laptop_logger.info(f'Handling check-password request: {value}')
            value = self.deserializer(value)
            await self.handle_check_password(value)
        elif topic == 'update-user-password-topic':
            laptop_logger.info('Handling change-password request')
            value = self.deserializer(value)
            await self.handle_change_password(value)
        elif topic == 'update-user-email-topic':
            laptop_logger.info('Handling change-email request')
            value = self.deserializer(value)
            await self.handle_change_email(value)
        elif topic == 'admin-get-all-users-topic':
            laptop_logger.info(f"Admin attempt to get all users: {value}")
            value = self.deserializer(value)
            await self.handle_admin_all_users_request(value)
        elif topic == 'admin-search-users-topic':
             laptop_logger.info(f"Admin search users: {value}")
             value = self.deserializer(value)
             await self.handle_admin_search_users(value)
        else:
            laptop_logger.warning(f"Received messager from unknown topic: {topic}")
            
    async def handle_admin_search_users(self, value):
         try:
              request_id = value.get('request_id')
              search_type = value.get('search_type')
              
              match search_type:
                   case 'name':
                        lc_param = 'name'
                   case 'email':
                        lc_param = 'email'
                   case 'id':
                        lc_param = 'id'
                        
              search_query = value.get('search_query')
              limit = value.get('limit')
              offset = value.get('offset')
              
              laptop_logger.debug(f'Handling admin search-users in method: {request_id} {search_query} {search_type} {limit} {offset}')
              
              users = await get_all_users(limit, offset)
              
              users_data = [
                   {
                		'id': user.id,
                		'name': user.name,
                		'email': user.email,
                          }
                  	for user in users
                              ]
              
              if not users_data:
                   response_data = {
                		'request_id': request_id,
                		'data': 'valid',
                		'users': 'No users found',
            				}
                   
                   await send_message_to_redis(db_kafka_producer, response_data, 'Database producer')
                   
              filtered_users = [user for user in users_data if user.get(lc_param) == search_query]
              if filtered_users:
                        response_data = {
                    			'request_id': request_id,
                    			'data': 'valid',
                    			'users': filtered_users,
                  		}
                        
              else:
                        response_data = {
                    			'request_id': request_id,
                    			'data': 'valid',
                    			'users': 'No users matching the search query',
                			}
                        
              await send_message_to_redis(db_kafka_producer, response_data, 'Database producer')
                             
         except Exception as e:
              laptop_logger.error(f'Error when fetching all users to filter, limit: {limit}, offset: {offset}: {e}')
              raise HTTPException(status_code=500, detail='Error when fetching all users for filtering')

             
            
    async def handle_admin_all_users_request(self, value):
        request_id = value.get('request_id')
        limit = value.get('limit')
        offset = value.get('offset')
        laptop_logger.debug(f'Handling admin get-all-users in method: {request_id} {limit} {offset}')
        try:
            users_data = await get_all_users(limit, offset)
            if users_data:
                 laptop_logger.info('Found users in DB')
                 response_data = {
									 'request_id': request_id,
									 'data': 'valid',
									 'users': users_data
								}
            else:
                 laptop_logger.info('No users found')
                 response_data = {
									 'request_id': request_id,
									 'data': 'valid',
                            'users': 'No users found'
								}
            await send_message_to_redis(db_kafka_producer, response_data, 'Database producer')
                
        except Exception as e:
            laptop_logger.error(f'Error when fetching all user: {e}')
            raise HTTPException(status_code=500, detail='Database error when fetching all users')
            
    async def handle_change_password(self, value):
        request_id = value.get('request_id')
        user_id = value.get('user_id')
        new_password = value.get('new_password')
        
        laptop_logger.debug(f'Handling change-password in method: {request_id} {user_id}')
        try:
                 if await check_data_coincidence(user_id, new_password, 'password'):
                      raise HTTPException(status_code=409, detail="Provided password is the same as current")
                 
                 result = await update_user_sensitive_data(new_password=new_password, user_id=user_id)
                      
                 if result.get('status') == 'success':
                    response_data = {
                        'request_id': request_id,
                        'data': 'valid',
                        'special': 'success'
                    }
                 else:
                    response_data = {
                        'request_id': request_id,
                        'data': 'invalid'
                    }
                    
                 await send_message_to_redis(db_kafka_producer, response_data, 'Database producer')
                           
        except Exception as e:
             laptop_logger.error(f'Error when trying to change user password: {e}')
             raise HTTPException(status_code=500, detail='Error when updating user password')
        
    async def handle_change_email(self, value):
        request_id = value.get('request_id')
        user_id = value.get('user_id')
        new_email = value.get('new_email')
        
        laptop_logger.debug(f'Handling change-email in method: {request_id} {user_id}')
        
        try:
                 if await check_data_coincidence(user_id, new_email, 'email'):
                      raise HTTPException(status_code=409, detail="Provided email is the same as current")
                 
                 res = await update_user_sensitive_data(new_email=new_email, user_id=user_id)
                      
                 if res.get('status') == 'success':
                    response_data = {
                        'request_id': request_id,
                        'data': 'valid',
                        'special': 'success'
                    }
                 else:
                    response_data = {
                        'request_id': request_id,
                        'data': 'invalid'
                    }
                    
                 await send_message_to_redis(db_kafka_producer, response_data, 'Database producer')
                        
        except Exception as e:
            laptop_logger.error(f'Error when trying to change user email: {e}')
            raise HTTPException(status_code=500, detail='Error when updating user email')
    
            
    async def handle_check_password(self, value):
            request_id = value.get('request_id')
            user_id = value.get('user_id')
            current_password = value.get('current_password')
            
            laptop_logger.debug(f'Handling check-password request in method: {request_id} {user_id} {current_password}')
            
            try:
                    is_password_valid = await check_data_coincidence(user_id, current_password, 'password')
                    if is_password_valid:
                         response_data = {
                                  'request_id': request_id,
                                  'data': 'valid',
                                  'special': 'success'
                                     }
                    else:
                              response_data = {
                                  'request_id': request_id,
                                  'data': 'invalid'
                                     }
                              
                    await send_message_to_redis(db_kafka_producer, response_data, 'Database producer')
                    
            except Exception as e:
                 laptop_logger.error(f'Error when trying to check password: {e}')
                 raise HTTPException(status_code=500, detail='Error when checking password')
               
                        
    async def handle_update_username(self, value):
            request_id = value.get('request_id')
            user_id = value.get('user_id')
            new_name = value.get('new_name')
            laptop_logger.debug(f'Handling update-username in method: {request_id} {user_id}')
            try:
                    result = await update_username(user_id, new_name)
                    if result.get('status') == 'success':
                            response_data = {
                            'request_id': request_id,
                            'data': 'valid',
                            'special': 'success'
                                     }
                    else:
                             response_data = {
                            'request_id': request_id,
                            'data': 'invalid'
                                     }
                             
                    await send_message_to_redis(db_kafka_producer, response_data, 'Database producer')
                    
            except Exception as e:
                 laptop_logger.error(f'Error when trying to change username: {e}')
                 raise HTTPException(status_code=500, detail='Error when changing username')
                    
                    
            
    async def handle_account_deletion(self, value):
        
        request_id = value.get('request_id')
        user_id = value.get('user_id')
        
        laptop_logger.info(f'Handling account deletion in method: {request_id} {user_id}')
        
        try:
                result = await delete_user(user_id)
                if result.get('status') == 'success':
                        response_data = {
                            'request_id': request_id,
                            'data': 'valid',
                            'special': 'success'
								}
                        
                else:
                        response_data = {
                            'request_id': request_id,
                            'data': 'invalid'
								}
                        
                await send_message_to_redis(db_kafka_producer, response_data, 'Database producer')
                        
                        
        except Exception as e:
            laptop_logger.error(f'Error when trying to delete user account {e}')
            raise HTTPException(status_code=500, detail='Error when deleting user account')
                    
                

    async def handle_user_profile_request(self, value):
        laptop_logger.info(value)

        request_id = value.get('request_id')
        user_id = value.get('user_id')

        laptop_logger.info(f'Handling user profile request in method: {request_id}, {user_id}')
        try:
             user_data = await get_user_by_id(user_id)
             if user_data:
                        laptop_logger.debug('Found corresponding user')
                        response_data = {
                            'request_id': request_id,
                            'user': {
                                'id': user_id,
                                'name': user_data.get('name'),
                                'email': user_data.get('email'),
                                'password': hash_password(user_data.get('password')),
                            },
                            'data': 'valid'
                        }
             else:
                        response_data = {
                            'request_id': request_id,
                            'data': 'invalid'
                        }

             await send_message_to_redis(db_kafka_producer, response_data, 'Database producer')
             
        except Exception as e:
                laptop_logger.info(f'Error when trying to fetch user info: {e}')
                raise HTTPException(status_code=500, detail='Error when fetching user info')

    async def handle_user_registration(self, value):
        laptop_logger.info(value)
        schema = value.get('data')

        name = schema.get('name')
        password = schema.get('password')
        email = schema.get('email')
        request_id = value.get('request_id')

        laptop_logger.debug(name, password, email)

        user_data = UserAddSchema(name=name, password=password, email=email)

        laptop_logger.info('Handling user registration')
        try:
             res = await add_user(user_data)
             if res.get('status') == 'success':
                 response_data = {
						  'request_id': request_id,
						  'data': 'valid',
                    'special': 'success'
					 }
                 
             else:
                 response_data = {
						  'request_id': request_id,
						  'data': 'invalid'
					  }
                 
             await send_message_to_redis(db_kafka_producer, response_data, 'Database producer')
             
        except Exception as e:
             laptop_logger.error(f'Error when trying to add user: {e}')
             raise HTTPException(status_code=500, detail='Error when adding user')


    async def handle_user_login(self, value):
        laptop_logger.info(f"Received login message: {value}")
        request_id = value.get('request_id')
        login_data = value.get('data')

        username = login_data.get('username')
        password = login_data.get('password')
        laptop_logger.debug(f'Handling user-login in method {username} {password} {request_id}')
        try:
              result = await verify_user_credentials(username, password)
              if result:
                        laptop_logger.info('Found corresponding data for login')
                        response_data = {
                            'request_id': request_id,
                            'data': 'valid',
                            'user': {
                                'id': result.get('id'),
                                'name': result.get('name'),
                            }
                        }
              else:
                        response_data = {
                            'request_id': request_id,
                            'data': 'invalid'
                        }
              await send_message_to_redis(db_kafka_producer, response_data, 'Database producer')
              
        except Exception as e:
                laptop_logger.error(f"Error when trying to log in user: {e}")
                raise HTTPException(status_code=404, detail=f"Error when logging in user")

    async def consume_messages(self):
        laptop_logger.info('DB consumer is consuming msgs')
        await self.start(list(self.topics.values()))

        try:
            async for msg in self.consumer:
                topic_key = msg.topic
                await self.event_handler(msg.value, topic_key)
        finally:
            await self.stop()


db_kafka_consumer = KafkaConsumerClient(LOCAL_TOPICS)

async def run_db_consumer():
    laptop_logger.info('Database consumer started')
    await db_kafka_consumer.consume_messages()
    laptop_logger.info('Stopping DB kafka consumer')