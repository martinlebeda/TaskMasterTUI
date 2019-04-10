#!/usr/bin/env python
import os
import re
import subprocess
import sys

EDIT_FILE = '/tmp/todo.txt'
# EDITOR = os.environ.get('EDITOR','vim')
EDITOR = 'vim'

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
            subprocess.run(["vivaldi-stable", url])  # TODO Lebeda - configure


def open_jira(names):
    '''Open task in jira - proprietary MC function'''
    for name in names:
        jira_tasks = re.findall('MCV-\d+', name)
        for jira_task in jira_tasks:
            subprocess.run(["vivaldi-stable", "http://mcv.marbes.cz/browse/" + jira_task])


# only for debug functions
# open_url(['https://www.databazeknih.cz/knihy/milenium-muz-ktery-hledal-svuj-stin-342724', 'http://github.com/tmux-plugins/tmux-open'])
# exit(0)

def edit_tasks(EDIT_FILE):
    subprocess.call([EDITOR, EDIT_FILE])
    subprocess.call(["tm", "tk", "import", EDIT_FILE])


showMaybe = False

while True:
    '''Main loop'''

    showMaybeParam = ""
    if showMaybe:
        print("maybe enabled")
        showMaybeParam = "-m"

    p1 = subprocess.Popen(["tm", "tk", "-C", "ls", showMaybeParam], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["fzf", '--multi', '--no-sort', '--border', "--ansi",
                           '--reverse', '--print-query', '--query=' + query,
                           '--expect=ctrl-w,ctrl-p,ctrl-u,ctrl-j,ctrl-alt-a,ctrl-alt-b,ctrl-alt-c,ctrl-alt-d,ctrl-c,'
                           + 'f5,f8,alt-a,alt-b,alt-c,alt-d,alt-e,alt-l,'
                           + 'f2,f4,ctrl-alt-r,ctrl-alt-m,alt-m,alt-n'],
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

    if key == 'ctrl-alt-a':
        query = '\'(A)'
        continue  # only refresh with new query

    if key == 'ctrl-alt-b':
        query = '\'(A) | \'(B)'
        continue  # only refresh with new query

    if key == 'ctrl-alt-c':
        query = '\'(A) | \'(B) | \'(C)'
        continue  # only refresh with new query

    if key == 'ctrl-alt-d':
        query = '\'@defered'
        continue  # only refresh with new query

    if key == 'f5':
        continue  # only refresh

    if key == 'ctrl-alt-m':
        showMaybe = not showMaybe
        if showMaybe:
            print("show maybe enabled")
        else:
            print("show maybe disabled")
        continue

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
        exec_task(ids, "defer", "--context", "@defered")  # TODO Lebeda - konstantu za param
    elif key == 'f4':
        exec_task(ids, "export", EDIT_FILE)
        edit_tasks(EDIT_FILE)
    elif key == 'ctrl-alt-r':
        exec_task(ids, "delete")
    elif key == 'ctrl-w':
        exec_task(ids, "work", "-w")
    elif key == 'alt-a':
        exec_task(ids, "prio", "A")
    elif key == 'alt-b':
        exec_task(ids, "prio", "B")
    elif key == 'alt-c':
        exec_task(ids, "prio", "C")
    elif key == 'alt-D':
        exec_task(ids, "prio", "D")
    elif key == 'alt-E':
        exec_task(ids, "prio", "E")
    elif key == 'alt-l':
        exec_task(ids, "prio", "-c")
    elif key == 'alt-n':
        exec_task(ids, "normal")
    elif key == 'alt-m':
        exec_task(ids, "maybe")
    elif key == 'ctrl-p':
        open_note(ids)
    elif key == 'ctrl-c':
        copy_taskname(ids)
    elif key == 'ctrl-j':
        open_jira(names)
    elif key == 'ctrl-u':
        open_url(names)

    # exit(0)  # only for debug
