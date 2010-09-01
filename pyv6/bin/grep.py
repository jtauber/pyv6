# Simple grep.  Only supports ^ . * $ operators.

from user import open_, read, close, exit_, write
from ulib import strchr
from printf import printf


def grep(pattern, fd):
    m = 0
    buf = " " * 1024
    
    # while (n = read(fd, buf+m, sizeof(buf)-m)) > 0
    while True:
        n, s = read(fd, 1024 - m)
        buf = buf[:m] + s
        if n <= 0: break
        
        m += n
        p = buf
        
        # while (q = strchr(p, '\n')) != 0
        while True:
            q = strchr(p, "\n")
            if q == 0: break
            
            q = "\0" + q[1:]
            if match(pattern, p):
                q = "\n" + q[1:]
                write(1, p, len(p) + 1 - len(q))
            
            p = q[1:]
        
        if p == buf:
            m = 0
        if m > 0:
            m -= len(p) - len(buf)
            # memmove(buf, p, m)
            buf = p[:m] + buf[m:]


def main(argc, argv):
    if argc <= 1:
        printf(2, "usage: grep pattern [file ...]\n")
        exit_()
    pattern = argv[1]
    
    if argc <=2:
        grep(pattern, 0)
        exit_()
    
    for i in range(2, argc):
        fd = open_(argv[i], 0)
        if fd < 0:
            printf(1, "grep: cannot open %s\n", argv[i])
            exit_()
        grep(pattern, fd)
        close(fd)
    exit_()


# Regexp matcher from Kernighan & Pike,
# The Practice of Programming, Chapter 9.

def match(re, text):
    if re[0] == "^":
        return matchhere(re[1:], text)
    
    while True: # must look at empty string
        if matchhere(re, text):
            return True
        text = text[1:]
        if text == "": break
    
    return False


# matchhere: search for re at beginning of text
def matchhere(re, text):
    if re == "":
        return True
    if len(re) > 1 and re[1] == "*":
        return matchstar(re[0], re[2:], text)
    if re == "$":
        return (text == "")
    if text != "" and (re[0] == "." or re[0] == text[0]):
        return matchhere(re[1:], text[1:])
    return False


# matchstar: search for c*re at beginning of text
def matchstar(c, re, text):
    while True: # a * matches zero or more instances
        if matchhere(re, text):
            return True
        if text == "":
            break
        text = text[1:]
        if text != c and c != ".":
            break
    return False
