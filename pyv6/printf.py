from user import write


# static
def putc(fd, c):
    write(fd, c, 1)


# static
def printint(fd, xx, base, sgn):
    digits = "0123456789ABCDEF"
    
    # coerce char into int
    if isinstance(xx, str):
        xx = ord(xx)
    
    buf = [None] * 16
    
    neg = False
    if sgn and xx < 0:
        neg = True
        x = -xx
    else:
        x = xx
    
    i = 0
    
    while True:
        buf[i] = digits[x % base]
        i += 1
        x = x / base
        if x == 0:
            break
    
    if neg:
        buf[i] = "-"
        i += 1
    
    while True:
        i -= 1
        if i < 0:
            break
        putc(fd, buf[i])


# Print to the given fd. Only understands %d, %x, %p, %s.
def printf(fd, fmt, *ap):
    
    state = 0
    
    for c in fmt:
        if state == 0:
            if c == "%":
                state = "%"
            else:
                putc(fd, c)
        elif state == "%":
            if c == "d":
                printint(fd, ap[0], 10, 1)
                ap = ap[1:]
            elif c == "x" or c == "p":
                printint(fd, ap[0], 16, 0)
                ap = ap[1:]
            elif c == "s":
                s = ap[0]
                ap = ap[1:]
                if s == "" or s == "\0" or s is None:
                    s = "(null)"
                while s != "":
                    putc(fd, s[0])
                    s = s[1:]
            elif c == "c":
                putc(fd, ap[0])
                ap = ap[1:]
            elif c == "%":
                putc(fd, c)
            else:
                # Unknown % sequence.  Print it to draw attention.
                putc(fd, "%")
                putc(fd, c)
            state = 0
