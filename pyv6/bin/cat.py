from user import open_, read, write, exit_
from printf import printf


def cat(fd):
    
    # while((n = read(fd, buf, sizeof(buf))) > 0)
    while True:
        n, buf = read(fd, 512)
        if n <= 0: break
        write(1, buf, n)
    
    if n < 0:
        printf(1, "cat: read error\n") # @@@ should that be 2?
    
    exit_(1)


def main(argc, argv):
    
    if argc <= 1:
        cat(0)
        exit_()
    
    for i in range(1, argc):
        fd = open_(argv[i], 0)
        if fd < 0:
            printf(1, "cat: cannot open %s\n", argv[i]) # @@@ should that be 2?
            exit_()
        cat(fd)
        close(fd)
    
    exit_()
