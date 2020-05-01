#!/usr/bin/env python
import os
import json
from urllib import parse
from redis import StrictRedis
from flask import Flask, session, render_template
from flask import request
from flask_talisman import Talisman
from flask_bootstrap import Bootstrap
from flask.ext.session import Session
from oauth_client import settings
from oauth_client.objects import OAuthTokenStore
from oauth_client.forms import NewClientIDForm


r = StrictRedis.from_url(settings.MESSAGE_QUEUE.URL, charset="utf-8", decode_responses=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = settings.SECRET_KEY
app.config['SESSION_TYPE'] = settings.SESSION_TYPE
app.config['SESSION_REDIS'] = settings.SESSION_REDIS
Talisman(app)
Bootstrap(app)

my_store = OAuthTokenStore()

@app.route('/', methods=['GET'])
def homepage():
    data = []
    if len(my_store._list_clients) > 0:
        for cache_id, client_data in my_store._list_clients.items():
            data.append(my_store.client_token_info(client_data['client_id']))
    return render_template("home.j2", client_data=json.dumps(data, indent=4, separators=(',', ': ')))

@app.route('/add-client', methods=['GET', 'POST'])
def add_client():
    form = NewClientIDForm(request.form)
    form.service_name.choices = [(x, x) for x in OAuthTokenStore.list_service_names()]

    if request.method == 'POST' and form.validate_on_submit():
        return redirect(url_for('/success'), code=302)

    return render_template("add_client.j2", form=form)

@app.route('/success', methods=['GET'])
def done_good():
    return render_template('success.j2')

@app.route('/auth_callback')
def auth_callback():    
    error = request.args.get('error', '')
    if error:
        return "Error: " + error
    state = request.args.get('state', '')
    if not is_valid_state(state):
    # Uh-oh, this request wasn't started by us!
        abort(403)
    code = request.args.get('code')
    # We'll change this next line in just a moment
    r.set(tdapi_access_code, code)
    return """Got a code!  Goodbye (code: %s....)""" % r.get(tdapi_access_code)[0:10]

def make_authorization_url():
    # Generate a random string for the state parameter
    # Save it for use later to prevent xsrf attacks

    from uuid import uuid4
    state = str(uuid4())
    save_created_state(CLIENT_ID, state)
    params = {"client_id": f'{CLIENT_ID}@AMER.OAUTHAP',
              "response_type": "code",
              "state": state,
              "redirect_uri": REDIRECT_URI}
    
    url = "https://auth.tdameritrade.com/auth?" + parse.urlencode(params)
    return url

# Left as an exercise to the reader.
# You may want to store valid states in a database or memcache,
# or perhaps cryptographically sign them and verify upon retrieval.
def save_created_state(key, val):
    r.set(key, val)

def is_valid_state(state):
    if r.get(redis_state_key) == state:
        r.delete(redis_state_key)
        return True
    else:
        return False


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=redirect_parsed.port)