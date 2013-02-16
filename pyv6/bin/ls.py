from user import open_, exit_, close, fstat, read
from ulib import strlen, stat
from printf import printf

from user import T_FILE, T_DIR

DIRSIZ = 14  # @@@

#include "fs.h"


def fmtname(path):
    # static char buf[DIRSIZ+1];
    # find first character after last slash
    # for(p=path+strlen(path); p >= path && *p != '/'; p--)
    #   ;
    # p++;
    for i in range(strlen(path), 0, -1):
        if path[i - 1] == "/":
            break
    p = path[i:]
    
    # return blank-padded name
    
    if strlen(p) >= DIRSIZ:
        return p
    buf = p + " " * (DIRSIZ - strlen(p))
    return buf


def ls(path):
    
    fd = open_(path, 0)
    if fd < 0:
        printf(2, "ls: cannot open %s\n", path)
        return
    
    n, st = fstat(fd)
    if n < 0:
        printf(2, "ls: cannot stat %s\n", path)
        close(fd)
        return
    
    if st.type == T_FILE:
        printf(1, "%s %d %d %d\n", fmtname(path), st.type, st.ino, st.size)
    
    elif st.type == T_DIR:
        if strlen(path) + 1 + DIRSIZ + 1 > 512:
            printf(1, "ls: path too long\n")
        else:
            prefix = path + "/"
            
            #while (read(fd, &de, sizeof(de)) == sizeof(de))
            while True:
                n, de = read(fd, 20)  # @@@ 20 = sizeof(de)
                if n != 20:
                    break
                de_inum = int(de[:6])
                de_name = de[6:].strip()  # @@@
                
                if de_inum == 0:
                    continue
                path = prefix + de_name
                
                n, st = stat(path)
                if n < 0:
                    printf(1, "ls: cannot stat %s\n", path)
                    continue
                
                printf(1, "%s %d %d %d\n", fmtname(path), st.type, st.ino, st.size)
    close(fd)


def main(argc, argv):
    
    if argc < 2:
        ls(".")
        exit_()
    
    for i in range(1, argc):
        ls(argv[i])
    
    exit_()
