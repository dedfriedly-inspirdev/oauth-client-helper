# API OAuth Redirect Lander

This is intended as a quick hitter to provide a simple method to gather and update a OAuth2 API access code.

The main porpoise of this is:

 * Give a simple web interface for defining clients
 * Provide handling of auth redirection and access code gathering
 * Token helper class to keep track of many clients, auth codes and tokens (refresh/access)
   * NOTE:  This does not currently handle generating refresh or access tokens!

What this does is simply allow for a locally accessible (ie, your computer MUST be able to access) endpoint

This also assumes it has access to a shared REDIS cache with the larger TD API 'stuff'.

This means i MUST have access to the shared Message queue service, this defaults to using the docker-compose redis endpoint.  Typically we should push this to a central REDIS instance that you'd then consume from.

## Config Vars

As a note, this uses dynaconf to expose or allow configuration files and env variables.  Below is a list of env variables available.  These support TOML typing.

All these should be exported or published into env

| ENV Var | Description | Example |
| --- | --- | --- |
| OAUTHCLIENT_OAUTH__REDIRECT_URL | This is the URL used in the OAuth redirect call back | ```bash
export OAUTHCLIENT_OAUTH__REDIRECT_URL='https://my.domain:1234/new_endpoint'``` |
| OAUTHCLIENT_OAUTH__TOKEN_CACHE | This is the file to use to save client token info, could use this to move to a, eg, docker volume for offline storage | ```bash
export OAUTHCLIENT_OAUTH__TOKEN_CACHE=/path/to/somefile.jsonk``` |
| OAUTHCLIENT_OAUTH__TOKEN_KEY_PREPEND| This is the string all REDIS info is stored against | ```bash
export OAUTHCLIENT_OAUTH__TOKEN_KEY_PREPEND='myfunnykey:'``` |
| OAUTHCLIENT_MESSAGE_QUEUE__URL | This is the URL to the REDIS endpoint to publish tokens into | |
