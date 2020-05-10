# OAuth Client Helper

This here thing, what is it.  Intended to simplify the creation and authentication of OAuth-able API endpoints.

Using OAuth2.0, reading is good [RFC6749](https://tools.ietf.org/html/rfc6749)

I'm relatively postive something like this MUST exist but this is my curiousity itch and learning something new outcome.

This offers a VERY OPINIONATED solution utilizing REDIS (required), a Flask app and two python objects for token file management and API client generation.  I targetted this for personal development and use, not intended to be multi user or auth secure!

This has the intention of working to create a token cache per user (or per docker instance) that holds all the API authentication information needed for each of the API Clients the user wants.  It's important to view this as user specific because the auth codes generated here give underlying systems access AS THE USER!  Take a moment to understand what you're doing and who has access to what.  Codes are published to redis, BUT they are not sent to a specific USERS redis, so if you have access to "this" redis DB, you'd have access to the codes.  There are no tokens ever stored in the token cache file, so that's nice.

And now that I have a way to store it, I wanted as simple as possible (few bells/whistles of course) web handler to be able to initiate the OAuth sequence (generate the auth URL + querystring params) and capture the redirect (assuming successful auth).  The web framework here currently runs on 0.0.0.0:8080, however you'd connect over 127.0.0.1:8080 (use the IP versus localhost!)

Def check out the python packages [README](pypkg_README.rst)

## Motivation

I've spent some time very recently working on a few API integrations that utilized OAuth to get access to protected resources.  If you're not familiar, the OAuth sequence is pretty simple.

 1) You're client issues a HTTP(S) GET to the websites auth page (you'd get these details from websites API docs)
        * NOTE:  Currently built this to utilize QueryString params
        * The API Auth page defines the required fields
        * Oh NOTE 2:  You prolly need to set up a developer account and generate a API Client ID, and by prolly i mean do it if you haven't
 2) The website you redirected to guides you thru the auth ON THEIR SERVICE
 3) If auth is successful, the website issues a HTTP 302 to your supplied "redirect_uri"
        * NOTE:  Remember now, this HTTP 302 is done on your local machine, so /etc/hosts or local DNS shenanigans would work
 4) The redirect includes an access code string, typically a one time use thing
 5) You use this access code to generate access related tokens
 6) Use these tokens in your subsequent requests, typically in the HTTP header Authorization field

Ok now that we have that covered, the issue i was having is two fold

 1) I was annoyed with manually having to copy/paste the returned access code after authorization (yes i get annoyed easily)
 2) I wanted a formal way to handle defining, saving and accessing all these tokens across what could be many, or at least, a few services and API Client IDs

## Root Info

This includes a default docker-compose setup for launching/running this independently.  That will launch a REDIS instance and run the webapp on default.  Various config options are discussed in the python package.

I would think that typically the python package (under /src) would be imported and used independetly of this example.  You would push in your projects REDIS config and then import the token and client objects.

## Usage Notes

### Dev Notes

For building, the package utilizes dephell and poetry.  So for development you'd (obv ideally under a venv):

```bash
pip install poetry
# this automatically includes development related packages, use --no-dev
poetry install --no-root

# to build out everything
poetry build
dephell deps convert
```

### How to

Here's some simple answers on how to use the project as docker instance, if you want python specific, go to the [pypkg_READMD](pypkg_README.rst)

```bash
docker-compose up --detach
docker-compose logs oauth-helper
docker-compose exec oauth-helper /usr/bin/env bash -l

# Now you're in on the oauth-helpers bash shell
user@a2ncaldlj$ cat ~/.oauth*.json
```

You could modify the docker-compose to expose env vars to customize the setup.  The simplest one would be allowing the token file to be stored in a volume for persistence

```bash
export OAUTHCLIENT_OAUTH__TOKEN_CACHE=/usr/local/.my_token_cache.json && docker-compose run -v "local_file_cache.token:/usr/local/.my_token_cache.json" oauth-helper
```

## Todos

Oh yeah, this is one of those projects where the guy that posted it opines on know deficiencies.  Red flag for 'eh good enough' code for sure

 * Potentially look at allowing user to generate access tokens in the webapp.  As of right now I'm not doing any of that due to complications around query string params and response param differences between endpoints.  I'm generally thinking this is focused on the auth code helper and you'd custom spin code for getting and saving access tokens
 * There is NO update or modify features in the app currently.  More probably out of laziness, but if you need to edit, edit the file statically on the drive.
 * Would be nice to allow SSL cert files to be defined via env vars
 * Would be nice to allow IP listening and port in settings
 * Full disclosure, haven't tested building the py pkg just yet
 * Create more docker entrypoints to allow nearly all functions with a docker run command
 * Create CLI commands to help support curl/wget system
 * Not currently implementing any HTTP Authorization headers for any AUTHORIZATION  (eg HTTP basic auth) requests, prolly should offer that option
 * Not implementing any resource granting thru password credentials
 * Only really focused on Bearer access token_type, per RFC, the OAuth-HTTP-MAC is another option, not done here yet
 * Need to improve (read as: create) proper success or failure notifications for the events