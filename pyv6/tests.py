#!/usr/bin/env python

## library tests

# from ulib import atoi
# print atoi("5")

# from bin.grep import match, matchhere
# print match("ten", "contents")
# print match("^ten", "contents")
# print match("^con", "contents")
# 
# exit()
# 
## user-space bin tests

from mock import MockFS, ModuleFile, go
MockFS.files["cat"] = ModuleFile("bin.cat")
MockFS.files["echo"] = ModuleFile("bin.echo")
MockFS.files["grep"] = ModuleFile("bin.grep")
MockFS.files["ls"] = ModuleFile("bin.ls")
MockFS.files["wc"] = ModuleFile("bin.wc")

def run(line):
    l_split = line.split()
    cmd = l_split[0]
    main = __import__("bin." + cmd, fromlist=["main"]).main
    go(main, len(l_split), l_split)

# run("echo hello world")
# run("zombie")
# run("kill")
# run("kill 5")
# run("ln")
# run("ln /foo /bar")
# run("rm")
# run("rm /bar")
# run("mkdir")
# run("mkdir /baz")
# run("cat /foo")
# run("forktest")
# run("wc /foo")
# run("ls /foo")
# run("ls /biz")
# run("grep ten /foo")
# run("grep ^ten /foo")
# run("grep ^con /foo")
# run("sh")

run("usertests")
