from datetime import datetime, timedelta

def set_time():
    alarm_time = 0
    while alarm_time == 0:
        try:
            alarm_time = datetime.strptime(input("What time do you want to set the initial alarm for? "), "%I:%M %p")
            alarm_time = alarm_time.replace(day=datetime.now().day, month=datetime.now().month, year=datetime.now().year, second=0)
        except ValueError:
            print("Invalid time, make sure to use the format 12:00 AM")
            alarm_time = 0
    if alarm_time < datetime.now():
        alarm_time = alarm_time + timedelta(days=1)
    return alarm_time

def set_interval():
    interval = 0
    while interval == 0:
        try:
            interval = int(input("Enter the amount of time (in seconds) between each alarm: "))
        except ValueError:
            print("That is not a number, try again.")
            interval = 0
    return interval

def set_amount():
    alarms_amount = 0
    while alarms_amount == 0:
        try:
            alarms_amount = int(input("How many alarms do you want to set? "))
        except ValueError:
            print("That is not a number, try again.")
            alarms_amount = 0
    return alarms_amount

def main():
    times = []
    alarm_time = set_time()
    times.append(datetime.strptime(alarm_time.strftime("%m-%d-%Y %I:%M:%S %p"), "%m-%d-%Y %I:%M:%S %p"))
    interval = set_interval()
    alarms_amount = set_amount()
    end_time = alarm_time + timedelta(seconds=interval*alarms_amount)
    end_time = end_time.strftime("%m-%d-%Y %I:%M:%S %p")
    print(f"Made {alarms_amount} alarms, ending at {end_time}")
    for i in range(alarms_amount):
        times.append(datetime.strptime(times[len(times)-1].strftime("%m-%d-%Y %I:%M:%S %p"), "%m-%d-%Y %I:%M:%S %p") + timedelta(seconds=interval))
    file = open("files/alarms.txt", "w")
    for i in times:
        file.write(i.strftime("%m-%d-%Y %I:%M:%S %p") + "\n")
    file.close()

main()
