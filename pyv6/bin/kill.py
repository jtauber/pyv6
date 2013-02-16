from user import exit_, kill
from ulib import atoi
from printf import printf


def main(argc, argv):
    
    if argc < 2:  # @@@ C source has < 1
        printf(2, "usage: kill pid...\n")
        exit_()
    
    for i in range(1, argc):
        kill(atoi(argv[i]))
    
    exit_()
