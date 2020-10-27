# %load https://raw.githubusercontent.com/keceli/ezHPC/main/ez_theta.py

def qstat(user='', jobid='', 
          header='JobID:User:Score:WallTime:RunTime:Nodes:Queue:Est_Start_Time',
          extra='',
          verbose=False):
    """
    Query about jobs submitted to queue manager with `qstat`.
    Parameters:
    ------------
    user: str, username
    jobid: str, cobalt job id, if more than one, seperate with a space
    header: str, customize info using headers 
    other header options: QueuedTime:TimeRemaining:State:Location:Mode:Procs:Preemptable:Index
    """
    import os
    import getpass
    cmd = ''
    if jobid:
        cmd = f'--header={header} {jobid}'
    else:
        if user == '':
            user = getpass.getuser() #user = '$(whoami)'
            cmd = f'-u {user} --header={header}'
        elif user.lower() == 'all':
            cmd = f'--header={header}'
        else:
            cmd = f'-u {user} --header={header}'
    if verbose:
        cmd = f'qstat -f -l {cmd}'
    else:
        cmd = f'qstat {cmd}'
    if extra:
        cmd += ' ' + extra
    print(f'Running {cmd} ...')
    stream = os.popen(cmd).read()
    if stream:
        print(stream)
    else:
        print('No active jobs')
    return

def i_qstat():
    """
    Query about jobs submitted to queue manager with `qstat`.
    """
    from ipywidgets import interact_manual, widgets
    import getpass
    im = interact_manual(qstat, user=getpass.getuser())
    app_button = im.widget.children[5]
    app_button.description = 'qstat'
    return

def qdel(jobid=''):
    """
    Delete job(s) with the given id(s).
    """
    cmd = f'qdel {jobid}'
    process = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    out, err = process.communicate()    
    print(f'stdout: {out}')
    print(f'stderr: {err}')
    return 

def i_qdel():
    """
    Delete job(s) with the given id(s).
    """
    from ipywidgets import interact_manual, widgets
    im = interact_manual(qdel)
    app_button = im.widget.children[1]
    app_button.description = 'qdel'
    return

def i_show_logs(job_prefix):
    """
    """
    from ipywidgets import widgets, Layout
    from IPython.display import display, clear_output
    from os.path import isfile
    outfile = f'{job_prefix}.output'
    errfile = f'{job_prefix}.error' 
    logfile = f'{job_prefix}.cobaltlog'
    if (isfile(outfile)):
        with open(outfile, 'r') as f:
            out = f.read()
        with open(errfile, 'r') as f:
            err = f.read()
        with open(logfile, 'r') as f:
            log = f.read()
        children = [widgets.Textarea(value=val, layout=Layout(flex= '1 1 auto', width='100%',height='400px')) 
                    for name,val in [(outfile,out), (errfile,err), (logfile,log)]]
        tab = widgets.Tab(children=children,layout=Layout(flex= '1 1 auto', width='100%',height='auto'))
        #ow = widgets.Textarea(value=out,description=outfile)
        #ew = widgets.Textarea(value=err,description=errfile)
        #lw = widgets.Textarea(value=log,description=logfile)
        tab.set_title(0, outfile)
        tab.set_title(1, errfile)
        tab.set_title(2, logfile)
        display(tab)
    return

