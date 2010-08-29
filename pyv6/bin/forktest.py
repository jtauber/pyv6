# Test that fork fails gracefully.
# Tiny executable so that the limit can be filling the proc table.

from user import fork, wait, exit_
from printf import printf


def forktest():
    printf(1, "fork test\n")
    
    for n in range(1000):
        pid = fork()
        if pid < 0:
            break
        if pid == 0:
            exit_()
    
    if n == 1000:
        printf(1, "fork claimed to work 1000 times!\n")
        exit_()
    
    while n > 0:
        if wait() < 0:
            printf(1, "wait stopped early\n")
            exit_(1)
        n -= 1
    
    if wait() != -1:
        printf(1, "wait got too many\n")
        exit_(1)
    
    printf(1, "fork test OK\n")


def main(argc, argv):
    forktest()
    exit_()
