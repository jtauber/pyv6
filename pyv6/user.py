# commented out due to circular import
# from printf import printf

from mock import mock_open, mock_read, mock_write, mock_close, mock_fstat, mock_unlink, mock_exec, mock_exit, mock_fork, mock_wait
from mock import O_RDONLY, O_RDWR, O_WRONLY, O_CREATE
from mock import T_FILE, T_DIR


# system call stubs

# int fork(void);
def fork(func, *argv):
    return mock_fork(func, *argv)

# int exit(void) __attribute__((noreturn));
def exit_(status=0):
    return mock_exit()

# int wait(void);
def wait():
    return mock_wait()

# int pipe(int*);
def pipe(p): return -1 # @@@

# int write(int, void*, int);
def write(fd, buf, length):
    return mock_write(fd, buf, length) # @@@

# int read(int, void*, int);
def read(fd, max_size):
    return mock_read(fd, max_size) # @@@

# int close(int);
def close(fd):
    return mock_close(fd) # @@@

# int kill(int);
def kill(n): pass

# int exec(char*, char**);
def exec_(path, argv):
    return mock_exec(path, argv)

# int open(char*, int);
def open_(filename, mode):
    return mock_open(filename, mode) # @@@

# int mknod(char*, short, short);

# int unlink(char*);
def unlink(path):
    return mock_unlink(path) # @@@

# int fstat(int fd, struct stat*);
def fstat(fd):
    return mock_fstat(fd) # @@@

# int link(char*, char*);
def link(old, new): pass

# int mkdir(char*);
def mkdir(path): return 1 # @@@

# int chdir(char*)
def chdir(path): pass

# int dup(int);
def dup(i): pass # @@@

# int getpid();
# char* sbrk(int);

# int sleep(int);
def sleep(n): pass
