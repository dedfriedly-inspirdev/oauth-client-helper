from oauth_client import settings
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, optional

class NewClientIDForm(FlaskForm):
    client_id = StringField('App Client ID',
        description='API Client ID you created',
        validators=[DataRequired(message="Need an OAuth API Client ID")])
    service_name = SelectField('Service Group Name',
        description='Arbitrary string used to group like client\'s together',
        validate_choice=False)
    auth_url = StringField('App Authorization URL',
        validators=[DataRequired(message="Need an OAuth authorization URL for the service")])
    redirect_url = StringField(f'App Redirc URL',
        default=f'{settings.OAUTH.REDIRECT_URL}',
        validators=[optional()])

    submit = SubmitField('Submit')