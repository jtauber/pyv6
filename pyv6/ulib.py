from user import open_, O_RDONLY, fstat, close, read

# #include "types.h"
# #include "stat.h"
# #include "fcntl.h"
# #include "user.h"
# #include "x86.h"
# 
# char*
# strcpy(char *s, char *t)
# {
#   char *os;
# 
#   os = s;
#   while((*s++ = *t++) != 0)
#     ;
#   return os;
# }
# 
# int
# strcmp(const char *p, const char *q)
# {
#   while(*p && *p == *q)
#     p++, q++;
#   return (uchar)*p - (uchar)*q;
# }
# 

def strlen(s):
    s += "\0" # @@@
    n = 0
    while s[n] != "\0":
        n += 1
    return n
    
    # or just return len(s) :-)


# void*
# memset(void *dst, int c, uint n)
# {
#   stosb(dst, c, n);
#   return dst;
# }
# 

def strchr(s, c):
    while s:
        if s[0] == c:
            return s
        s = s[1:]
    return 0


def gets(max_length):
    
    buf = ""
    for i in range(max_length):
        cc, c = read(0, 1)
        if cc < 1:
            break
        buf += c
        if c == "\n" or c == "\r":
            break
    buf += "\0"
    return len(buf), buf


def stat(name):
    fd = open_(name, O_RDONLY)
    if fd < 0:
        return -1
    r, st = fstat(fd)
    close(fd)
    return r, st


def atoi(s):
    s += "\0" # @@@
    n = 0
    while "0" <= s[0] <= "9":
        n = n * 10 + ord(s[0]) - ord("0")
        s = s[1:]
    return n


# 
# void*
# memmove(void *vdst, void *vsrc, int n)
# {
#   char *dst, *src;
#   
#   dst = vdst;
#   src = vsrc;
#   while(n-- > 0)
#     *dst++ = *src++;
#   return vdst;
# }
