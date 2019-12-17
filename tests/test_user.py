import json
from flask import g
from API.extensions import mail

def test_email_change(app, user_1_auth_tokens):
  ''' Test user can change their email '''
  mail.init_app(app)
  with app.test_client() as client:
    response = client.post(
      '/u/email_change',
      data=json.dumps(dict(
        new_email='test@test.test'
      )),
      content_type='application/json',
      headers={'Authorization': 'Bearer ' + user_1_auth_tokens['access_token']}
    )
    data = json.loads(response.data.decode())
    with mail.record_messages() as outbox:
      print(outbox)
    assert response.status_code == 201
    assert 'Confirmation link sent to current email.' in data['message']
    # assert 'Email Change Confirmation' in data['subject ']