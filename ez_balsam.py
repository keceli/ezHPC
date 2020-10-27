def add_pgsql_path(path='/soft/datascience/balsam/pgsql/bin/'):
    """
    Add PostgreSQL directory to the path
    """
    import os
    if path not in os.environ['PATH']:
        os.environ['PATH'] += os.pathsep + path
    return

def check_pgsql(pgsql_exe='pg_ctl'):
    """
    Check PostgreSQL executable and version
    Balsam requires PostgreSQL version 9.6.4 or newer to be installed.
    TODO: Validate version
    """
    import os
    import shutil
    mypg_ctl = shutil.which(pgsql_exe)
    if mypg_ctl:
        print('PostgreSQL found: ', mypg_ctl)
        # pg_version = !$mypg_ctl --version
        pg_version = os.popen(f'{mypg_ctl} --version')
        print('PostgreSQL version: ', pg_version.read().split()[-1])
        return True
    else:
        print('PostgreSQL not found. Add PostgreSQL directory to the PATH')
        return False

def load_balsam():
    """
    Check Balsam module and print location and version
    """
    try:
        import balsam
        import os
        print('Balsam found: ', balsam.__file__)
        print('Balsam version: ', balsam.__version__)
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        add_pgsql_path()
        check_pgsql()
    except Exception as e:
        print('🛑 Exception caught')
        print(e, '\n')
        print('Make sure Balsam is installed and you are using the right kernel/environment')
    return
    
def get_databases(verbose=True):
    """
    Return balsam databases. If verbose, print.
    """
    from balsam import django_config
    from balsam.django_config.db_index import refresh_db_index
    from ipywidgets import interact
    import os
    databasepaths = []
    try:
        databasepaths.extend(refresh_db_index())
        if verbose:
            print(f'There are {len(databasepaths)} Balsam databases available:')
            for i,db in enumerate(databasepaths):
                print(f'{i}: {db}')
    except Excpetion as e:
        print('🛑 Exception caught during balsam.django_config.db_index.refresh_db_index:')
        print(e, '\n')
    return databasepaths 
    
def activate_database(db=''):
    """
    Activates Balsam database by setting the BALSAM_DB_PATH environment variable.
    """
    import os
    os.environ["BALSAM_DB_PATH"] = db
    print(f'Selected database: {os.environ["BALSAM_DB_PATH"]}')
    return
    
def i_activate_database():
    """
    Activates Balsam database by setting the index of BALSAM_DB_PATH environment variable
    from the dropdown list.
    """
    from ipywidgets import interact
    databasepaths = get_databases()
    interact(activate_database,db=[(i,db) for i,db in enumerate(databasepaths)])
    return

def get_apps(verbose=True):
    """
    Return apps in the balsam database. If verbose, print.
    """
    from balsam.core.models import ApplicationDefinition as App
    from balsam.scripts import postgres_control
    import os
    try:
        apps = App.objects.all()
        if verbose:
            print(f'Found {len(apps)} apps in {os.environ["BALSAM_DB_PATH"]}:')
            for i,app in enumerate(apps):
                print(f'{i}: {app.name}')
        return apps
    except Exception as e:
        if 'could not connect to server' in str(e):
            print('🛑 Server exception caught:')
            print(e,'\n')
            print(f'Trying to restart the Balsam server {os.environ["BALSAM_DB_PATH"]} ...')
            try:
                postgres_control.start_main(os.environ["BALSAM_DB_PATH"])
            except Exception as e:
                print('Exception caught during restart:')
                print(e,'\n') 
        elif 'exit status 127' in str(e):
            print('🛑 Exception 127 caught:')
            print(e, '\n')   
            print('Checking postgresql')
            if not check_pgsql():
                print('Trying to add postgresql to the path')
                add_pgsql_path()
                if check_pgsql():
                    print('postgresql added, try again')
                else:
                    print('Unsuccessful, you need to add postgresql to the path manually')
        else:
            print('🛑 Unknown exception caught:')
            print('You may need to restart Balsam server on terminal')
            print(e,'\n')
        return None
    
