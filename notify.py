import os
from twilio.rest import Client
import vobject

from profile import get_profile


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
    
def send_message(recepient, subject, lunch_bool):
    sub_dict = get_profile(subject)
    rec_dict = get_profile(recepient)
    rec_name, rec_pn = rec_dict['name'].split(), rec_dict['phonenum']
    sub_name, sub_pn = sub_dict['name'], sub_dict['phonenum']
    
    meal_type = 'lunch' if lunch_bool else 'dinner'
    
    #sub_pn, sub_name, fname = generate_virtual_card(sub_dict)
    tup = (rec_name[0], meal_type, sub_name, sub_pn)
    
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    
    client = Client(account_sid, auth_token)
    client.messages.create(
        body="Hey %s! You're recieved a MealMatch for %s: %s. You can text them at %s !" % tup,
        # media_url='$PATH/static/vcards/%s',
        from_='+19377497562',
        to='+1'+rec_pn)
    # sleep(3)
    # os.remove('$PATH/static/vcards/%s' % fname)

if __name__ == "__main__":
    send_message("jdapaah", 'avaidya', True, False)
