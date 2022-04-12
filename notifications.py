import os
from twilio.rest import Client


def send_message(name, phonenumber):


    account_sid = "ACd5ce2d27c589a1fe06b96e89542c243f"
    auth_token = "0b49a5fad5a4254fe67333a56d084aad"
    client = Client(account_sid, auth_token)

    print("Hello this worked?")
    print(name)
    print(phonenumber)

    message = client.messages \
        .create(
            body='You matched with {} on MealMatch! Check the app for more information on your match.'.format(name),
            from_='+15405016252',
            to='{}'.format(phonenumber)
        )

    print(message.sid)
