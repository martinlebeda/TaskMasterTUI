#!/usr/bin/env python
import os
import re
import subprocess
import sys

EDIT_FILE = '/tmp/todo.txt'
EDITOR = os.environ.get('EDITOR','vim')

query = " | ".join(sys.argv[1:])

# execute taskmaster task
def exec_task(ids, *cmd):
    args = ["tm", "tk"] + list(cmd) + ids
    print(args)
    sp = subprocess.run(args)
    if sp.returncode != 0:
        print("subprocess error: ", sp.returncode)
        print(sp.stderr)
        exit(sp.returncode)


# execute notepad
def open_note(ids):
    p = subprocess.Popen(["tm", "tk", "taskname", "-f", *ids], stdout=subprocess.PIPE)
    tasknames = p.stdout.readlines()
    p.wait()
    for taskname in tasknames:
        taskname = taskname.strip().decode()
        subprocess.call(["lnch", "/home/martin/bin/poznKUkolu.sh", taskname])  # TODO Lebeda - configure


def copy_taskname(ids):
    """Copy taskname to clipboard"""
    p = subprocess.Popen(["tm", "tk", "taskname", *ids], stdout=subprocess.PIPE)
    tasknames = p.stdout.readlines()
    p.wait()
    tasknames_str = "".join(map(bytes.decode, tasknames))
    p = subprocess.Popen(['xsel', '-bi'], stdin=subprocess.PIPE)
    p.communicate(input=tasknames_str.encode())


def open_url(names):
    '''open urls from task'''
    for name in names:
        urls = re.findall('https*://\S+', name)
        for url in urls:
            subprocess.run(["chromium", url])


def open_jira(names):
    '''Open task in jira - proprietary MC function'''
    for name in names:
        jira_tasks = re.findall('MCV-\d+', name)
        for jira_task in jira_tasks:
            subprocess.run(["chromium", "http://mcv.marbes.cz/browse/" + jira_task])


# only for debug functions
# open_url(['https://www.databazeknih.cz/knihy/milenium-muz-ktery-hledal-svuj-stin-342724', 'http://github.com/tmux-plugins/tmux-open'])
# exit(0)

def edit_tasks(EDIT_FILE):
    subprocess.call([EDITOR, EDIT_FILE])
    subprocess.call(["tm", "tk", "import", EDIT_FILE])

while True:
    '''Main loop'''
    p1 = subprocess.Popen(["tm", "tk", "-C", "ls"], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["fzf", '--multi', '--no-sort', '--border', "--ansi",
                           '--reverse', '--print-query', '--query=' + query,
                           '--expect=ctrl-w,ctrl-p,ctrl-u,ctrl-j,ctrl-c,f5,f8,alt-a,alt-b,alt-c,alt-l,f2,f4,ctrl-alt-d'],
                          stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.wait()
    lines = p2.stdout.readlines()
    exit_code = p2.wait()

    if exit_code == 130:
        print("Exit task with", exit_code)
        exit(0)

    query = lines[0].strip().decode()
    lines.remove(lines[0])
    print("query ", query)

    key = lines[0].strip().decode()
    lines.remove(lines[0])
    print("key ", key)

    if key == 'f5':
        continue  # only refresh

    if key == 'f2':
        if os.path.exists(EDIT_FILE):
            os.remove(EDIT_FILE)
        edit_tasks(EDIT_FILE)

    ids = []
    names = []
    for line in lines:
        taskId = re.sub(r' .*', "", line.strip().decode())
        taskName = re.sub(r'^\d+ *', "", line.strip().decode())
        # taskNameStriped = re.sub(r'^\([A-Z]\) *', "", taskName).strip()
        # taskNameStriped = re.sub(r' [+@][^ ]+', "", taskNameStriped).strip()
        ids.append(taskId)
        names.append(taskName)

    if key == '':
        # print("mark done ", taskId)
        exec_task(ids, 'done')
    elif key == 'f8':
        print("mark defer ", taskId)
        exec_task(ids, "defer", "--context", "@defered")  # TODO Lebeda - konstantu za param
    elif key == 'f4':
        print("edit tasks", taskId)
        exec_task(ids, "export", EDIT_FILE)
        edit_tasks(EDIT_FILE)
    elif key == 'ctrl-alt-d':
        print("delete tasks", taskId)
        exec_task(ids, "delete")
    elif key == 'ctrl-w':
        exec_task(ids, "work", "-w")
    elif key == 'alt-a':
        exec_task(ids, "prio", "A")
    elif key == 'alt-b':
        exec_task(ids, "prio", "B")
    elif key == 'alt-c':
        exec_task(ids, "prio", "C")
    elif key == 'alt-l':
        exec_task(ids, "prio", "-c")
    elif key == 'ctrl-p':
        open_note(ids)
    elif key == 'ctrl-c':
        copy_taskname(ids)
    elif key == 'ctrl-j':
        open_jira(names)
    elif key == 'ctrl-u':
        open_url(names)

    # exit(0)  # only for debug
