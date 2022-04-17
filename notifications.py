import os
from twilio.rest import Client


def send_message(message, phonenumber):


    account_sid = "ACd5ce2d27c589a1fe06b96e89542c243f"
    auth_token = "0b49a5fad5a4254fe67333a56d084aad"
    client = Client(account_sid, auth_token)

    print("Hello this worked?")
    print(name)
    print(phonenumber)

    message = client.messages \
        .create(
            body=message,
            from_='+15405016252',
            to='{}'.format(phonenumber)
        )

    print(message.sid)


def cancel_request_message(phonenumber):


    account_sid = "ACd5ce2d27c589a1fe06b96e89542c243f"
    auth_token = "0b49a5fad5a4254fe67333a56d084aad"
    client = Client(account_sid, auth_token)



    message = client.messages \
        .create(
            body='A match you recently made was cancelled. Check the MealMatch app for more information',
            from_='+15405016252',
            to='{}'.format(phonenumber)
        )

    print(message.sid)

