# Shell.

from user import open_, read, fork, wait, chdir, exit_
from user import O_RDWR
from printf import printf
from ulib import gets, strlen, strchr


# 
# #include "types.h"
# #include "user.h"
# #include "fcntl.h"
# 
# // Parsed command representation
# #define EXEC  1
# #define REDIR 2
# #define PIPE  3
# #define LIST  4
# #define BACK  5

EXEC = 1

MAXARGS = 10


class Cmd:
    pass


class ExecCmd:
    def __init__(self):
        self.type = EXEC
        self.argv = [None] * MAXARGS


# struct redircmd {
#   int type;
#   struct cmd *cmd;
#   char *file;
#   char *efile;
#   int mode;
#   int fd;
# };
# 
# struct pipecmd {
#   int type;
#   struct cmd *left;
#   struct cmd *right;
# };
# 
# struct listcmd {
#   int type;
#   struct cmd *left;
#   struct cmd *right;
# };
# 
# struct backcmd {
#   int type;
#   struct cmd *cmd;
# };
# 
# int fork1(void);  // Fork but panics on failure.
# void panic(char*);
# struct cmd *parsecmd(char*);
# 

# Execute cmd.  Never returns.
def runcmd(cmd):
    # int p[2];
    # struct backcmd *bcmd;
    # struct execcmd *ecmd;
    # struct listcmd *lcmd;
    # struct pipecmd *pcmd;
    # struct redircmd *rcmd;
    
    if cmd == 0:
        exit_()
    
    if cmd.type == EXEC:
        if cmd.argv[0] == 0:
            exit_()
        exec_(cmd.argv[0], cmd.argv)
        printf(2, "exec %s failed\n", cmd.argv[0])
        
    elif cmd.type == REDIR:
        rcmd = redircmd(cmd)
        close(rcmd.fd)
        if open_(rcmd.file, rcmd.mode) < 0:
            printf(2, "open %s failed\n", rcmd.file);
            exit_()
        runcmd(rcmd.cmd)
        
    elif cmd.type == LIST:
        lcmd = listcmd(cmd)
        if fork1() == 0:
            runcmd(lcmd.left)
        wait()
        runcmd(lcmd.right)
        
    elif cmd.type == PIPE:
        pcmd = pipecmd(cmd)
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
        bcmd = backcmd(cmd)
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
        
        if fork1() == 0:
            runcmd(parsecmd(buf))
        wait()
    
    exit_()


def panic(s):
    raise Exception
    printf(2, "%s\n", s)
    exit_()


def fork1():
    pid = fork()
    if pid == -1:
        panic("fork")
    return pid


# Constructors

# struct cmd*
# redircmd(struct cmd *subcmd, char *file, char *efile, int mode, int fd)
# {
#   struct redircmd *cmd;
# 
#   cmd = malloc(sizeof(*cmd));
#   memset(cmd, 0, sizeof(*cmd));
#   cmd->type = REDIR;
#   cmd->cmd = subcmd;
#   cmd->file = file;
#   cmd->efile = efile;
#   cmd->mode = mode;
#   cmd->fd = fd;
#   return (struct cmd*)cmd;
# }
# 
# struct cmd*
# pipecmd(struct cmd *left, struct cmd *right)
# {
#   struct pipecmd *cmd;
# 
#   cmd = malloc(sizeof(*cmd));
#   memset(cmd, 0, sizeof(*cmd));
#   cmd->type = PIPE;
#   cmd->left = left;
#   cmd->right = right;
#   return (struct cmd*)cmd;
# }
# 
# struct cmd*
# listcmd(struct cmd *left, struct cmd *right)
# {
#   struct listcmd *cmd;
# 
#   cmd = malloc(sizeof(*cmd));
#   memset(cmd, 0, sizeof(*cmd));
#   cmd->type = LIST;
#   cmd->left = left;
#   cmd->right = right;
#   return (struct cmd*)cmd;
# }
# 
# struct cmd*
# backcmd(struct cmd *subcmd)
# {
#   struct backcmd *cmd;
# 
#   cmd = malloc(sizeof(*cmd));
#   memset(cmd, 0, sizeof(*cmd));
#   cmd->type = BACK;
#   cmd->cmd = subcmd;
#   return (struct cmd*)cmd;
# }


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
    print "peek", repr(st), ps, es, repr(toks)
    
    s = ps
    while s < es and strchr(WHITESPACE, st[s]):
        s += 1
    ps = s
    
    print st[s] != "\0"
    
    return (st[s] != "\0") and (strchr(toks, st[s]) != 0), ps


def parsecmd(st):
    s = 0
    es = s + strlen(st)
    
    print "parsecmd", repr(st), s, es
    
    cmd, s = parseline(st, s, es)
    
    print repr(st), s, es, st[s:es]
    
    dummy, s = peek(st, s, es, "\0")

    print repr(st), s, es, st[s:es]

    if s != es:
        printf(2, "leftovers: %s\n", st)
        panic("syntax")
    
    # nulterminate(cmd)
    
    return cmd, ps


def parseline(st, ps, es):
    
    cmd, ps = parsepipe(st, ps, es)
    
    # while peek(ps, es, "&"):
    #     gettoken(ps, es, 0, 0);
    #     cmd = backcmd(cmd);
    # 
    # if peek(ps, es, ";"):
    #     gettoken(ps, es, 0, 0);
    #     cmd = listcmd(cmd, parseline(ps, es));
    
    return cmd, ps



def parsepipe(st, ps, es):
    
    cmd, ps = parseexec(st, ps, es)
    
    # if peek(ps, es, "|"):
    #     gettoken(ps, es, 0, 0)
    #     cmd = pipecmd(cmd, parsepipe(ps, es))
    
    return cmd, ps


def parseredirs(cmd, st, ps, es):
    
    while True:
        dummy, ps = peek(st, ps, es, "<>")
        if not dummy: break
        
        assert False
        # tok, ps, q, eq = gettoken(st, ps, es)
        # 
        # if tok != "a":
        #     panic("missing file for redirection")
        # 
        # if tok == "<":
        #     cmd = redircmd(cmd, st, q, eq, O_RDONLY, 0) # st[q:eq] rather than st, q, eq
        # elif tok == ">":
        #     cmd = redircmd(cmd, st, q, eq, O_WRONLY|O_CREATE, 1)
        # elif tok == "+":
        #     cmd = redircmd(cmd, st, q, eq, O_WRONLY|O_CREATE, 1)
    
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
    
    # if(peek(ps, es, "("))
    #     return parseblock(ps, es);
    
    cmd = ExecCmd()
    
    argc = 0
    cmd, ps = parseredirs(cmd, st, ps, es)
    
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
        
        cmd, ps = parseredirs(cmd, st, ps, es)
    
    cmd.argv[argc] = ""
    
    return cmd, ps


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
