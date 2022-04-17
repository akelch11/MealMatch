import os
from twilio.rest import Client


def send_message(message, phonenumber):


    account_sid = "ACd5ce2d27c589a1fe06b96e89542c243f"
    auth_token = "0b49a5fad5a4254fe67333a56d084aad"
    client = Client(account_sid, auth_token)

    print(message)
    print(phonenumber)

    message = client.messages \
        .create(
            body=message,
            from_='+15405016252',
            to='{}'.format(phonenumber)
        )



