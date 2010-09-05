# Shell.

from user import open_, read, fork, wait, chdir, exit_, exec_, close, pipe
from user import O_RDWR, O_WRONLY, O_CREATE
from printf import printf
from ulib import gets, strlen, strchr


# #include "types.h"
# #include "user.h"
# #include "fcntl.h"


EXEC = 1
REDIR = 2
PIPE = 3
LIST = 4
BACK = 5


MAXARGS = 10


class Cmd:
    pass


class ExecCmd(Cmd):
    def __init__(self):
        self.type = EXEC
        self.argv = [None] * MAXARGS


class RedirCmd(Cmd):
    def __init__(self, subcmd, filename, mode, fd):
        self.type = REDIR
        self.cmd = subcmd
        self.filename = filename
        self.mode = mode
        self.fd = fd


class PipeCmd(Cmd):
    def __init__(self, left, right):
        self.type = PIPE
        self.left = left
        self.right = right


class ListCmd(Cmd):
    def __init__(self, left, right):
        self.type = LIST
        self.left = left
        self.right = right


class BackCmd(Cmd):
    def __init__(self, subcmd):
        self.type = BACK
        self.cmd = subcmd


# Execute cmd.  Never returns.
def runcmd(cmd):
    p = [0, 0]
    
    if cmd == 0:
        exit_()
    
    if cmd.type == EXEC:
        ecmd = cmd
        if ecmd.argv[0] == 0:
            exit_()
        exec_(ecmd.argv[0], ecmd.argv)
        printf(2, "exec %s failed\n", ecmd.argv[0])
        
    elif cmd.type == REDIR:
        rcmd = cmd
        close(rcmd.fd)
        if open_(rcmd.file, rcmd.mode) < 0:
            printf(2, "open %s failed\n", rcmd.file);
            exit_()
        runcmd(rcmd.cmd)
        
    elif cmd.type == LIST:
        lcmd = cmd
        if fork1() == 0:
            runcmd(lcmd.left)
        wait()
        runcmd(lcmd.right)
        
    elif cmd.type == PIPE:
        pcmd = cmd
        if pipe(p) < 0:
            panic("pipe")
        if fork1() == 0:
            close(1)
            dup(p[1])
            close(p[0])
            close(p[1])
            runcmd(pcmd.left)
        if fork1() == 0:
            close(0)
            dup(p[0])
            close(p[0])
            close(p[1])
            runcmd(pcmd.right)
        close(p[0])
        close(p[1])
        wait()
        wait()
        
    elif cmd.type == BACK:
        bcmd = cmd
        if fork1() == 0:
            runcmd(bcmd.cmd)
        
    else:
        panic("runcmd")
    
    exit_()


def getcmd(nbuf):
    printf(2, "$ ")
    n, buf = gets(nbuf)
    if buf[0] == 0: # EOF
        return -1, buf
    return 0, buf


def main(argv, argc):
    #static char buf[100];
    #int fd;
    
    # Assumes three file descriptors open.
    # while((fd = open("console", O_RDWR)) >= 0){
    while True:
        fd = open_("console", O_RDWR)
        if fd < 0: break
        
        if fd >= 3:
            close(fd)
            break
    
    # Read and run input commands.
    # while(getcmd(buf, sizeof(buf)) >= 0){
    while True:
        n, buf = getcmd(100)
        if n < 0: break
        
        if buf[0] == "c" and buf[1] == "d" and buf[2] == " ":
            # Clumsy but will have to do for now.
            # Chdir has no effect on the parent if run in the child.
            buf = buf[:strlen(buf) - 1] # chop \n
            if chdir(buf[3:]) < 0:
                printf(2, "cannot cd %s\n", buf[3:])
            continue
        
        fork1(runcmd, parsecmd(buf))
        # wait()
    
    exit_()


def panic(s):
    printf(2, "%s\n", s)
    exit_()


def fork1(func, *argv):
    pid = fork(func, *argv)
    if pid == -1:
        panic("fork")
    return pid


# Parsing


WHITESPACE = " \t\r\n\v"
SYMBOLS = "<|>&;()"


def gettoken(st, ps, es):

    s = ps
    while s < es and strchr(WHITESPACE, st[s]):
        s += 1
    
    q = s
    
    ret = st[s]
    
    if st[s] == "\0": # @@@ can this happen?
        pass
    elif st[s] in "|();&<":
        s += 1
    elif st[s] == ">":
        s += 1
        if st[s] == ">":
            ret = "+"
            s += 1
    else:
        ret = "a"
        while s < es and not strchr(WHITESPACE, st[s]) and not strchr(SYMBOLS, st[s]):
            s += 1
    
    eq = s
    
    while s < es and strchr(WHITESPACE, st[s]):
        s += 1
    
    ps = s
    
    return ret, ps, q, eq