def i_show_apps():
    """
    Show apps saved in the Balsam database
    """
    import os
    from ipywidgets import widgets, Layout
    from IPython.display import display, clear_output
    children = [widgets.Textarea(value=str(app), layout=Layout(flex= '1 1 auto', width='400px',height='200px')) 
                        for app in apps]
    tab = widgets.Accordion(children=children,layout=Layout(flex= '1 1 auto', width='500px',height='auto'))
    for i,app in enumerate(apps):
        tab.set_title(i, app.name)
    print(f'Apps in the Balsam database {os.environ["BALSAM_DB_PATH"]}:')
    display(tab)
    return
    
def save_app(name, executable, description='', envscript='', preprocess='', postprocess=''):
    """
    Adds a new app with the given properties to the balsam database.
    Parameters
    ----------
    name: str, name of the app
    executable: str, path to the executable
    description: str, info about the app
    preprocess: str, path to the preprocessing script
    postprocess: str, path to the postprocessing script
    """
    from balsam.core.models import ApplicationDefinition as App
    import shutil
    import os
    newapp = App()
    if App.objects.filter(name=name).exists():
        print(f"An application named {name} already exists")
        return
    else:
        newapp.name        = name
        newapp.executable  = executable
        newapp.description = description
        newapp.envscript   = envscript
        newapp.preprocess  = preprocess
        newapp.postprocess = postprocess
        appexe = shutil.which(executable)
        if appexe:        
            print(f'{appexe} is found')
            newapp.save()
            print(f'{newapp.name} added to the balsam database {os.environ["BALSAM_DB_PATH"]}.')
        else:
            print('{executable} is not found')
    return

def i_save_app():
    """
    Adds a new app to the balsam database with the given properties to the balsam database.
    """
    from ipywidgets import interact_manual
    import os
    print(f'Balsam database: {os.environ["BALSAM_DB_PATH"]}')
    im = interact_manual(save_app, name='', executable='')
    app_button = im.widget.children[6]
    app_button.description = 'save app'
    return

def delete_app(name):
    """
    Delete Balsam app with the given name
    Note: All apps with the same name will be deleted
    """
    from balsam.core.models import ApplicationDefinition as App
    if App.objects.filter(name=name).exists():
        app = App.objects.filter(name=name)
        app.delete()
        print(f'{name} app deleted.')
    else:
        print(f'{name} app not found.' )
    return

def i_delete_app():
    """
    Delete selected Balsam app
    """    
    from balsam.core.models import ApplicationDefinition as App
    from ipywidgets import widgets, interact_manual
    from IPython.display import display, clear_output
    import os
    print(f'Balsam database: {os.environ["BALSAM_DB_PATH"]}')
    allapps = [app.name for app in App.objects.all()]
    idelete = widgets.Button(
                    value=False,
                    description='delete app',
                    disabled=False,
                    button_style='danger',
                    tooltip='Delete app',
                    icon='')
    iapps = widgets.Dropdown(options=allapps, description='app')
    output = widgets.Output()
    display(iapps,idelete,output)
    def delete_clicked(b):
        with output:
            clear_output()
            delete_app(iapps.value)
    idelete.on_click(delete_clicked)
    return   

def save_job(name, workflow, application, description='', 
            args='', num_nodes=1, ranks_per_node=1,
            cpu_affinity='depth', data={}, environ_vars=''):
    """
    Adds and returns a new job with the given properties
    """
    from balsam.launcher.dag import BalsamJob
    from balsam.core.models import ApplicationDefinition as App
    import os
    job                = BalsamJob()
    job.name           = name
    job.workflow       = workflow
    job.application    = application
    job.description    = description
    job.args           = args
    job.num_nodes      = num_nodes
    job.ranks_per_node = ranks_per_node
    job.cpu_affinity   = cpu_affinity
    job.environ_vars   = environ_vars
    job.data           = {}
    job.save()
    print(f'{job.name} {job.job_id} added to the balsam database {os.environ["BALSAM_DB_PATH"]}.')
    return job

