from user import exit_, mkdir
from printf import printf


def main(argc, argv):
    
    if argc < 2:
        printf(2, "Usage: mkdir files...\n")
        exit_()
    
    for i in range(1, argc):
        if mkdir(argv[i]) < 0:
            printf(2, "mkdir: %s failed to create\n", argv[i])
            break
    
    exit_()
