import datetime, uuid
import win32com.client


class ScheduleTask():
    def CreateTask(self,schedule_action,schedule_arguments,time_schedule):
        scheduler = win32com.client.Dispatch('Schedule.Service')
        scheduler.Connect()
        root_folder = scheduler.GetFolder('\\')
        task_def = scheduler.NewTask(0)
        # Create trigger
        #start_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
        start_time = datetime.date.today()
        start_time = str(start_time) + "T" + time_schedule
        #start_time = str(start_time) + "T06:00:00" 
        print("Task Scheduler Update: ",start_time)
        TASK_TRIGGER_TIME = 2
        trigger = task_def.Triggers.Create(TASK_TRIGGER_TIME)
        #trigger.StartBoundary = start_time.isoformat()
        trigger.StartBoundary = start_time



        # Create action
        TASK_ACTION_EXEC = 0
        action = task_def.Actions.Create(TASK_ACTION_EXEC)
        action.ID = 'RUN UPLOADER' + str(uuid.uuid4())
        #action.ID = 'RUN UPLOADER'
        action.Path = schedule_action
        action.Arguments = schedule_arguments

        # Set parameters
        task_def.RegistrationInfo.Description = 'AVIR Image Uploader'
        task_def.Settings.Enabled = True
        task_def.Settings.StopIfGoingOnBatteries = False

        # Register task
        # If task already exists, it will be updated
        TASK_CREATE_OR_UPDATE = 6
        TASK_LOGON_NONE = 0
        root_folder.RegisterTaskDefinition(
        'AVIR Image Uploader' ,  # Task name
        task_def,
        TASK_CREATE_OR_UPDATE,
        '',  # No user
        '',  # No password
        TASK_LOGON_NONE)

    #createTask("06:00:00")