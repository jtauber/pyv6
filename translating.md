Translating C to Python
=======================

Just some notes on how I've gone about translating various C idioms into
Python. At the moment I'm mostly focused on a working, literal translation.
Making the Python more idiomatic will be done in a second pass.


Obviously something like:
    
    void
    cat(int fd)
    {

just becomes:
    
    def cat(fd):


At the moment, I'm quite literally translating things like:
    
    int
    main(int argc, char *argv[])
    {

as:
    
    def main(argc, argv):

although I could, of course, replace any reference to argc with len(argv) in
the function body. This will be done in a second-pass translation.


A for loop like:
    
    for(i = 1; i < argc; i++){
      ...

gets translated quite conveniently as:
    
    for i in range(1, argc):
        ...


An if with an assignment, like:
    
    if((fd = open(argv[i], 0)) < 0){
      ...

is translated as:
    
    # if((fd = open(argv[i], 0)) < 0)
    fd = open_(argv[i], 0)
    if fd < 0:
        ...

A while with an assignment, like:
    
    while((n = foo()) > 0)
      ...

becomes:
    
    # while((n = foo()) > 0)
    while True:
        n = foo()
        if n <= 0:
            break
        ...

A do..while, like:
    
    do{
      buf[i++] = digits[x % base];
    }while((x /= base) != 0);

becomes:
    
    while True:
        buf[i] = digits[x % base]
        i += 1
        x = x / base
        if x == 0: break


I'm thinking something like:
    
    n = read(fd, buf, sizeof(buf))

really needs to be translated into:
    
    n, buf = read(fd, 512)

where 512 is sizeof(buf) in the original code.


An include like:
    
    #include "user.h"

to get the definition of printf becomes:
    
    from user import printf


Something like:
    
    i+1 < argc ? " " : "\n"

becomes:
    
    " " if i + 1 < argc else "\n"


String Pointer Manipulation
---------------------------
    
If:
    
    char *s;

then:
    
    *s

is normally translated:
    
    s[0]

and so:
    
    while('0' <= *s && *s <= '9')
        ...

becomes:
    
    while "0" <= s[0] <= "9":
        ...

Something like
    
    s++

becomes:
    
    s = s[1:]

and any time a character is coerced to its ASCII code, we need to use:
    
    ord(...)

and so, something like:
    
    n = n*10 + *s++ - '0';

becomes:
    
    n = n * 10 + ord(s[0]) - ord("0")
    s = s[1:]


@@@ OPEN QUESTIONS:

- how to translate code that assumes a null-terminated string
