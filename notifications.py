import os
from twilio.rest import Client


def send_message(person):


    account_sid = "ACd5ce2d27c589a1fe06b96e89542c243f"
    auth_token = "0b49a5fad5a4254fe67333a56d084aad"
    client = Client(account_sid, auth_token)

    message = client.messages \
        .create(
            body='You matched with {} on MealMatch! Check the app for more information.'.format(person),
            from_='+15405016252',
            to='9088013229'
        )

    print(message.sid)
