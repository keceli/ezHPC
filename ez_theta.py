def qstat(user='', jobid='', 
          header='JobID:User:Score:WallTime:RunTime:Nodes:Queue:Est_Start_Time', 
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
    if jobid:
        cmd = f'--header={header} {jobid}'
    else:
        if user == '':
            user = getpass.getuser() #user = '$(whoami)'
        cmd = f'-u {user} --header={header}'
    if verbose:
        cmd = f'qstat -f -l {cmd}'
    else:
        cmd = f'qstat {cmd}'
    stream = os.popen(cmd)
    print(stream.read())
    return

def i_qstat():
    """
    Query about jobs submitted to queue manager with `qstat`.
    """
    from ipywidgets import interact_manual, widgets
    import getpass
    im = interact_manual(qstat, user=getpass.getuser())
    app_button = im.widget.children[4]
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
