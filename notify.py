import os
from twilio.rest import Client
import vobject

from profile import get_profile


def generate_virtual_card(pdict):
    name = pdict['name']
    first_name, last_name = name.split()
    phone_num = '+1'+pdict['phonenum']
    fname = pdict['netid']+'.vcf'
    return phone_num, fname

    vCard = vobject.vCard()
    vCard.add('N').value = vobject.vcard.Name(family=last_name, given=first_name)
    vCard.add('FN').value = name

    vCard.add('TEL')
    vCard.tel.value = phone_num
    vCard.tel.type_param = 'MOBILE'


    return phone_num, fname
    
def send_message(recepient, subject, lunch_bool, today_bool):
    profile_dict = get_profile(subject)
    rec_dict = get_profile(recepient)
    rec_name, rec_pn = rec_dict['name'].split(), rec_dict['phonenum']
    meal_day = 'today' if today_bool else 'tomorrow'
    meal_type = 'lunch' if lunch_bool else 'dinner'

    
    phone_num, fname = generate_virtual_card(profile_dict)
    print(rec_dict['name'])
    tup = (rec_name[0], meal_type, meal_day, profile_dict['name'], phone_num)
    
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    
    client = Client(account_sid, auth_token)
    client.messages.create(
        body="Hey %s! You're recieved a match for %s %s: %s. You can text them at %s !" % tup,
        # media_url='$PATH/static/vcards/%s',
        from_='+19377497562',
        to='+1'+rec_pn)
    # sleep(3)
    # os.remove('$PATH/static/vcards/%s' % fname)

if __name__ == "__main__":
    send_message("jdapaah", 'avaidya', True, False)
