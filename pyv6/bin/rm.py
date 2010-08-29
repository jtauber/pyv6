from user import exit_, unlink
from printf import printf


def main(argc, argv):
    
    if argc < 2:
        printf(2, "Usage: rm files...\n")
        exit_()
    
    for i in range(1, argc):
        if unlink(argv[i]) < 0:
            printf(2, "rm: %s failed to delete\n", argv[i])
            break
    
    exit_()
