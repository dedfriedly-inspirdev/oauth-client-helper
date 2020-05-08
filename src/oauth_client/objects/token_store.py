#!/usr/bin/env python
from oauth_client.config import settings
from redis import StrictRedis, ConnectionError
import json
import logging
from datetime import datetime
from filelock import Timeout, FileLock


class OAuthTokenStore:
    """
    Generic method to save and retrieve values from file and redis backed token storage
    """
    def __init__(self, ):
        self._redis = StrictRedis.from_url(settings.MESSAGE_QUEUE.URL, charset="utf-8", decode_responses=True)
        self._token_file = settings.OAUTH.TOKEN_CACHE
        self._token_prepend = settings.OAUTH.TOKEN_KEY_PREPEND
        self._access_code_prepend = f'{self._token_prepend}_accesscode'
        self._token_refresh_prepend = f'{self._token_prepend}_refreshtoken'
        self._token_access_prepend = f'{self._token_prepend}_accesstoken'
        self._last = None  # this is a bail out help if you happen to read auth code before you were ready to use it

        try:
            self._redis.ping()
        except ConnectionError as e:
            self._error = e
            logging.warning(f'Redis connection error, please resolve, this module requires redis:  {e.args}')

    def _get_token_cache_data(self, client_id):
        if self._get_client_id(client_id=client_id) is None:
            return None
        else:
            return self._get_client_id(client_id=client_id).popitem()

    def _modify_token_cache_data(self, client_id, data:dict):
        data.update({'client_id': client_id,
                     'last_mod_time': int(datetime.utcnow().timestamp())
                     }) # forcing these two fields

        lock = FileLock(f'{self._token_file}.lock')

        with open(self._token_file, 'r') as f:
            existing_data = json.load(f)

        try:
            lock.acquire(timeout=2)

            if self._get_client_id(client_id=client_id) is None:
                # looks to be a net new client id, appending it
                with open(self._token_file, 'w+') as f:
                    num_keys = len(existing_data.keys())
                    existing_data[num_keys + 1] = data
                    f.seek(0)
                    json.dump(existing_data, f)
            else:
                cache_id, client_dict = self._get_client_id(client_id=client_id).popitem()
                existing_data[cache_id].update(**data)

                with open(self._token_file, 'w+') as f:
                    f.seek(0)
                    json.dump(existing_data, f)

                existing_data[cache_id].update(**data)
        except TimeoutError as e:
            raise(e)
        finally:
            lock.release()

    def add_oauth_client(self, client_id:str, auth_url:str, qs_params:dict, service_name:str=None, redirect_url=settings.OAUTH.REDIRECT_URL):
        """
        This is setting up the client_id for an oauth call.  I want this to be extensible so I'm adding
        the ability to provide a service_name for segmenting.

        Note, no data pushed to redis here, this is all local file cache stuff
        """
        assert self._token_file is not None, "No local token file storage set, this is required"

        data = {
            'client_id': client_id,
            'auth_url': auth_url,
            'redirect_url': redirect_url,
            'service_name': service_name,
            'qs_params': qs_params,
            'add_time': int(datetime.utcnow().timestamp()),
            'auth_code_set': False,
            'refresh_token_ttl': None,
            'acess_token_ttl': None,
        }

        self._modify_token_cache_data(client_id, data)

        return self._get_client_id(client_id)

    def is_auth_code_set(self, client_id):
        if self._get_client_id(client_id) is not None:
            cache_id, client_dict = self._get_client_id(client_id).popitem()

            try:
                return client_dict['auth_code_set']
            except:
                return "DATA FORMAT ISSUE - no auth_code_set in token cache"
        else:
            return None

    def client_token_info(self, client_id):
        if self._get_client_id(client_id) is not None:
            cache_id, client_dict = self._get_client_id(client_id).popitem()

            try:
                client_dict.update({'refresh_token_ttl': self._redis.ttl(f'{self._token_refresh_prepend}:_{client_id}'),
                                    'acess_token_ttl': self._redis.ttl(f'{self._token_access_prepend}:_{client_id}')})
            except ConnectionError as e:
                client_dict.update({'refresh_token_ttl': 'NO MESSAGE BROKER CONN',
                                    'acess_token_ttl': 'NO MESSAGE BROKER CONN'})

            return client_dict

        else:
            return None
    
    def get_qs_params(self, client_id):
        if self._get_client_id(client_id=client_id) is not None:
            cache_id, client_data = self._get_token_cache_data(client_id)

            try:
                return client_data['qs_params']
            except:
                return None

    def get_access_code(self, client_id):
        if self._get_client_id(client_id=client_id) is not None:
            self._last = self._redis.get(f'{self._access_code_prepend}:_{client_id}')
            self._redis.delete(f'{self._access_code_prepend}:_{client_id}')
            
            self._modify_token_cache_data(client_id, {'auth_code_set': False})
            return self._last
        else:
            logging.info(f"No client id found that matches requested:  {client_id}")
            return None

    def set_access_code(self, client_id, access_code):
        if self._get_client_id(client_id=client_id) is not None:
            self._redis.set(f'{self._access_code_prepend}:_{client_id}', access_code, ex=None)
            
            self._modify_token_cache_data(client_id, {'auth_code_set': True})
            return True
        else:
            logging.info(f"No client id found that matches requested:  {client_id}")
            return False

    def get_refresh_token(self, client_id):
        if self._get_client_id(client_id=client_id) is not None:
            return self._redis.get(f'{self._token_refresh_prepend}:_{client_id}')
        else:
            logging.info(f"No client id found that matches requested:  {client_id}")
            return None

    def set_refresh_token(self, client_id, token, ttl:int):
        if self._get_client_id(client_id=client_id) is not None:
            self._redis.set(f'{self._token_refresh_prepend}:_{client_id}', token, ex=ttl)
            return 1
        else:
            logging.info(f"No client id found that matches requested:  {client_id}")
            return None

    def get_access_token(self, client_id):
        if self._get_client_id(client_id=client_id) is not None:
            return self._redis.get(f'{self._token_access_prepend}:_{client_id}')
        else:
            logging.info(f"No client id found that matches requested:  {client_id}")
            return None

    def set_access_token(self, client_id, token, ttl:int):
        if self._get_client_id(client_id=client_id) is not None:
            self._redis.set(f'{self._token_access_prepend}:_{client_id}', token, ttl)
            return 1
        else:
            logging.info(f"No client id found that matches requested:  {client_id}")
            return None

    def redis_key_name(self, key_type:str, client_id:str):
        if key_type == "access_code":
            return f'{self._access_code_prepend}:_{client_id}'
        elif key_type == "token_refresh":
            return f'{self._token_refresh_prepend}:_{client_id}'
        elif key_type == "token_access":
            return f'{self._token_access_prepend}:_{client_id}'
        else:
            raise ValueError(f'Unknown key_type "{key_type}", expected ["access_code", "token_refresh", "token_access"]')

    @property
    def _list_clients(self, ):
        try:
            with open(self._token_file, 'r') as f:
                data = json.load(f)

        except FileNotFoundError as e:
            data = {}

        finally:
            return data

    @classmethod
    def list_service_names(klass, ):
        my_obj = klass()

        client_info = my_obj._list_clients

        service_name_list = [ ]

        for k, v in client_info.items():
            if v['service_name'] not in service_name_list:
                service_name_list.append(v['service_name'])

        return service_name_list

    def _get_client_id(self, client_id, ):
        try:
            with open(self._token_file, 'r') as f:
                data = json.load(f)

            return_data = None
            for key, val in data.items():
                if val['client_id'] == client_id:
                    return_data = {key: val}
                    break

        except FileNotFoundError as e:
            import os
            with open(self._token_file, 'a+') as f:
                json.dump({}, f)
            os.chmod(self._token_file, 0o600)

            return_data = None

        finally:
            return return_data

    def _clear_file_cache(self, ):
        try:
            import os
            with open(self._token_file, 'w+') as f:
                json.dump({}, f)
            os.chmod(self._token_file, 0o600)
        finally:
            return None
