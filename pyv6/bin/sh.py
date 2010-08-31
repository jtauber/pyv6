# Shell.

from user import open_, read, fork, wait, chdir, exit_
from user import O_RDWR
from printf import printf
from ulib import gets, strlen


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

# 
# #define MAXARGS 10
# 

class Cmd:
    pass


class ExecCmd:
    def __init__(self):
        self.type = EXEC
        self.argv = [None]
        self.eargv = [None]


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

# void
# panic(char *s)
# {
#   printf(2, "%s\n", s);
#   exit();
# }
# 

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
# // Parsing
# 
# char whitespace[] = " \t\r\n\v";
# char symbols[] = "<|>&;()";
# 
# int
# gettoken(char **ps, char *es, char **q, char **eq)
# {
#   char *s;
#   int ret;
#   
#   s = *ps;
#   while(s < es && strchr(whitespace, *s))
#     s++;
#   if(q)
#     *q = s;
#   ret = *s;
#   switch(*s){
#   case 0:
#     break;
#   case '|':
#   case '(':
#   case ')':
#   case ';':
#   case '&':
#   case '<':
#     s++;
#     break;
#   case '>':
#     s++;
#     if(*s == '>'){
#       ret = '+';
#       s++;
#     }
#     break;
#   default:
#     ret = 'a';
#     while(s < es && !strchr(whitespace, *s) && !strchr(symbols, *s))
#       s++;
#     break;
#   }
#   if(eq)
#     *eq = s;
#   
#   while(s < es && strchr(whitespace, *s))
#     s++;
#   *ps = s;
#   return ret;
# }

def peek(ps, es, toks): pass
    # char *s;
    
    # s = *ps;
    # while(s < es && strchr(whitespace, *s))
    #     s++;
    # *ps = s;
    # return *s && strchr(toks, *s);

# struct cmd *parseline(char**, char*);
# struct cmd *parsepipe(char**, char*);
# struct cmd *parseexec(char**, char*);
# struct cmd *nulterminate(struct cmd*);
# 


def parsecmd(s):
    # char *es;
    # struct cmd *cmd;
    
    # es = s + strlen(s)
    cmd = parseline(s, None)
    
    # peek(&s, es, "")
    # 
    # if s != es:
    #     printf(2, "leftovers: %s\n", s)
    #     panic("syntax")
    # # nulterminate(cmd)
    
    return cmd


def parseline(ps, es):
    # struct cmd *cmd;
    
    cmd = parsepipe(ps, es)
    
    # while peek(ps, es, "&"):
    #     gettoken(ps, es, 0, 0);
    #     cmd = backcmd(cmd);
    # 
    # if peek(ps, es, ";"):
    #     gettoken(ps, es, 0, 0);
    #     cmd = listcmd(cmd, parseline(ps, es));
    
    return cmd



def parsepipe(ps, es):
    # struct cmd *cmd;
    
    cmd = parseexec(ps, es)
    
    # if peek(ps, es, "|"):
    #     gettoken(ps, es, 0, 0)
    #     cmd = pipecmd(cmd, parsepipe(ps, es))
    
    return cmd


def parseredirs(cmd, ps, es):
    # int tok;
    # char *q, *eq;
    
    while peek(ps, es, "<>"):
        tok = gettoken(ps, es, 0, 0)
        
        x, q, eq = gettoken(ps, es)
        if x != "a":
            panic("missing file for redirection")
        
        if tok == "<":
            cmd = redircmd(cmd, q, eq, O_RDONLY, 0)
        elif tok == ">":
            cmd = redircmd(cmd, q, eq, O_WRONLY|O_CREATE, 1)
        elif tok == "+":
            cmd = redircmd(cmd, q, eq, O_WRONLY|O_CREATE, 1)
    
    return cmd

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


def parseexec(ps, es):
    # char *q, *eq;
    # int tok, argc;
    # struct execcmd *cmd;
    # struct cmd *ret;
    
    # if(peek(ps, es, "("))
    #     return parseblock(ps, es);
    
    cmd = ExecCmd()
    
    argc = 0
    cmd = parseredirs(cmd, ps, es)
    
    # while(!peek(ps, es, "|)&;")){
    #     if((tok=gettoken(ps, es, &q, &eq)) == 0)
    #         break;
    #     if(tok != 'a')
    #         panic("syntax");
    #     cmd->argv[argc] = q;
    #     cmd->eargv[argc] = eq;
    #     argc++;
    #     if(argc >= MAXARGS)
    #         panic("too many args");
    #     ret = parseredirs(ret, ps, es);
    
    cmd.argv[argc] = 0
    cmd.eargv[argc] = 0
    
    return cmd


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