def parse_cobaltlog(prefix='', verbose=True):
    """
    Return a dictionary with the content parsed from <prefix>.cobaltlog file
    """
    from os.path import isfile
    from dateutil.parser import parse
    from pprint import pprint
    logfile = f'{prefix}.cobaltlog'
    d = {}
    if isfile(logfile):
        with open(logfile, 'r') as f:    
            lines = f.readlines()
        for line in lines:
            if line.startswith('Jobid'):
                jobid = line.split()[-1].strip()
                d['jobid'] = jobid
            elif line.startswith('qsub'):
                cmd = line.strip()
                d['qsub_cmd'] = cmd
            elif 'submitted with cwd set to' in line:
                d['work_dir'] = line.split()[-1].strip()
                d['submit_time'] = parse(line.split('submitted')[0].strip())
            elif 'INFO: Starting Resource_Prologue' in line:
                d['init_time'] = parse(line.split('INFO:')[0].strip())
                d['queue_time'] = d['init_time'] - d['submit_time'].replace(tzinfo=None)
                d['queue_seconds'] = d['queue_time'].seconds
            elif 'Command:' in line:
                d['script'] = line.split(':')[-1].strip()
                d['start_time'] = parse(line.split('Command:')[0].strip())
                d['boot_time'] = d['start_time'].replace(tzinfo=None) - d['init_time']
                d['boot_seconds'] = d['boot_time'].seconds
            elif 'COBALT_PARTCORES' in line:
                d['partcores'] = line.split('=')[-1].strip()
            elif 'SHELL=' in line:
                d['shell'] = line.split('=')[-1].strip()
            elif 'COBALT_PROJECT' in line:
                d['project'] = line.split('=')[-1].strip()
            elif 'COBALT_PARTNAME' in line:
                d['partname'] = line.split('=')[-1].strip()
            elif 'LOGNAME=' in line:
                d['logname'] = line.split('=')[-1].strip()
            elif 'USER=' in line:
                d['user'] = line.split('=')[-1].strip()
            elif 'COBALT_STARTTIME' in line:
                d['cobalt_starttime'] = line.split('=')[-1].strip()
            elif 'COBALT_ENDTIME' in line:
                d['cobalt_endtime'] = line.split('=')[-1].strip()
            elif 'COBALT_PARTSIZE' in line:
                d['partsize'] = line.split('=')[-1].strip()
            elif 'HOME=' in line:
                d['home'] = line.split('=')[-1].strip()
            elif 'COBALT_JOBSIZE' in line:
                d['jobsize'] = line.split('=')[-1].strip()
            elif 'COBALT_QUEUE' in line:
                d['queue'] = line.split('=')[-1].strip()
            elif 'Info: stdin received from' in line:
                d['stdin'] = line.split()[-1].strip()
            elif 'Info: stdout sent to' in line:
                d['stdout'] = line.split()[-1].strip()
            elif 'Info: stderr sent to' in line:
                d['stderr'] = line.split()[-1].strip()
            elif 'with an exit code' in line:
                d['exit_code'] = line.split(';')[-1].split()[-1]
                d['end_time'] = parse(line.split('Info:')[0].strip())
                d['job_time'] = d['end_time'] - d['start_time']
                d['wall_seconds'] = d['job_time'].seconds             
    else:
        print(f'{logfile} is not found.')
    if verbose:
        pprint(d)
    return d

def print_cobalt_times(prefix=''):
    """
    Print timings from Cobalt logfile
    """
    d = parse_cobaltlog(prefix=prefix, verbose=False)
    for key, val in d.items():
        if '_time' in key or 'seconds' in key:
            print(f'{key}: {val}')

def get_job_script(nodes=1, ranks_per_node=1, affinity='-d 1 -j 1 --cc depth', command='',verbose=True):
    """
    Returns Cobalt job script with the given parameters
    TODO: add rules for affinity
    """
    script = '#!/bin/bash -x \n'
    ranks  = ranks_per_node * nodes
    script += f'aprun -n {ranks} -N {ranks_per_node} {affinity} {command}'
    if verbose: print(script)
    return script

def i_get_job_script_manual():
    from ipywidgets import widgets, Layout, interact_manual
    from IPython.display import display, clear_output
    from os.path import isfile
    inodes = widgets.BoundedIntText(value=1, min=1, max=4394, step=1, description='nodes', disabled=False)
    iranks_per_node = widgets.BoundedIntText(value=1, min=1, max=64, step=1, description='rank_per_nodes', disabled=False)
    im = interact_manual(get_job_script, nodes=inodes, ranks_per_node=irank_per_nodes)
    get_job_script_button = im.widget.children[4]
    get_job_script_button.description = 'get_job_script'
    return

def i_get_job_script():
    from ipywidgets import widgets, Layout, interact_manual
    from IPython.display import display, clear_output
    from os.path import isfile
    inodes = widgets.BoundedIntText(value=1, min=1, max=4394, step=1, description='nodes', disabled=False)
    iranks_per_node = widgets.BoundedIntText(value=1, min=1, max=64, step=1, description='ranks/node', disabled=False)
    iaffinity = widgets.Text(value='-d 1 -j 1 --cc depth',description='affinity')
    icommand = widgets.Text(value='',description='executable and args')
    out = widgets.interactive_output(get_job_script, {'nodes': inodes, 
                                                      'ranks_per_node': iranks_per_node,
                                                      'affinity': iaffinity,
                                                      'command': icommand})
    box = widgets.VBox([widgets.VBox([inodes, iranks_per_node, iaffinity, icommand]), out])
    display(box)
    return

