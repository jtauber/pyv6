from user import fork, sleep, exit_


# Create a zombie process that
# must be reparented at exit.


def main(argc, argv):
    
    if fork() > 0:
        sleep(5)  # Let child exit before parent
    
    exit_()
