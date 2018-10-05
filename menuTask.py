#!/usr/bin/env python
import re
import subprocess
import sys

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


while True:
    '''Main loop'''
    p1 = subprocess.Popen(["tm", "tk", "-C", "ls"], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["fzf", '--multi', '--no-sort', '--border', "--ansi",
                           '--reverse', '--print-query', '--query=' + query,
                           '--expect=ctrl-w,ctrl-p,ctrl-c,f5,f8,alt-a,alt-b,alt-c,alt-l'],
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

    ids = []
    for line in lines:
        taskId = re.sub(r' .*', "", line.strip().decode())
        # taskName = re.sub(r'^\d+ *', "", line.strip().decode())
        # taskNameStriped = re.sub(r'^\([A-Z]\) *', "", taskName).strip()
        # taskNameStriped = re.sub(r' [+@][^ ]+', "", taskNameStriped).strip()

        ids.append(taskId)

    if key == '':
        # print("mark done ", taskId)
        exec_task(ids, 'done')
    elif key == 'f8':
        # print("mark defer ", taskId)
        exec_task(ids, "defer", "--context @upřesnit")  # TODO Lebeda - konstantu za param
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

    exit(0)  # only for debug
