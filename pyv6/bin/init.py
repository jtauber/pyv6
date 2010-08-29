# init: The initial user-level program

from user import open_, dup, fork, wait
from mock import O_RDWR # @@@
from printf import printf


argv = "sh"


def main():
    
    if open_("console", O_RDWR) < 0:
        mknod("console", 1, 1)
        open_("console", O_RDWR)
    
    dup(0) # stdout
    dup(0) # stderr
    
    while True:
        printf(1, "init: starting sh\n")
        pid = fork()
        
        if pid < 0:
            printf(1, "init: fork failed\n")
            exit()
        
        if pid == 0:
            exec_("sh", argv)
            printf(1, "init: exec sh failed\n")
            exit()
        
        while True:
            wpid = wait()
            if wpid < 0 or wpid == pid:
                break
            print(1, "zombie!\n")