def i_save_job():
    """
    Adds and returns a new job with the given properties
    """
    from ipywidgets import interact, interact_manual
    from IPython.display import display, clear_output
    from balsam.core.models import ApplicationDefinition as App
    from ipywidgets import widgets
    import os
    print(f'Balsam database: {os.environ["BALSAM_DB_PATH"]}')
    apps = App.objects.all()
    appnames = [app.name for app in apps]
    isave = widgets.ToggleButton(
                value=False,
                description='save job',
                disabled=False,
                button_style='success', # 'success', 'info', 'warning', 'danger' or ''
                tooltip='save job to the balsam database',
                icon='') 
    im = interact_manual(save_job, name='', workflow='', application=appnames, description='', 
              args='', num_nodes=range(1,4394), ranks_per_node=range(1,256),
              cpu_affinity=['depth','none'],data={},environ_vars='')
    app_button = im.widget.children[10]
    app_button.description = 'save job'
    return

def show_job_info(job_id='',show_output=False):
    """
    Prints verbose job info for a given job id.
    Parameters
    ----------
    job_id: str, Partial or full Balsam job id.
    """
    from balsam.launcher.dag import BalsamJob as Job
    import pathlib
    jobs = Job.objects.all().filter(job_id__contains=job_id)
    if len(jobs) == 1:
        thejob = jobs[0]
        print(jobs[0])
        if show_output:
            output = f'{thejob.working_directory}/{thejob.name}.out'
            if pathlib.Path(output).is_file():
                with open(output) as f:
                    out = f.read()
                print(f'Output file {output} content:')
                print(out)
            else:
                print(f'{output} not found.')
                print(f'Job state: {thejob.state}')
                if thejob.state =='CREATED':
                    print('The job has not run yet.')
    elif len(jobs) == 0:
        print('No matching jobs')
    else:
        print(f'{len(jobs)} jobs matched, enter full id.')
        print('Matched jobs:')
        for job in jobs:
            print(f'{job.name}: {job.job_id} ')
    return

def i_show_job_info():
    """Show the job verbose information for a given job id"""
    from ipywidgets import interact
    from IPython.display import display, clear_output
    interact(show_job_info)
    return

def list_jobs(state='ALL',workflow='ALL',app='ALL',name=''):
    """
    List Balsam jobs with the given properties
    """
    from balsam.launcher.dag import BalsamJob as Job
    from balsam.core.models import ApplicationDefinition as App
    jobs = Job.objects.all()
    print(f'Total number of jobs: {len(jobs)}')
    if state != 'ALL':
        jobs = jobs.filter(state=state)
    if workflow != 'ALL':
        jobs = jobs.filter(workflow=workflow)
    if app != 'ALL':
        jobs = jobs.filter(application=app)
    if name:
        jobs = jobs.filter(name__icontains=name)
    print(f'Selected number of jobs: {len(jobs)}')
    if len(jobs) > 0: 
        t = '{:<20}'.format('Name')
        t += ' {:>8}'.format('Nodes')
        t += ' {:>12}'.format('Ranks')
        t += ' {:^8}'.format('ID')
        if state =='JOB_FINISHED':
            t += '{:>12}'.format('Runtime')
        elif state =='ALL':
            t += '{:>15}'.format('State')
        print(t)
        for job in jobs:
            s = '{:<20.15}'.format(job.name)
            s += ' {:>8}'.format(job.num_nodes)
            s += ' {:>12}'.format(job.num_ranks)
            s += '  {:>8}'.format(str(job.job_id).split('-')[0])            

            if state =='JOB_FINISHED':
                s += '{:>12.3f}'.format(job.runtime_seconds)
            elif state =='ALL':
                s += '{:>15}'.format(job.state)
            print(s)
    return
            
