O_RDONLY  = 0x000
O_WRONLY  = 0x001
O_RDWR    = 0x002
O_CREATE  = 0x200

T_DIR  = 1   # Directory
T_FILE = 2   # File
T_DEV  = 3   # Special device



import sys


class File(object):
    def __init__(self, contents):
        self.contents = contents
        self.type = T_FILE
        self.dev = 1
        self.ino = 123
        self.nlink = 0
    
    @property
    def size(self):
        return len(self.contents)


class Dir(object):
    def __init__(self, contents):
        self.type = T_DIR
        self.dev = 1
        self.ino = 234
        self.nlink = 0
        self.contents = contents
    
    @property
    def size(self):
        return len(self.contents)


class MockFileSystem:
    
    def __init__(self):
        self.files = {}
        self.files["/foo"] = File("contents of foo!\n")
        self.files["/biz"] = Dir("123456alpha         987654beta          ")
        self.files["/biz/alpha"] = File("contents of alpha!\n")
        self.files["/biz/beta"] = File("contents of beta!\n")
        self.fds = {}
    
    def open(self, path, mode):
        if path not in self.files:
            return -1
        next_fd = len(self.fds) + 3
        self.fds[next_fd] = (path, mode, 0, self.files[path])
        return next_fd
    
    def read(self, fd, max_size):
        if fd == 0:
            buf = sys.stdin.read(max_size)
            return len(buf), buf
        elif fd == 1:
            sys.stdout.write(buf[:length])
        elif fd == 2:
            assert False
        else:
            path, mode, ptr, f = self.fds[fd]
            if ptr >= len(f.contents):
                return 0, "" # EOF
            end = min(len(f.contents), ptr + max_size)
            buf = f.contents[ptr:end]
            self.fds[fd] = (path, mode, end, f)
            return len(buf), buf
    
    def write(self, fd, buf, length):
        if fd == 0:
            assert False
        elif fd == 1:
            sys.stdout.write(buf[:length])
        elif fd == 2:
            sys.stderr.write(buf[:length])
        else:
            assert False
    
    def close(self, fd):
        del self.fds[fd]
    
    def fstat(self, fd):
        class Stat: pass
        path, mode, ptr, f = self.fds[fd]
        s = Stat()
        s.type = f.type     # Type of file
        s.dev = f.dev       # Device number
        s.ino = f.ino       # Inode number on device
        s.nlink = f.nlink   # Number of links to file
        s.size = f.size     # Size of file in bytes
        return 0, s
        
MockFS = MockFileSystem()

def mock_open(path, mode):
    return MockFS.open(path, mode)

def mock_read(fd, max_size):
    return MockFS.read(fd, max_size)

def mock_write(fd, buf, length):
    return MockFS.write(fd, buf, length)

def mock_close(fd):
    return MockFS.close(fd)

def mock_fstat(fd):
    return MockFS.fstat(fd)
