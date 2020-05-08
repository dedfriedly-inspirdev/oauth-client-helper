#!/usr/bin/env python
import os
import json
import logging
import pandas as pd
from urllib import parse
from redis import StrictRedis
from flask import current_app as app
from flask import session, render_template
from flask import request, redirect, abort
# from flask_session import Session
from oauth_client.config import settings
from oauth_client.objects import OAuthTokenStore, OAuthClient
from oauth_client.forms import NewClientIDForm


logging.warning(f"Message Queue URL: {settings.MESSAGE_QUEUE.URL}")

r = StrictRedis.from_url(settings.MESSAGE_QUEUE.URL, charset="utf-8", decode_responses=True)

my_store = OAuthTokenStore()

@app.route('/', methods=['GET'])
def homepage():
    data = []
    if len(my_store._list_clients) > 0:
        df = pd.DataFrame.from_dict(my_store._list_clients)

        # yes realize this is weird but trust me
        colnames = df.index.values.tolist()
        data = df.to_dict('split')['data']
    else:
        colnames = [ ]
        data = [ ]
    return render_template("home.j2", colnames=colnames, data=data)

@app.route('/add-client', methods=['GET', 'POST'])
def add_client():
    form = NewClientIDForm(request.form)
    form.service_name.choices = [(x, x) for x in OAuthTokenStore.list_service_names()]

    if request.method == 'GET':
        # Append the default args required in the qsparams
        form.auth_url_qsparams.append_entry({
                'qs_key': 'client_id',
                'qs_val': '{client_id}'
            })
        form.auth_url_qsparams.append_entry({
                'qs_key': 'redirect_uri',
                'qs_val': '{redirect_url}'
            })
        form.auth_url_qsparams.append_entry({
                'qs_key': 'response_type',
                'qs_val': 'code'
            })

    if request.method == 'POST' and form.validate_on_submit():
        client_data = {
            'client_id': form.client_id.data,
            'auth_url': form.auth_url.data,
            'redirect_url': form.redirect_url.data
        }

        if form.other_service.data == True:
            client_data.update({'service_name': form.other_service_name.data})
        else:
            client_data.update({'service_name': form.service_name.data})

        qs_params = { }
        for q in form.auth_url_qsparams.data:
            qs_params.update({q['qs_key']: q['qs_val']})

        client_data.update({'qs_params': qs_params})

        rdata = my_store.add_oauth_client(**client_data)

        return render_template('success.j2', client_data=rdata)

    return render_template("add_client.j2", form=form)


@app.route('/client-detail/<client_id>', methods=['GET'])
def client_id_detail(client_id):
    my_cid = OAuthClient(client_id)

    return render_template('client_detail.j2', client_id=client_id, client_data=json.dumps(my_cid.client_info, indent=4, separators=(',', ': ')))

@app.route('/client-auth/<client_id>', methods=['GET'])
def client_init_auth(client_id):
    my_cid = OAuthClient(client_id)

    my_cid_info = my_cid.client_info

    redirect_url = my_cid_info['redirect_url']

    my_qs_params = {}
    for k, v in my_cid_info['qs_params'].items():
        my_qs_params[k] = v.format(client_id=client_id, redirect_url=redirect_url)

    return redirect(make_authorization_url(auth_url=my_cid_info['auth_url'], qs_params=my_qs_params, client_id=client_id))

@app.route('/auth_callback')
def auth_callback():    
    error = request.args.get('error', '')
    if error:
        return "Error: " + error

    state = request.args.get('state', '')

    client_id = is_valid_state(state)
    if client_id is None:
    # Uh-oh, this request wasn't started by us!
        abort(403)
    
    code = request.args.get('code')
    # We'll change this next line in just a moment
    my_store.set_access_code(client_id, code)
    return render_template('success.j2', client_data={'auth_code': f'...snipped...{code[-15:]}'})

def make_authorization_url(auth_url, qs_params, client_id):
    # Generate a random string for the state parameter
    # Save it for use later to prevent xsrf attacks
    from uuid import uuid4
    state = str(uuid4())
    save_created_state(client_id, state)
    
    qs_params.update({
        "state": state,
    })
    
    url = f'{auth_url}?{parse.urlencode(qs_params)}'
    return url

# Left as an exercise to the reader.
# You may want to store valid states in a database or memcache,
# or perhaps cryptographically sign them and verify upon retrieval.
def save_created_state(client_id, val):
    r.set(f'oauth:_state', val, ex=30)
    # Need to save the Client ID we're working on!
    r.set(f'oauth:_state:_cid', client_id, ex=30)

    return None

def is_valid_state(state):
    if r.get(f'oauth:_state') == state:
        r.delete(f'oauth:_state')
        cid = r.get(f'oauth:_state:_cid')
        r.delete(f'oauth:_state:_cid')
        return cid
    else:
        return None
