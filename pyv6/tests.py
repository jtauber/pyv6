#!/usr/bin/env python

## library tests

from ulib import atoi
print atoi("5")


## user-space bin tests

from user import Exit

def run(line):
    l_split = line.split()
    cmd = l_split[0]
    main = __import__("bin." + cmd, fromlist=["main"]).main
    try:
        main(len(l_split), l_split)
    except Exit:
        return
    # if we get here we *should* have seen an Exit but didn't
    raise

run("echo hello world")
run("zombie")
run("kill")
run("kill 5")
run("ln")
run("ln /foo /bar")
run("rm")
run("rm /bar")
run("mkdir")
run("mkdir /baz")
run("cat /foo")
run("forktest")
run("wc /foo")
run("ls /foo")
run("ls /biz")
run("grep *foo /foo")

# run("mkfs")
# run("sh")
# run("usertests")
