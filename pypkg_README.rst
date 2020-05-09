
API OAuth Redirect Lander
=========================

This is intended as a quick hitter to provide a simple method to gather and update a OAuth2 API access code.

The main porpoise of this is:


* Give a simple web interface for defining clients
* Provide handling of auth redirection and access code gathering
* Token helper class to keep track of many clients, auth codes and tokens (refresh/access)

  * NOTE:  This does not currently handle generating refresh or access tokens!

What this does is simply allow for a locally accessible (ie, your computer MUST be able to access) endpoint

This also assumes it has access to a shared REDIS cache with the larger TD API 'stuff'.

This means i MUST have access to the shared Message queue service, this defaults to using the docker-compose redis endpoint.  Typically we should push this to a central REDIS instance that you'd then consume from.

Install
-------

``pip install git+https://github.com/dedfriedly-inspirdev/oauth-client-helper.git``

Usage Examples
--------------

Ideally I envisioned this to be embedded into a larger app that handles refresh and/or access token as well as forcing user to authenticate.  So let's talk abit about how we might use this.

Create py file for launcing oauth-client app
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

So i'm in my project/superduper folder.  I'll create a silly oauth.py that my look like

.. code-block:: python

   #!/usr/bin/env python
   # NOTE: dummy path -> project/superduper/oauth.py
   from oauth_client import create_app

   app = create_app()

   if __name__ == '__main__':
       app.run(debug=True, host='0.0.0.0', port=8080, ssl_context='adhoc')

And then you'd start the oauth client webapp with

``python project/superduper/oauth.py``

Now go to your friendly browser and ``http://127.0.0.1:8080/``

Use the token inside your app
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

I'm going to assume you'll add client information thru the web and I won't cover that here.

So I'd say to utlize this it would something like:

.. code-block:: python

   from oauth_client.objects import OAuthTokenStore, OAuthClient

   my_store = OAuthTokenStore()
   my_store.list_service_names() # get all the currently used service groups

   # Let's loop over all the client data
   for cache_id, client_data in my_store._list_clients.items():
       print(f'Cache ID:{cache_id} --> Data:{client_data}')

       # The OAuthClient object is used to lock to specific client id
       my_cid = OAuthClient(client_data['client_id'])
       my_cid.client_info
       my_cid.is_auth_code_set() # NOTE:  READING the auth_code deletes the value as it's one time readable, this will tell you if it's set/available to read

Here's a simple workflow for getting and setting tokens

.. code-block:: python

   from oauth_client.objects import OAuthClient

   my_cid = OAuthClient('MySecretKeyHere==')

   # Let's do a test always to see if an auth code exists, we should update all tokens if that's set
   if my_cid.is_auth_code_set():
       my_auth_code = my_cid.auth_code # note if you read from it, it's deleted!
       refresh_token, access_token = use_code_to_get_token(my_cid.auth_url, my_auth_code) # some imaginary function that used auth code and returns a refresh and access token
       my_cid.refresh_token = {'token': refresh_token, 'ttl': 60} # setting token requires a dict of token and ttl
       my_cid.access_token = {'token': refresh_token, 'ttl': 60} # setting token requires a dict of token and ttl

Config Vars (NOT COMPLETE)
--------------------------

As a note, this uses dynaconf to expose or allow configuration files and env variables.  Below is a list of env variables available.  These support TOML typing.

All these should be exported or published into env

.. list-table::
   :header-rows: 1

   * - ENV Var
     - Description
     - Example
   * - OAUTHCLIENT_OAUTH__REDIRECT_URL
     - This is the URL used in the OAuth redirect call back
     - ```bash


export OAUTHCLIENT_OAUTH\ **REDIRECT_URL='https://my.domain:1234/new_endpoint'``` |
| OAUTHCLIENT_OAUTH**\ TOKEN_CACHE | This is the file to use to save client token info, could use this to move to a, eg, docker volume for offline storage | ``bash
export OAUTHCLIENT_OAUTH__TOKEN_CACHE=/path/to/${USER}_somefile.json`` |
| OAUTHCLIENT_OAUTH\ **TOKEN_KEY_PREPEND| This is the string all REDIS info is stored against | ```bash
export OAUTHCLIENT_OAUTH**\ TOKEN_KEY_PREPEND='myfunnykey:'``` |
| OAUTHCLIENT_MESSAGE_QUEUE__URL | This is the URL to the REDIS endpoint to publish tokens into | |

Some SSL Things
---------------

Because the redirecting application (eg not this one, but some fancier thing) often forces the redirect to HTTPS, I've built this to use Talisman and be served over HTTPS by default.  This can be annoying to actually use this silly thing due to how strict browsers have gotten over SSL security (oh the arms race dilema, how i hate thee).  You'll find the ssl context settings under ``src/oauth_client/wsgi.py``.  The biggest item of note is i'm using the adhoc ssl context!  To get a bit nicer to use, you should consider creatiner your own self-signed keys and using them in the ``app.run``.

Here's a link worth reading:  https://letsencrypt.org/docs/certificates-for-localhost/

TL;DR;

The simplest way to generate a private key and self-signed certificate for localhost is with this openssl command:

.. code-block:: bash

   openssl req -x509 -out localhost.crt -keyout localhost.key \
     -newkey rsa:2048 -nodes -sha256 \
     -subj '/CN=localhost' -extensions EXT -config <( \
      printf "[dn]\nCN=localhost\n[req]\ndistinguished_name = dn\n[EXT]\nsubjectAltName=DNS:localhost\nkeyUsage=digitalSignature\nextendedKeyUsage=serverAuth")

You'll then change the ssl context to something like

.. code-block::

   app.run(..., ssl_context=('localhost.crt', 'localhost.pem'))
