from os import environ
from twilio.rest import Client
import vobject
from user_profile import get_from_netid

def generate_virtual_card(netid):
    name, phone_num = get_from_netid(netid, "name", "phonenum")
    
    phone_num = '+1'+phone_num
    first_name, last_name = name.split()

    vCard = vobject.vCard()
    vCard.add('N').value = vobject.vcard.Name(family=last_name, given=first_name)
    vCard.add('FN').value = name

    vCard.add('TEL')
    vCard.tel.value = phone_num
    vCard.tel.type_param = 'MOBILE'


def send_message(message, phonenumber):
    account_sid = environ['TWILIO_ACCOUNT_SID']
    auth_token = environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

    print(message)
    print(phonenumber)

    message = client.messages \
        .create(
            body=message,
            from_='+1' + environ['TWILIO_NUMBER'],
            to='{}'.format(phonenumber)
        )