def peek(st, ps, es, toks):
    s = ps
    while s < es and strchr(WHITESPACE, st[s]):
        s += 1
    ps = s
    
    return (st[s] != "\0") and (strchr(toks, st[s]) != 0), ps


def parsecmd(st):
    s = 0
    es = s + strlen(st)
    
    cmd, s = parseline(st, s, es)
    
    dummy, s = peek(st, s, es, "\0")
    
    if s != es:
        printf(2, "leftovers: %s\n", st)
        panic("syntax")
    
    # nulterminate(cmd)
    
    return cmd


def parseline(st, ps, es):
    
    cmd, ps = parsepipe(st, ps, es)
    
    # while peek(ps, es, "&"):
    while True:
        dummy, ps = peek(st, ps, es, "&")
        if not dummy: break
        
        tok, ps, q, eq = gettoken(st, ps, es)
        
        cmd = BackCmd(cmd)
    
    dummy, ps = peek(st, ps, es, ";")
    if dummy:
        tok, ps, q, eq = gettoken(st, ps, es)
        cmd2, ps = parseline(st, ps, es)
        cmd = ListCmd(cmd, cmd2)
    
    return cmd, ps



def parsepipe(st, ps, es):
    
    cmd, ps = parseexec(st, ps, es)
    
    dummy, ps = peek(st, ps, es, "|")
    if dummy:
        tok, ps, q, eq = gettoken(st, ps, es)
        cmd2, ps = parsepipe(st, ps, es)
        cmd = PipeCmd(cmd, cmd2)
    
    return cmd, ps


def parseredirs(cmd, st, ps, es):
    
    while True:
        dummy, ps = peek(st, ps, es, "<>")
        if not dummy: break
        
        tok, ps, q, eq = gettoken(st, ps, es)
        
        tok2, ps, q, eq = gettoken(st, ps, es)
        if tok2 != "a":
            panic("missing file for redirection")
        
        if tok == "<":
            cmd = RedirCmd(cmd, st[q:eq], O_RDONLY, 0)
        elif tok == ">":
            cmd = RedirCmd(cmd, st[q:eq], O_WRONLY|O_CREATE, 1)
        elif tok == "+":
            cmd = RedirCmd(cmd, st[q:eq], O_WRONLY|O_CREATE, 1)
    
    return cmd, ps


# struct cmd*
# parseblock(char **ps, char *es)
# {
#   struct cmd *cmd;
# 
#   if(!peek(ps, es, "("))
#     panic("parseblock");
#   gettoken(ps, es, 0, 0);
#   cmd = parseline(ps, es);
#   if(!peek(ps, es, ")"))
#     panic("syntax - missing )");
#   gettoken(ps, es, 0, 0);
#   cmd = parseredirs(cmd, ps, es);
#   return cmd;
# }


def parseexec(st, ps, es):
    
    dummy, ps = peek(st, ps, es, "(")
    if dummy:
        return parseblock(ps, es);
    
    ret = ExecCmd()
    cmd = ret
    
    argc = 0
    ret, ps = parseredirs(ret, st, ps, es)
    
    while True:
        dummy, ps = peek(st, ps, es, "|)&;")
        if dummy: break
        
        tok, ps, q, eq = gettoken(st, ps, es)
        
        if tok == "\0":
            break
        if tok != "a":
            panic("syntax")
        cmd.argv[argc] = st[q:eq]
        argc += 1
        
        if argc >= MAXARGS:
            panic("too many args")
        
        ret, ps = parseredirs(ret, st, ps, es)
    
    cmd.argv[argc] = ""
    
    return ret, ps


# // NUL-terminate all the counted strings.
# struct cmd*
# nulterminate(struct cmd *cmd)
# {
#   int i;
#   struct backcmd *bcmd;
#   struct execcmd *ecmd;
#   struct listcmd *lcmd;
#   struct pipecmd *pcmd;
#   struct redircmd *rcmd;
# 
#   if(cmd == 0)
#     return 0;
#   
#   switch(cmd->type){
#   case EXEC:
#     ecmd = (struct execcmd*)cmd;
#     for(i=0; ecmd->argv[i]; i++)
#       *ecmd->eargv[i] = 0;
#     break;
# 
#   case REDIR:
#     rcmd = (struct redircmd*)cmd;
#     nulterminate(rcmd->cmd);
#     *rcmd->efile = 0;
#     break;
# 
#   case PIPE:
#     pcmd = (struct pipecmd*)cmd;
#     nulterminate(pcmd->left);
#     nulterminate(pcmd->right);
#     break;
#     
#   case LIST:
#     lcmd = (struct listcmd*)cmd;
#     nulterminate(lcmd->left);
#     nulterminate(lcmd->right);
#     break;
# 
#   case BACK:
#     bcmd = (struct backcmd*)cmd;
#     nulterminate(bcmd->cmd);
#     break;
#   }
#   return cmd;
# }
