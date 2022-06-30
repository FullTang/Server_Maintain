# Version 2.3
# Checks server status and restarts if the server has crashed.
# Restarts server daily at 1am if no one is online.
# Performs a backup of the server monthly.
# Deletes old backups (except for January backups) in February (as defined by delete_backup_month_int = 2).

import os, time, subprocess, logging, shutil

# Initialize the log settings
logging.basicConfig(filename='Server Maintain Log.log', level=logging.INFO)

RestartCanceled = False
LoginActive = False
WorldActive = False

last_online = "00:00:00"
PersonOnline1 = False
PersonOnline2 = False

Restart_Hour = 1
Restart_Time1 = '01:00:00'
Restart_Time1 = Restart_Time1[:1] + str(Restart_Hour) + Restart_Time1[2:]

Restart_Time2 = '01:00:59'
Restart_Time2 = Restart_Time2[:1] + str(Restart_Hour) + Restart_Time2[2:]

monthly_backup_day = "01"

Times_Ran = 0
Crash_Restarts = 0
Daily_Restarts = 0
Restart_canceled_online = 0


while 1 == 1:

    def getTasksDatabase(name):
        r = os.popen('tasklist /v').read().strip().split('\n')
        for i in range(len(r)):
            s = r[i]
            if name in r[i]:
                return r[i]
        return []


    if __name__ == '__main__':
        '''
        This code checks tasklist, and will print the status of a code
        '''

        imgName = 'cmd.exe'                    # Checks if the database is running.

        notResponding = 'Not Responding'

        r = getTasksDatabase(imgName)

        if not r:
            print('%s - No such process' % (imgName))

        elif 'Not Responding' in r:
            print('%s is Not responding' % (imgName))
            Crash_Restarts = Crash_Restarts + 1

        else:
            print('SingleCore Database is Running')

    def getTasksLogin(name):
        r = os.popen('tasklist /v').read().strip().split('\n')
        for i in range(len(r)):
            s = r[i]
            if name in r[i]:
                return r[i]
        return []


    if __name__ == '__main__':
        '''
        This code checks tasklist, and will print the status of a code
        '''

        imgName = '2_Login.exe'              # Checks if the Login server is running.

        notResponding = 'Not Responding'

        r = getTasksLogin(imgName)

        if not r:
            print('%s - No such process' % imgName)
            LoginActive = False

        elif 'Not Responding' in r:
            print('%s is Not responding' % imgName)
            LoginActive = False
            Crash_Restarts = Crash_Restarts + 1

        else:
            print('%s is Running' % imgName)
            LoginActive = True

    def getTasksWorld(name):
        r = os.popen('tasklist /v').read().strip().split('\n')
        for i in range(len(r)):
            s = r[i]
            if name in r[i]:
                return r[i]
        return []


    if __name__ == '__main__':
        '''
        This code checks tasklist, and will print the status of a code
        '''

        imgName = '3_World.exe'                  # Checks if the world server is running.

        notResponding = 'Not Responding'

        r = getTasksWorld(imgName)

        if not r:
            print('%s - No such process' % imgName)
            WorldActive = False

        elif 'Not Responding' in r:
            print('%s is Not responding' % imgName)
            WorldActive = False
            Crash_Restarts = Crash_Restarts + 1

        else:
            print('%s is Running' % imgName)
            WorldActive = True

    RestartNeeded = False
    RestartCanceled = False
    if LoginActive == False:
        print("Login not responding, restarting server.")
        RestartNeeded = True

    if WorldActive == False:
        print("World not responding, restarting server.")
        RestartNeeded = True

    # Checks if it needs a daily restart.

    if time.strftime('%H:%M:%S') < Restart_Time1:
        RestartNeeded1 = False
    else:
        RestartNeeded1 = True

    if time.strftime('%H:%M:%S') > Restart_Time2:
        RestartNeeded2 = False
    else:
        RestartNeeded2 = True

    if RestartNeeded1 and RestartNeeded2 == True:
        RestartNeeded = True

    # Checks the last time someone was online. The 'world.pkt' file is a log that updates when someone is logged in.

    if os.path.exists(r"C:\WoW Server\TriCore Server\SingleCoreR2\Logs\world.pkt"):
        last_online = time.ctime(os.path.getmtime(r"C:\WoW Server\TriCore Server\SingleCoreR2\Logs\world.pkt"))
        last_online = (last_online[11:19])

    if last_online < Restart_Time1:
        PersonOnline1 = False
    else:
        PersonOnline1 = True

    if last_online > Restart_Time2:
        PersonOnline2 = False
    else:
        PersonOnline2 = True

    if PersonOnline1 and PersonOnline2 == True:
        RestartCanceled = True
        RestartNeeded = False

    if RestartNeeded == True and RestartCanceled == False:
        Daily_Restarts = Daily_Restarts + 1

    if RestartCanceled == True:
        Restart_canceled_online = Restart_canceled_online + 1
        logging.info(" Restart canceled due to server activity at " + time.strftime('%x %H:%M:%S'))
        if Restart_Time1[1] <= str(8):
            Restart_Hour = Restart_Hour + 1
            Restart_Time1 = Restart_Time1[:1] + str(Restart_Hour) + Restart_Time1[2:]
            Restart_Time2 = Restart_Time2[:1] + str(Restart_Hour) + Restart_Time2[2:]
        time.sleep(60)
    else:
        pass

    # What happens when the server restarts

    if RestartNeeded == True:
        subprocess.call("taskkill /IM cmd.exe")         # Shutdown the database
        subprocess.call("taskkill /IM 2_Login.exe")     # Shutdown the login server
        subprocess.call("taskkill /IM 3_World.exe")     # Shutdown the world server
        time.sleep(5)

        # Deletes the ever growing "world.pkt" file, if it exists

        if os.path.exists(r"C:\WoW Server\TriCore Server\SingleCoreR2\Logs\world.pkt"):
            try:
                os.remove(r"C:\WoW Server\TriCore Server\SingleCoreR2\Logs\world.pkt")
                logging.info(" Successfully deleted world.pkt at " + time.strftime('%x %H:%M:%S'))
                time.sleep(1)
            except OSError:
                logging.warning(" Failed to delete world.pkt at " + time.strftime('%x %H:%M:%S'))

        else:
            print("No one has been online since last server restart.")

        # Creates a backup for current month on the day as defined by monthly_backup_day

        if (time.strftime('%d')) == monthly_backup_day:

            # First it checks to see if the backup has been created or not.

            if not os.path.exists(r"D:\Backup " + time.strftime('%m%d%y')):
                logging.info(" Attempting to backup on " + time.strftime('%x %H:%M:%S'))
                def createFolder(directory):
                    try:
                        if not os.path.exists(directory):
                            os.makedirs(directory)
                    except OSError:
                        print('Error: Creating directory. ' + directory)

                createFolder(r"D:\Backup " + time.strftime('%m%d%y'))
                time.sleep(1)

                # If the backup has not been created, copies the entire server into the backup folder, while offline.

                root_src_dir = r"C:\WoW Server"  # Source directory
                root_dst_dir = r"D:\Backup " + time.strftime('%m%d%y')  # Destination folder

                if os.path.exists(r"D:\Backup " + time.strftime('%m%d%y')):
                    print("Backing up server. Server will be online in about 1 hour from " + time.strftime('%H%M')
                          + " hours.")
                    try:
                        for src_dir, dirs, files in os.walk(root_src_dir):
                            dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)
                            if not os.path.exists(dst_dir):
                                os.makedirs(dst_dir)
                            for file_ in files:
                                src_file = os.path.join(src_dir, file_)
                                dst_file = os.path.join(dst_dir, file_)
                                if os.path.exists(dst_file):
                                    os.remove(dst_file)
                                shutil.copy(src_file, dst_dir)
                    except OSError:
                        logging.warning(" Failed to backup on " + time.strftime('%x %H:%M:%S'))

                while "0" + str(Restart_Hour) == time.strftime('%H'):  # Wait for 1 hr to ensure the copy is complete.
                    time.sleep(60)
                logging.info(" Backup completed on " + time.strftime('%x %H:%M:%S'))

        # Deletes old backups

        current_year = time.strftime("%y")
        previous_year = int(current_year) - 1
        delete_backup_month_int = 2

        if time.strftime("%m") == "0" + str(delete_backup_month_int):
            logging.info(" Attempting to delete backups on " + time.strftime('%x %H:%M:%S'))
            print("Attempting to delete old backups. Server will be online shortly.")
            if delete_backup_month_int < 10:
                delete_backup_month_str = str("0" + str(delete_backup_month_int))
            else:
                delete_backup_month_str = str(delete_backup_month_int)

            while delete_backup_month_int <= 12:

                if os.path.exists(r"D:\Backup " + delete_backup_month_str + time.strftime('%d') + str(previous_year)):

                    def deleteFolder(directory):
                        try:
                            if os.path.exists(directory):
                                os.removedirs(directory)
                        except OSError:
                            logging.warning(" Failed to delete backup on " + time.strftime('%x %H:%M:%S'))

                    deleteFolder(r"D:\Backup " + delete_backup_month_str + time.strftime('%d') + str(previous_year))
                    time.sleep(.1)
                    logging.info("Backup " + r"D:\Backup " + delete_backup_month_str + time.strftime('%d') +
                                 str(previous_year) + " deleted on " + time.strftime('%x %H:%M:%S'))

                delete_backup_month_int = delete_backup_month_int + 1
                if delete_backup_month_int < 10:
                    delete_backup_month_str = str("0" + str(delete_backup_month_int))
                else:
                    delete_backup_month_str = str(delete_backup_month_int)
                time.sleep(1)

        # Starts up the server

        os.startfile(r"C:\Users\Server\Desktop\1_Database - Shortcut.lnk")
        time.sleep(5)
        os.startfile(r"C:\Users\Server\Desktop\2_Login - Shortcut.lnk")
        time.sleep(5)
        os.startfile(r"C:\Users\Server\Desktop\3_World - Shortcut.lnk")
        Restart_Hour = 1
        Restart_Time1 = Restart_Time1[:1] + str(Restart_Hour) + Restart_Time1[2:]
        Restart_Time2 = Restart_Time2[:1] + str(Restart_Hour) + Restart_Time2[2:]
        time.sleep(60)

    time.sleep(10)
    Times_Ran = Times_Ran + 1

    print("----------------------------")
    print('Times Checked: ' + str(Times_Ran))
    print('Crash Restarts: ' + str(Crash_Restarts))
    print('Daily Restarts: ' + str(Daily_Restarts))
    print('Daily Restarts Canceled: ' + str(Restart_canceled_online))
    print("----------------------------")
