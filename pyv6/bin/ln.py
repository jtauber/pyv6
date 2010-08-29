from user import exit_, link
from printf import printf


def main(argc, argv):
    
    if argc != 3:
        printf(2, "Usage: ln old new\n")
        exit_()
    
    if link(argv[1], argv[2]) < 0:
        printf(2, "link %s %s: failed\n", argv[1], argv[2])
    
    exit_()
