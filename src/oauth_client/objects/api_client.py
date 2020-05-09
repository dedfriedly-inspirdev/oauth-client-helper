#!/usr/bin/env python
from oauth_client.config import settings
from redis import StrictRedis, ConnectionError
import json
import logging
from datetime import datetime
from filelock import Timeout, FileLock

class OAuthClient:
    """
    TODO:  There's really no easy way now to modify any of the token cache vars here.  Should allow getter/setter for those token cache items
    """
    def __init__(self, client_id:str):
        assert client_id is not None, "Require a client API ID string to init"
        from oauth_client.objects.token_store import OAuthTokenStore

        self._token_cache = OAuthTokenStore()

        assert self._token_cache._get_client_id(client_id) is not None, "Client API ID not already defined, add this client ID to the token cache first"
        self.client_id = client_id

    def is_auth_code_set(self, ):
        return self._token_cache.is_auth_code_set(self.client_id)

    @property
    def auth_code(self, ):
        my_auth_code = self._token_cache.get_access_code(self.client_id)
        self._last_auth = my_auth_code
        return my_auth_code
    
    @auth_code.setter
    def auth_code(self, val):
        self._token_cache.set_access_code(self.client_id, val)
        return True

    @property
    def client_id(self, ):
        return self._client_id
    
    @client_id.setter
    def client_id(self, val):
        self._client_id = val
        return self._client_id

    @property
    def refresh_token(self, ):
        return self._token_cache.get_refresh_token(self.client_id)

    @refresh_token.setter
    def refresh_token(self, val:dict):
        assert 'token' in val, "Setting refresh token requires dict with a key of 'token'"
        assert 'ttl' in val, "Setting refresh token requires dict with a key of 'ttl'"

        self._token_cache.set_refresh_token(self.client_id, val['token'], val['ttl'])
        return self.refresh_token

    @property
    def access_token(self, ):
        return self._token_cache.get_access_code(self.client_id)
    
    @access_token.setter
    def access_token(self, val):
        assert 'token' in val, "Setting refresh token requires dict with a key of 'token'"
        assert 'ttl' in val, "Setting refresh token requires dict with a key of 'ttl'"

        self._token_cache.set_access_token(self.client_id, val['token'], val['ttl'])
        return self.access_token

    @property
    def client_info(self):
        client_data = self._token_cache.client_token_info(self.client_id)

        client_data['redis_keys'] = {
            'access_code': self._token_cache.redis_key_name('access_code', self.client_id),
            'token_refresh': self._token_cache.redis_key_name('token_refresh', self.client_id),
            'token_access': self._token_cache.redis_key_name('token_access', self.client_id),
        }

        client_data['redis_values'] = {
            'access_code': self._token_cache.is_auth_code_set(self.client_id),
            'token_refresh': self._token_cache.get_refresh_token(self.client_id),
            'token_access': self._token_cache.get_access_token(self.client_id),
        }

        return client_data
