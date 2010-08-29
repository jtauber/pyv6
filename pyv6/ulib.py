from user import open_, O_RDONLY, fstat, close

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
    n = 0
    while s[n:]:
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

# char*
# gets(char *buf, int max)
# {
#   int i, cc;
#   char c;
# 
#   for(i=0; i+1 < max; ){
#     cc = read(0, &c, 1);
#     if(cc < 1)
#       break;
#     buf[i++] = c;
#     if(c == '\n' || c == '\r')
#       break;
#   }
#   buf[i] = '\0';
#   return buf;
# }

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
