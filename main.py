employees = {}

def uploadSalaryTable(file_name):

    weekend_days = []
    lower_limits = {}
    upper_limits = {}
    weekday_hour_rate = {}
    weekend_hour_rate = {}

    with open(file_name) as f:
        lines =  f.readlines()

        for i in lines:
            key_name, values = i.split('=')
            values = values.replace('\n','')

            if key_name == 'weekend_days':
                weekend_days = values.split(',')

            elif key_name == 'lower':
                lower_limit_pday = values.split(',')

                for j in lower_limit_pday:
                    shift, time = j.split('-')
                    lower_limits[shift] = time

            elif key_name == 'upper':
                upper_limit_pday = values.split(',')

                for j in upper_limit_pday:
                    shift, time = j.split('-')
                    upper_limits[shift] = time

            elif key_name == 'weekday_rate':
                weekday_h_rate_pshift = values.split(',')

                for j in weekday_h_rate_pshift:
                    shift, rate = j.split('-')
                    weekday_hour_rate[shift] = int(rate)
            
            elif key_name == 'weekend_rate':
                weekend_h_rate_pshift = values.split(',')

                for j in weekend_h_rate_pshift:
                    shift, rate = j.split('-')
                    weekend_hour_rate[shift] = int(rate)


    return weekend_days, lower_limits, upper_limits, weekday_hour_rate, weekend_hour_rate

def uploadEmployeesData(file_name):

    employees = {}

    with open(file_name) as f:
        lines = f.readlines()

    for i in lines:
        name, hourspday_chn = i.split('=')
        hourspday_chn = hourspday_chn.replace('\n','')
        hourspday = hourspday_chn.split(',')
        employees[name] = hourspday

    return employees

def replaceMidnight(ending_hours):

    ending_hours = '24'
    return ending_hours

def timeConversion(starting_hours, starting_minutes, ending_hours, ending_minutes):

    starting_time_hours = (float(starting_hours[0])*10) + (float(starting_hours[1])*1)
    starting_time_minutes = (float(starting_minutes[0])/6) + (float(starting_minutes[1])/60)
    starting_time = starting_time_hours + starting_time_minutes

    ending_time_hours = (float(ending_hours[0])*10) + (float(ending_hours[1])*1)
    ending_time_minutes = (float(ending_minutes[0])/6) + (float(ending_minutes[1])/60)
    ending_time = ending_time_hours + ending_time_minutes

    return starting_time, ending_time

def calculatePayment(starting_hours, starting_minutes, ending_hours, ending_minutes, rate):
    
    starting_time, ending_time = timeConversion(starting_hours, starting_minutes, ending_hours, ending_minutes)
    total_time_hours = ending_time - starting_time
    total_payment = total_time_hours * rate

    return total_payment

def contiguousShifts(starting_hours, starting_minutes, ending_hours, ending_minutes, upper_limits, starting_shift_name, rate, new_rate):

    threshold_hours, threshold_minutes = upper_limits[starting_shift_name].split(':')
    aux_payment = calculatePayment(starting_hours, starting_minutes, threshold_hours, threshold_minutes, rate)
    new_payment = calculatePayment(threshold_hours, threshold_minutes, ending_hours, ending_minutes, new_rate)
    total_payment = aux_payment + new_payment

    return total_payment

weekend_days, lower_limits, upper_limits, weekday_hour_rate, weekend_hour_rate = uploadSalaryTable('salary-table.txt')

employees = uploadEmployeesData('employee-data.txt')

for emp in employees:
    total_payment = 0

    for hourspday in employees[emp]:
        found_flag = False
        found_start_flag = False
        found_end_flag = False
        day = hourspday[:2]
        time_frame = hourspday[2:]
        lower_limit, upper_limit = time_frame.split('-') 
        
        if day in weekend_days:
            ratepshift = weekend_hour_rate

        else:
            ratepshift = weekday_hour_rate

        for starting_point in lower_limits:

            for ending_point in upper_limits:
                
                if starting_point == ending_point and found_flag == False:

                    starting_hours = lower_limit.split(':')[0]
                    ending_hours = upper_limit.split(':')[0]

                    if ending_hours == '00':
                        ending_hours = replaceMidnight(ending_hours)

                    lower_hour = lower_limits[starting_point].split(':')[0]
                    upper_hour = upper_limits[ending_point].split(':')[0]
                    
                    if int(starting_hours) >= int(lower_hour) and int(starting_hours) <= int(upper_hour):
                        starting_shift_name = starting_point
                        found_start_flag = True
                    
                    if int(ending_hours) >= int(lower_hour) and int(ending_hours) <= int(upper_hour):
                        ending_shift_name = ending_point
                        found_end_flag = True

                    found_flag = found_start_flag and found_end_flag

        starting_hours, starting_minutes = lower_limit.split(':')
        ending_hours, ending_minutes = upper_limit.split(':')

        if starting_shift_name == ending_shift_name:  
            
            upper_hour, upper_minutes = upper_limits[ending_shift_name].split(':')
            rate = float(ratepshift[starting_shift_name])
           
            if ending_hours == '00':
                ending_hours = replaceMidnight(ending_hours)

            if int(ending_hours) < int(upper_hour):
                total_payment_shift = calculatePayment(starting_hours, starting_minutes, ending_hours, ending_minutes, rate)

            else:

                if int(ending_minutes) > 0:

                    for shift in lower_limits:
                        hours = lower_limits[shift].split(':')[0]
                        
                        if hours == '00':
                            hours = replaceMidnight(hours)

                        if int(hours) == int(ending_hours):
                            new_rate = float(ratepshift[shift])

                    total_payment_shift = contiguousShifts(starting_hours, starting_minutes, ending_hours, ending_minutes, upper_limits, starting_shift_name, rate, new_rate)

                else:

                    total_payment_shift = calculatePayment(starting_hours, starting_minutes, ending_hours, ending_minutes, rate)

        else:

            lower_limit_hours, lower_limit_minutes = upper_limits[starting_shift_name].split(':')
            upper_limit_hours, upper_limit_minutes = lower_limits[ending_shift_name].split(':')

            if upper_limit_hours == '00':
                upper_limit_hours = replaceMidnight(upper_limit_hours)

            starting_time, ending_time = timeConversion(lower_limit_hours, lower_limit_minutes, upper_limit_hours, upper_limit_minutes)
            one_minute = float(1/60)

            if round(ending_time - starting_time, 3) == round(one_minute, 3):

                rate = float(ratepshift[starting_shift_name])
                new_rate = float(ratepshift[ending_shift_name])

                total_payment_shift = contiguousShifts(starting_hours, starting_minutes, ending_hours, ending_minutes, upper_limits, starting_shift_name, rate, new_rate)
            
        total_payment = total_payment + total_payment_shift

    print('The amount to pay ' + emp + ' is:', total_payment)
