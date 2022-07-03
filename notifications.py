from os import environ
from twilio.rest import Client
import vobject
from user_profile import get_profile

def generate_virtual_card(pdict):
    phone_num = '+1'+pdict['phonenum']
    fname = pdict['netid']+'.vcf'
    name = pdict['name']
    first_name, last_name = name.split()

    vCard = vobject.vCard()
    vCard.add('N').value = vobject.vcard.Name(family=last_name, given=first_name)
    vCard.add('FN').value = name

    vCard.add('TEL')
    vCard.tel.value = phone_num
    vCard.tel.type_param = 'MOBILE'

    return phone_num, name, fname


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



