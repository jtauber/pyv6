from user import open_, read, close, exit_
from ulib import strchr
from printf import printf


def wc(fd, name):
    l = 0
    w = 0
    c = 0
    inword = False
    
    # while((n = read(fd, buf, sizeof(buf))) > 0)
    while True:
        n, buf = read(fd, 512)
        if n <= 0:
            break
        
        for i in range(n):
            c += 1
            if buf[i] == "\n":
                l += 1
            if strchr(" \r\t\n\v", buf[i]):
                inword = False
            elif not inword:
                w += 1
                inword = True
    
    if n < 0:
        printf(1, "wc: read error\n")
        exit_(1)
    
    printf(1, "%d %d %d %s\n", l, w, c, name)


def main(argc, argv):
    if argc <= 1:
        wc(0, "")
        exit_()
    
    for i in range(1, argc):
        fd = open_(argv[i], 0)
        if fd < 0:
            printf(1, "cat: cannot open %s\n", argv[i])
            exit_()
        wc(fd, argv[i])
        close(fd)
    
    exit_()
