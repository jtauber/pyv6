from user import exit_
from printf import printf


def main(argc, argv):
    
    for i in range(1, argc):
        printf(1, "%s%s", argv[i], " " if i + 1 < argc else "\n")
    
    exit_()