def is_valid_theta_job(queue='', nodes=1, wall_minutes=10):
    """
    Return True if given <queue> <nodes> <wall_minutes> are valid for a job on Theta,
    Return False and print the reason otherwise.
    See https://alcf.anl.gov/support-center/theta/job-scheduling-policy-theta
    Parameters
    ----------
    queue: str, queue name, can be: 'default', 'debug-cache-quad', 'debug-flat-quad', 'backfill'
    nodes: int, Number of nodes, can be an integer from 1 to 4096 depending on the queue.
    wall_minutes: int, max wall time in minutes, depends on the queue and the number of nodes, max 1440 minutes
    """
    isvalid = True
    if queue.startswith('debug'):
        if wall_minutes > 60:
            print(f'Max wall time for {queue} queue is 60 minutes')
            isvalid = False
        if nodes > 8:
            print(f'Max number of nodes for {queue} queue is 8')
            isvalid = False
    else:
        if nodes < 128:
            print(f'Min number of nodes for {queue} queue is 128')
            isvalid = False
        else:
            if wall_minutes < 30:
                print(f'Min wall time for {queue} queue is 30 minutes') 
                isvalid = False
        if nodes < 256 and wall_minutes > 180:
                print(f'Max wall time for {queue} queue is 180 minutes') 
                isvalid = False
        elif nodes < 384 and wall_minutes > 360:
                print(f'Max wall time for {queue} queue is 360 minutes') 
                isvalid = False
        elif nodes < 640 and wall_minutes > 540:
                print(f'Max wall time for {queue} queue is 540 minutes') 
                isvalid = False
        elif nodes < 902 and wall_minutes > 720:
                print(f'Max wall time for {queue} queue is 720 minutes') 
                isvalid = False
        elif wall_minutes > 1440:
                print('Max wall time on Theta is 1440 minutes') 
                isvalid = False
        else:
            isvalid = True
    return isvalid
 
def qsub(project='',
         script='',
         script_file='',
         queue='debug-cache-quad',
         nodes=1,
         wall_minutes=30,
         attrs='ssds=required:ssd_size=128',
         workdir='',
         jobname='',
         stdin='',
         stdout=''):
    """
    Submits a job to the queue with the given parameters.
    Returns Cobalt Job Id if submitted succesfully.
    Returns 0 otherwise.
    Parameters
    ----------
    project: str, name of the project to be charged
    queue: str, queue name, can be: 'default', 'debug-cache-quad', 'debug-flat-quad', 'backfill'
    nodes: int, Number of nodes, can be an integer from 1 to 4096 depending on the queue.
    wall_minutes: int, max wall time in minutes, depends on the queue and the number of nodes, max 1440 minutes
    """
    import os
    import stat
    import time
    from subprocess import Popen, PIPE
    from os.path import isfile

    valid = is_valid_theta_job(queue=queue, nodes=nodes, wall_minutes=wall_minutes)
    if not valid:
        print('Job is not valid, change queue, nodes, or wall_minutes.')
        return 0
    with open(script_file, 'w') as f:
        f.write(script)
    time.sleep(1)
    exists = isfile(script_file)
    if exists:
        print(f'Created {script_file} on {os.path.abspath(script_file)}.')
        st = os.stat(script_file)
        os.chmod(script_file, st.st_mode | stat.S_IEXEC)
    time.sleep(1)
    cmd = f'qsub -A {project} -q {queue} -n {nodes} -t {wall_minutes} --attrs {attrs} '
    if workdir:
        cmd += f' --cwd {workdir}'
    if jobname:
        cmd += f' --jobname {jobname}'
    if stdin:
        cmd += f' -i {stdin}'
    if stdout:
        cmd += f' -o {stdout}'
    cmd += f' {script_file}'
    print(f'Submitting: \n {cmd} ...\n')
    process = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    out, err = process.communicate()
    print(f'job id: {out.decode("utf-8")}')
    print(f'stderr: {err.decode("utf-8")}')
    return out.decode("utf-8")

def i_qsub():
    """
    Submits a job to the queue with the given parameters.
    """
    from ipywidgets import widgets, Layout, interact_manual
    from IPython.display import display, clear_output
    from os.path import isfile
    inodes = widgets.BoundedIntText(value=1, min=1, max=4394, step=1, description='nodes', disabled=False)
    iranks_per_node = widgets.BoundedIntText(value=1, min=1, max=64, step=1, description='rank/nodes', disabled=False)
    iqueue = widgets.Dropdown(options=['debug-flat-quad','debug-cache-quad','default', 'backfill'],
                              description='queue',
                              value='debug-cache-quad')
    iwall_minutes = widgets.BoundedIntText(value=10, min=10, max=1440, step=10, description='wall minutes', disabled=False)

    iscript = widgets.Textarea(value='#!/bin/bash -x \n',
                               description='job script',
                               layout=Layout(flex= '0 0 auto', width='auto',height='200px'))
    iscript_file= widgets.Text(value='',description='job script file name')
    iproject= widgets.Text(value='',description='project')
    isave = widgets.Checkbox(value=False,description='save', indent=True)
    isubmit = widgets.Button(
                    value=False,
                    description='submit',
                    disabled=False,
                    button_style='success',
                    tooltip='submit job',
                    icon='')
    output = widgets.Output()
    i_get_job_script()
    display(iproject, inodes, iqueue, iwall_minutes, iscript_file, iscript, isubmit, output)
    jobid = ''
    def submit_clicked(b):
        with output:
            clear_output()
            jobid = qsub(project=iproject.value,
                         script=iscript.value,
                         script_file=iscript_file.value,
                         queue=iqueue.value,
                         nodes=inodes.value,
                         wall_minutes=iwall_minutes.value)
    isubmit.on_click(submit_clicked)
    return
