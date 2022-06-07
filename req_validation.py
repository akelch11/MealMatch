from datetime import date, datetime, tzinfo, timedelta
from sys import stdout, stderr
from flask import Flask, request, session
from flask import render_template, make_response, redirect, url_for
import logging


def validate_scheduled_req(args):
     # We have to run the same validation we did in html
    # for if the user submits via the address link:(
    
    
    
    try:
        meal_type = args.get('meal')
        print('Meal type', meal_type, file=stdout)
        dhall = args.get('location')
        print('DHALL STRING:', dhall, file=stdout)
        start_time = args.get('start')
        end_time = args.get('end')
        at_dhall = args.get('atdhall')
    except Exception as ex:
        return make_response(render_template('page404.html'), 404)

    
    empty = meal_type is None or end_time is None or  \
            start_time is None or dhall is None or at_dhall is None

    if empty:
        return False

    valid_times = validate_scheduled_times(start_time, end_time, meal_type)

    print("Are times valid? ", valid_times, file= stdout)

    print('Returning: ', not (empty) and (valid_times), file=stdout )
    return (not empty) and (valid_times)


def validate_ondemand_req(args):
     # We have to run the same validation we did in html
    # for if the user submits via the address link:(
    
    
    try:
        meal_type = args.get('meal')
        print('Meal type', meal_type, file=stdout)
        dhall = args.get('location')
        print('DHALL STRING:', dhall, file=stdout)
        start_time = args.get('start')
        end_time = args.get('end')
        at_dhall = args.get('atdhall')
    except Exception as ex:
        return make_response(render_template('page404.html'), 404)

    
    empty = end_time is None or start_time is None or dhall is None or at_dhall is None

    if empty:
        return False

    valid_times = validate_ondemand_times(end_time)

    print("Are times valid? ", valid_times)

    return (not empty) and (valid_times)


def validate_ondemand_times(t1):
    
    if (t1 == None):
         return False
    else:

        now = datetime.now()

        time_end = datetime.fromisoformat(date.today().isoformat() + ' ' + t1 + ":00")
        
        print(time_end, file = stdout)
       
        lunch_start = ""

        if now.isoweekday() == 6 or now.isoweekday() == 7:
            lunch_start = "10:00"
        else:
            lunch_start = "11:30"

        time_lunch = datetime.fromisoformat(date.today().isoformat() + ' ' + lunch_start + ":00")
        time_lunch_end =  datetime.fromisoformat(date.today().isoformat() + ' 14:00:00')

        time_dinner = datetime.fromisoformat(date.today().isoformat() + ' 17:00:00')
        time_dinner_end = datetime.fromisoformat(date.today().isoformat() + ' 20:00:00')
        # // times are within lunch range and not in past

        is_lunchtime = time_lunch <= now and now <= time_lunch_end
        is_dinnertime = time_dinner <= now and now <= time_dinner_end
        
        lunch_bool = is_lunchtime and \
                    now <= time_end \
                    and time_end <= time_lunch_end \
                    and time_interval_len_minutes(now, time_lunch_end) >= 20               

        dinner_bool = is_dinnertime and \
                    now <= time_end \
                    and time_end <= time_dinner_end \
                    and time_interval_len_minutes(now, time_dinner_end) >= 20 
        
        print('Test flag conditions')
        print(is_lunchtime)
        print(now <= time_end)
        print(time_end <= time_lunch_end)
        print(time_interval_len_minutes(time_end, time_lunch_end) >= 20)

        return lunch_bool or dinner_bool



def validate_scheduled_times(t1, t2, meal):
    
    if (t1 == None or t2 == None or meal == None):
         return False
    else:

        now = datetime.now()

        time_start = datetime.fromisoformat(date.today().isoformat() + ' ' + t1 + ":00")
        time_end = datetime.fromisoformat(date.today().isoformat() + ' ' + t2 + ":00")
		
        print(time_start, file=stdout)
        print(time_end, file = stdout)
       
        lunch_start = ""

        if now.isoweekday() == 6 or now.isoweekday() == 7:
            lunch_start = "10:00"
        else:
            lunch_start = "11:30"

        time_lunch = datetime.fromisoformat(date.today().isoformat() + ' ' + lunch_start + ":00")
        time_dinner = datetime.fromisoformat(date.today().isoformat() + ' 17:00:00')
        
        time_lunch_end =  datetime.fromisoformat(date.today().isoformat() + ' 14:00:00')
        time_dinner_end = datetime.fromisoformat(date.today().isoformat() + ' 20:00:00')
        # // times are within lunch range and not in past
        
        lunch_bool = (meal == 'lunch') and \
                    time_lunch <= time_start and now <= time_start \
                    and time_start < time_end \
                    and time_end <= time_lunch_end \
                    and time_interval_len_minutes(time_start, time_end) >= 20               

        dinner_bool = (meal == "dinner") and \
            time_dinner <= time_start and now <= time_start \
            and time_start < time_end and time_end <= time_dinner_end \
            and time_interval_len_minutes(time_start, time_end) >= 20 
        
        # # print((meal == "dinner"))
        # print(time_lunch)
        # print( now <= time_start)
        return lunch_bool or dinner_bool


def time_interval_len_minutes(t1,t2):
    timedelta = t2 - t1
    print("TD: ",timedelta)
    print("min: ", timedelta.total_seconds() // 60)
    return timedelta.total_seconds() // 60
       


# if __name__ == "__main__":
#     print(validate_ondemand_times("15:59"), file = stdout)