def i_list_jobs():
    """
    List Balsam jobs with the given properties
    """
    from balsam.launcher.dag import BalsamJob as Job
    from balsam.core.models import ApplicationDefinition as App
    from ipywidgets import widgets, interact
    from IPython.display import display, clear_output

    allstates = ['ALL',
                 'CREATED',
                 'AWAITING_PARENTS',
                 'READY',
                 'STAGED_IN',
                 'PREPROCESSED',
                 'RUNNING',
                 'RUN_DONE',
                 'POSTPROCESSED',
                 'JOB_FINISHED',
                 'RUN_TIMEOUT',
                 'RUN_ERROR',
                 'RESTART_READY',
                 'FAILED',
                 'USER_KILLED']
    allworkflows = [wf['workflow'] for wf in Job.objects.order_by().values('workflow').distinct()]
    allworkflows.append('ALL')
    allapps = [app.name for app in App.objects.all()]
    allapps.append('ALL')
    ilist = widgets.Button(
                    value=False,
                    description='list jobs',
                    disabled=False,
                    button_style='info', # 'success', 'info', 'warning', 'danger' or ''
                    tooltip='List selected jobs',
                    icon='') 
    im = interact(list_jobs, state=allstates, workflow=allworkflows, 
                 app=allapps, name='')
    return

def delete_jobs(state='ALL',workflow='ALL',app='ALL',name='', confirm=False):
    """
    Delete Balsam jobs with the given properties
    """
    jobs = Job.objects.all()
    print(f'Total number of jobs: {len(jobs)}')
    if state != 'ALL':
        jobs = jobs.filter(state=state)
    if workflow != 'ALL':
        jobs = jobs.filter(workflow=workflow)
    if app != 'ALL':
        jobs = jobs.filter(application=app)
    if name:
        jobs = jobs.filter(name__icontains=name)
    print(f'Selected number of jobs: {len(jobs)}')
    if len(jobs) > 0: 
        t = '{:<20}'.format('Name')
        t += ' {:>8}'.format('Nodes')
        t += ' {:>12}'.format('Ranks')
        t += ' {:^8}'.format('ID')
        if state =='JOB_FINISHED':
            t += '{:>12}'.format('Runtime')
        elif state =='ALL':
            t += '{:>15}'.format('State')
        print(t)
        for job in jobs:
            s = '{:<20.15}'.format(job.name)
            s += ' {:>8}'.format(job.num_nodes)
            s += ' {:>12}'.format(job.num_ranks)
            s += '  {:>8}'.format(str(job.job_id).split('-')[0])            

            if state =='JOB_FINISHED':
                s += '{:>12.3f}'.format(job.runtime_seconds)
            elif state =='ALL':
                s += '{:>15}'.format(job.state)
            print(s)
        if confirm:
            try:
                for job in jobs:
                    print(f"Deleting {job.name} {str(job.job_id).split('-')[0]}")
                    job.delete()
                print(f'Deleted {len(jobs)} jobs')
            except Exception as e:
                print('Exception caught while deleting the selected jobs:')
                print(e)
    return
    
