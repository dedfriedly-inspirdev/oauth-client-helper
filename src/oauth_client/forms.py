from oauth_client.config import settings
from flask_wtf import FlaskForm
from wtforms import Form, FormField, FieldList, StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, optional


class QueryStringForm(Form):
    qs_key = StringField('Key')
    qs_val = StringField('Value')


class NewClientIDForm(FlaskForm):
    client_id = StringField('App Client ID',
        description='API Client ID you created',
        validators=[DataRequired(message="Need an OAuth API Client ID")])
    service_name = SelectField('Service Group Name',
        description='Arbitrary string used to group like client\'s together',
        validate_choice=False)
    other_service = BooleanField('New Service Group',
        description="Create a new service group",
        validators=[optional()])
    other_service_name = StringField('New Service Group Name',
        description="Name of the new service group desired",
        validators=[optional()])
    auth_url = StringField('App Authorization URL',
        validators=[DataRequired(message="Need an OAuth authorization URL for the service")])
    auth_url_qsparams = FieldList(
        FormField(QueryStringForm),
        max_entries=6)
    redirect_url = StringField(f'App Redirect/Callback URL',
        default=f'{settings.OAUTH.REDIRECT_URL}',
        validators=[optional()])

    submit = SubmitField('Submit')