def i_delete_jobs():
    """
    Delete Balsam jobs with the given properties
    """
    from balsam.launcher.dag import BalsamJob as Job
    from balsam.core.models import ApplicationDefinition as App
    from ipywidgets import widgets, fixed
    from IPython.display import display, clear_output

    allstates = ['ALL',
                 'CREATED',
                 'AWAITING_PARENTS',
                 'READY',
                 'STAGED_IN',
                 'PREPROCESSED',
                 'RUNNING',
                 'RUN_DONE',
                 'POSTPROCESSED',
                 'JOB_FINISHED',
                 'RUN_TIMEOUT',
                 'RUN_ERROR',
                 'RESTART_READY',
                 'FAILED',
                 'USER_KILLED']
    allworkflows = [wf['workflow'] for wf in Job.objects.order_by().values('workflow').distinct()]
    allworkflows.append('ALL')
    allapps = [app.name for app in App.objects.all()]
    allapps.append('ALL')
    iconfirm = widgets.Checkbox(value=False, description='confirm delete')
    ilist = widgets.Button(
                    value=False,
                    description='list jobs',
                    disabled=False,
                    button_style='info', # 'success', 'info', 'warning', 'danger' or ''
                    tooltip='List selected jobs',
                    icon='') 
    idelete = widgets.Button(
                    value=False,
                    description='DELETE',
                    disabled=False,
                    button_style='danger', # 'success', 'info', 'warning', 'danger' or ''
                    tooltip='Deletes selected jobs',
                    icon='') # check
    istate = widgets.Dropdown(options=allstates,value='ALL',description='state')
    iworkflow = widgets.Dropdown(options=allworkflows,value='ALL',description='workflow')
    iapp = widgets.Dropdown(options=allapps,value='ALL',description='app')
    iname = widgets.Text(value='', description='name')
    output = widgets.Output()
    display(istate, iworkflow, iapp, iname, iconfirm, ilist, idelete, output)
    def delete_clicked(b):
        with output:
            clear_output()
            delete_jobs(state=istate.value,workflow=iworkflow.value,app=iapp.value,
                     name=iname.value, confirm=iconfirm.value)
    def list_clicked(b):
        with output:
            clear_output()
            list_jobs(state=istate.value,workflow=iworkflow.value,app=iapp.value,
                     name=iname.value)
    idelete.on_click(delete_clicked)
    ilist.on_click(list_clicked)
    return

def submit_jobs(project='',queue='debug-cache-quad',nodes=1,
           wall_minutes=30,job_mode='mpi',wf_filter='',
           save=False,submit=False):
    """
    Submits a job to the queue with the given parameters.
    Parameters
    ----------
    project: str, name of the project to be charged
    queue: str, queue name, can be: 'default', 'debug-cache-quad', 'debug-flat-quad', 'backfill'
    nodes: int, Number of nodes, can be an integer from 1 to 4096 depending on the queue.
    wall_minutes: int, max wall time in minutes, depends on the queue and the number of nodes, max 1440 minutes
    job_mode: str, Balsam job mode, can be 'mpi', 'serial'
    wf_filter: str, Selects Balsam jobs that matches the given workflow filter.
    """
    from balsam import setup
    setup()
    from balsam.service import service
    from balsam.core import models
    validjob = True
    QueuedLaunch = models.QueuedLaunch
    mylaunch = QueuedLaunch()
    mylaunch.project = project
    mylaunch.queue = queue
    mylaunch.nodes = nodes
    mylaunch.wall_minutes = wall_minutes
    mylaunch.job_mode = job_mode
    mylaunch.wf_filter = wf_filter
    mylaunch.prescheduled_only=False
    if queue.startswith('debug'):
        if wall_minutes > 60:
            validjob = False
            print(f'Max wall time for {queue} queue is 60 minutes')
        if nodes > 8:
            validjob = False
            print(f'Max number of nodes for {queue} queue is 8')
    else:
        if nodes < 128:
            validjob = False
            print(f'Min number of nodes for {queue} queue is 128')
    if save and validjob:
        mylaunch.save()
        print(f'Ready to submit')
        if submit:
            service.submit_qlaunch(mylaunch, verbose=True)
    
def i_submit_jobs():
    from ipywidgets import interact, widgets
    inodes = widgets.BoundedIntText(value=1, min=1, max=4394, step=1, description='nodes', disabled=False)
    iwall_minutes = widgets.BoundedIntText(value=10, min=10, max=1440, step=30, description='wall minutes', disabled=False)
    isave = widgets.Checkbox(value=False,description='save', indent=True)
    isubmit = widgets.ToggleButton(
                    value=False,
                    description='submit',
                    disabled=False,
                    button_style='success', # 'success', 'info', 'warning', 'danger' or ''
                    tooltip='submit job',
                    icon='') # ('check')
    im = interact(submit_jobs, project='',queue=['debug-flat-quad','debug-cache-quad','default', 'backfill'],
                         nodes=inodes, wall_minutes=iwall_minutes, job_mode=['mpi','serial'],
                         wf_filter='', save=isave, submit=isubmit)
