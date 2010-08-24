#include "types.h"
#include "stat.h"
#include "user.h"
#include "fs.h"
#include "fcntl.h"

char buf[2048];
char name[3];
char *echoargv[] = { "echo", "ALL", "TESTS", "PASSED", 0 };
int stdout = 1;

// simple file system tests

void
opentest(void)
{
  int fd;

  printf(stdout, "open test\n");
  fd = open("echo", 0);
  if(fd < 0){
    printf(stdout, "open echo failed!\n");
    exit();
  }
  close(fd);
  fd = open("doesnotexist", 0);
  if(fd >= 0){
    printf(stdout, "open doesnotexist succeeded!\n");
    exit();
  }
  printf(stdout, "open test ok\n");
}

void
writetest(void)
{
  int fd;
  int i;

  printf(stdout, "small file test\n");
  fd = open("small", O_CREATE|O_RDWR);
  if(fd >= 0){
    printf(stdout, "creat small succeeded; ok\n");
  } else {
    printf(stdout, "error: creat small failed!\n");
    exit();
  }
  for(i = 0; i < 100; i++) {
    if(write(fd, "aaaaaaaaaa", 10) != 10) {
      printf(stdout, "error: write aa %d new file failed\n", i);
      exit();
    }
    if(write(fd, "bbbbbbbbbb", 10) != 10) {
      printf(stdout, "error: write bb %d new file failed\n", i);
      exit();
    }
  }
  printf(stdout, "writes ok\n");
  close(fd);
  fd = open("small", O_RDONLY);
  if(fd >= 0){
    printf(stdout, "open small succeeded ok\n");
  } else {
    printf(stdout, "error: open small failed!\n");
    exit();
  }
  i = read(fd, buf, 2000);
  if(i == 2000) {
    printf(stdout, "read succeeded ok\n");
  } else {
    printf(stdout, "read failed\n");
    exit();
  }
  close(fd);

  if(unlink("small") < 0) {
    printf(stdout, "unlink small failed\n");
    exit();
  }
  printf(stdout, "small file test ok\n");
}

void
writetest1(void)
{
  int i, fd, n;

  printf(stdout, "big files test\n");

  fd = open("big", O_CREATE|O_RDWR);
  if(fd < 0){
    printf(stdout, "error: creat big failed!\n");
    exit();
  }

  for(i = 0; i < MAXFILE; i++) {
    ((int*) buf)[0] = i;
    if(write(fd, buf, 512) != 512) {
      printf(stdout, "error: write big file failed\n", i);
      exit();
    }
  }

  close(fd);

  fd = open("big", O_RDONLY);
  if(fd < 0){
    printf(stdout, "error: open big failed!\n");
    exit();
  }

  n = 0;
  for(;;) {
    i = read(fd, buf, 512);
    if(i == 0) {
      if(n == MAXFILE - 1) {
        printf(stdout, "read only %d blocks from big", n);
        exit();
      }
      break;
    } else if(i != 512) {
      printf(stdout, "read failed %d\n", i);
      exit();
    }
    if(((int*)buf)[0] != n) {
      printf(stdout, "read content of block %d is %d\n",
             n, ((int*)buf)[0]);
      exit();
    }
    n++;
  }
  close(fd);
  if(unlink("big") < 0) {
    printf(stdout, "unlink big failed\n");
    exit();
  }
  printf(stdout, "big files ok\n");
}

void
createtest(void)
{
  int i, fd;

  printf(stdout, "many creates, followed by unlink test\n");

  name[0] = 'a';
  name[2] = '\0';
  for(i = 0; i < 52; i++) {
    name[1] = '0' + i;
    fd = open(name, O_CREATE|O_RDWR);
    close(fd);
  }
  name[0] = 'a';
  name[2] = '\0';
  for(i = 0; i < 52; i++) {
    name[1] = '0' + i;
    unlink(name);
  }
  printf(stdout, "many creates, followed by unlink; ok\n");
}

void dirtest(void)
{
  printf(stdout, "mkdir test\n");

  if(mkdir("dir0") < 0) {
    printf(stdout, "mkdir failed\n");
    exit();
  }

  if(chdir("dir0") < 0) {
    printf(stdout, "chdir dir0 failed\n");
    exit();
  }

  if(chdir("..") < 0) {
    printf(stdout, "chdir .. failed\n");
    exit();
  }

  if(unlink("dir0") < 0) {
    printf(stdout, "unlink dir0 failed\n");
    exit();
  }
  printf(stdout, "mkdir test\n");
}

void
exectest(void)
{
  printf(stdout, "exec test\n");
  if(exec("echo", echoargv) < 0) {
    printf(stdout, "exec echo failed\n");
    exit();
  }
}

// simple fork and pipe read/write

void
pipe1(void)
{
  int fds[2], pid;
  int seq, i, n, cc, total;

  if(pipe(fds) != 0){
    printf(1, "pipe() failed\n");
    exit();
  }
  pid = fork();
  seq = 0;
  if(pid == 0){
    close(fds[0]);
    for(n = 0; n < 5; n++){
      for(i = 0; i < 1033; i++)
        buf[i] = seq++;
      if(write(fds[1], buf, 1033) != 1033){
        printf(1, "pipe1 oops 1\n");
        exit();
      }
    }
    exit();
  } else if(pid > 0){
    close(fds[1]);
    total = 0;
    cc = 1;
    while((n = read(fds[0], buf, cc)) > 0){
      for(i = 0; i < n; i++){
        if((buf[i] & 0xff) != (seq++ & 0xff)){
          printf(1, "pipe1 oops 2\n");
          return;
        }
      }
      total += n;
      cc = cc * 2;
      if(cc > sizeof(buf))
        cc = sizeof(buf);
    }
    if(total != 5 * 1033)
      printf(1, "pipe1 oops 3 total %d\n", total);
    close(fds[0]);
    wait();
  } else {
    printf(1, "fork() failed\n");
    exit();
  }
  printf(1, "pipe1 ok\n");
}

// meant to be run w/ at most two CPUs
void
preempt(void)
{
  int pid1, pid2, pid3;
  int pfds[2];

  printf(1, "preempt: ");
  pid1 = fork();
  if(pid1 == 0)
    for(;;)
      ;

  pid2 = fork();
  if(pid2 == 0)
    for(;;)
      ;

  pipe(pfds);
  pid3 = fork();
  if(pid3 == 0){
    close(pfds[0]);
    if(write(pfds[1], "x", 1) != 1)
      printf(1, "preempt write error");
    close(pfds[1]);
    for(;;)
      ;
  }

  close(pfds[1]);
  if(read(pfds[0], buf, sizeof(buf)) != 1){
    printf(1, "preempt read error");
    return;
  }
  close(pfds[0]);
  printf(1, "kill... ");
  kill(pid1);
  kill(pid2);
  kill(pid3);
  printf(1, "wait... ");
  wait();
  wait();
  wait();
  printf(1, "preempt ok\n");
}

// try to find any races between exit and wait
void
exitwait(void)
{
  int i, pid;

  for(i = 0; i < 100; i++){
    pid = fork();
    if(pid < 0){
      printf(1, "fork failed\n");
      return;
    }
    if(pid){
      if(wait() != pid){
        printf(1, "wait wrong pid\n");
        return;
      }
    } else {
      exit();
    }
  }
  printf(1, "exitwait ok\n");
}

void
mem(void)
{
  void *m1, *m2;
  int pid;

  if((pid = fork()) == 0){
    m1 = 0;
    while((m2 = malloc(10001)) != 0) {
      *(char**) m2 = m1;
      m1 = m2;
    }
    while(m1) {
      m2 = *(char**)m1;
      free(m1);
      m1 = m2;
    }
    m1 = malloc(1024*20);
    if(m1 == 0) {
      printf(1, "couldn't allocate mem?!!\n");
      exit();
    }
    free(m1);
    printf(1, "mem ok\n");
    exit();
  } else {
    wait();
  }
}

// More file system tests

// two processes write to the same file descriptor
// is the offset shared? does inode locking work?
void
sharedfd(void)
{
  int fd, pid, i, n, nc, np;
  char buf[10];

  unlink("sharedfd");
  fd = open("sharedfd", O_CREATE|O_RDWR);
  if(fd < 0){
    printf(1, "fstests: cannot open sharedfd for writing");
    return;
  }
  pid = fork();
  memset(buf, pid==0?'c':'p', sizeof(buf));
  for(i = 0; i < 1000; i++){
    if(write(fd, buf, sizeof(buf)) != sizeof(buf)){
      printf(1, "fstests: write sharedfd failed\n");
      break;
    }
  }
  if(pid == 0)
    exit();
  else
    wait();
  close(fd);
  fd = open("sharedfd", 0);
  if(fd < 0){
    printf(1, "fstests: cannot open sharedfd for reading\n");
    return;
  }
  nc = np = 0;
  while((n = read(fd, buf, sizeof(buf))) > 0){
    for(i = 0; i < sizeof(buf); i++){
      if(buf[i] == 'c')
        nc++;
      if(buf[i] == 'p')
        np++;
    }
  }
  close(fd);
  unlink("sharedfd");
  if(nc == 10000 && np == 10000)
    printf(1, "sharedfd ok\n");
  else
    printf(1, "sharedfd oops %d %d\n", nc, np);
}

// two processes write two different files at the same
// time, to test block allocation.
void
twofiles(void)
{
  int fd, pid, i, j, n, total;
  char *fname;

  printf(1, "twofiles test\n");

  unlink("f1");
  unlink("f2");

  pid = fork();
  if(pid < 0){
    printf(1, "fork failed\n");
    return;
  }

  fname = pid ? "f1" : "f2";
  fd = open(fname, O_CREATE | O_RDWR);
  if(fd < 0){
    printf(1, "create failed\n");
    exit();
  }

  memset(buf, pid?'p':'c', 512);
  for(i = 0; i < 12; i++){
    if((n = write(fd, buf, 500)) != 500){
      printf(1, "write failed %d\n", n);
      exit();
    }
  }
  close(fd);
  if(pid)
    wait();
  else
    exit();

  for(i = 0; i < 2; i++){
    fd = open(i?"f1":"f2", 0);
    total = 0;
    while((n = read(fd, buf, sizeof(buf))) > 0){
      for(j = 0; j < n; j++){
        if(buf[j] != (i?'p':'c')){
          printf(1, "wrong char\n");
          exit();
        }
      }
      total += n;
    }
    close(fd);
    if(total != 12*500){
      printf(1, "wrong length %d\n", total);
      exit();
    }
  }

  unlink("f1");
  unlink("f2");

  printf(1, "twofiles ok\n");
}

// two processes create and delete different files in same directory
void
createdelete(void)
{
  enum { N = 20 };
  int pid, i, fd;
  char name[32];

  printf(1, "createdelete test\n");
  pid = fork();
  if(pid < 0){
    printf(1, "fork failed\n");
    exit();
  }

  name[0] = pid ? 'p' : 'c';
  name[2] = '\0';
  for(i = 0; i < N; i++){
    name[1] = '0' + i;
    fd = open(name, O_CREATE | O_RDWR);
    if(fd < 0){
      printf(1, "create failed\n");
      exit();
    }
    close(fd);
    if(i > 0 && (i % 2 ) == 0){
      name[1] = '0' + (i / 2);
      if(unlink(name) < 0){
        printf(1, "unlink failed\n");
        exit();
      }
    }
  }

  if(pid==0)
    exit();
  else
    wait();

  for(i = 0; i < N; i++){
    name[0] = 'p';
    name[1] = '0' + i;
    fd = open(name, 0);
    if((i == 0 || i >= N/2) && fd < 0){
      printf(1, "oops createdelete %s didn't exist\n", name);
      exit();
    } else if((i >= 1 && i < N/2) && fd >= 0){
      printf(1, "oops createdelete %s did exist\n", name);
      exit();
    }
    if(fd >= 0)
      close(fd);

    name[0] = 'c';
    name[1] = '0' + i;
    fd = open(name, 0);
    if((i == 0 || i >= N/2) && fd < 0){
      printf(1, "oops createdelete %s didn't exist\n", name);
      exit();
    } else if((i >= 1 && i < N/2) && fd >= 0){
      printf(1, "oops createdelete %s did exist\n", name);
      exit();
    }
    if(fd >= 0)
      close(fd);
  }

  for(i = 0; i < N; i++){
    name[0] = 'p';
    name[1] = '0' + i;
    unlink(name);
    name[0] = 'c';
    unlink(name);
  }

  printf(1, "createdelete ok\n");
}

// can I unlink a file and still read it?
void
unlinkread(void)
{
  int fd, fd1;

  printf(1, "unlinkread test\n");
  fd = open("unlinkread", O_CREATE | O_RDWR);
  if(fd < 0){
    printf(1, "create unlinkread failed\n");
    exit();
  }
  write(fd, "hello", 5);
  close(fd);

  fd = open("unlinkread", O_RDWR);
  if(fd < 0){
    printf(1, "open unlinkread failed\n");
    exit();
  }
  if(unlink("unlinkread") != 0){
    printf(1, "unlink unlinkread failed\n");
    exit();
  }

  fd1 = open("unlinkread", O_CREATE | O_RDWR);
  write(fd1, "yyy", 3);
  close(fd1);

  if(read(fd, buf, sizeof(buf)) != 5){
    printf(1, "unlinkread read failed");
    exit();
  }
  if(buf[0] != 'h'){
    printf(1, "unlinkread wrong data\n");
    exit();
  }
  if(write(fd, buf, 10) != 10){
    printf(1, "unlinkread write failed\n");
    exit();
  }
  close(fd);
  unlink("unlinkread");
  printf(1, "unlinkread ok\n");
}

void
linktest(void)
{
  int fd;

  printf(1, "linktest\n");

  unlink("lf1");
  unlink("lf2");

  fd = open("lf1", O_CREATE|O_RDWR);
  if(fd < 0){
    printf(1, "create lf1 failed\n");
    exit();
  }
  if(write(fd, "hello", 5) != 5){
    printf(1, "write lf1 failed\n");
    exit();
  }
  close(fd);

  if(link("lf1", "lf2") < 0){
    printf(1, "link lf1 lf2 failed\n");
    exit();
  }
  unlink("lf1");

  if(open("lf1", 0) >= 0){
    printf(1, "unlinked lf1 but it is still there!\n");
    exit();
  }

  fd = open("lf2", 0);
  if(fd < 0){
    printf(1, "open lf2 failed\n");
    exit();
  }
  if(read(fd, buf, sizeof(buf)) != 5){
    printf(1, "read lf2 failed\n");
    exit();
  }
  close(fd);

  if(link("lf2", "lf2") >= 0){
    printf(1, "link lf2 lf2 succeeded! oops\n");
    exit();
  }

  unlink("lf2");
  if(link("lf2", "lf1") >= 0){
    printf(1, "link non-existant succeeded! oops\n");
    exit();
  }

  if(link(".", "lf1") >= 0){
    printf(1, "link . lf1 succeeded! oops\n");
    exit();
  }

  printf(1, "linktest ok\n");
}

// test concurrent create and unlink of the same file
void
concreate(void)
{
  char file[3];
  int i, pid, n, fd;
  char fa[40];
  struct {
    ushort inum;
    char name[14];
  } de;

  printf(1, "concreate test\n");
  file[0] = 'C';
  file[2] = '\0';
  for(i = 0; i < 40; i++){
    file[1] = '0' + i;
    unlink(file);
    pid = fork();
    if(pid && (i % 3) == 1){
      link("C0", file);
    } else if(pid == 0 && (i % 5) == 1){
      link("C0", file);
    } else {
      fd = open(file, O_CREATE | O_RDWR);
      if(fd < 0){
        printf(1, "concreate create %s failed\n", file);
        exit();
      }
      close(fd);
    }
    if(pid == 0)
      exit();
    else
      wait();
  }

  memset(fa, 0, sizeof(fa));
  fd = open(".", 0);
  n = 0;
  while(read(fd, &de, sizeof(de)) > 0){
    if(de.inum == 0)
      continue;
    if(de.name[0] == 'C' && de.name[2] == '\0'){
      i = de.name[1] - '0';
      if(i < 0 || i >= sizeof(fa)){
        printf(1, "concreate weird file %s\n", de.name);
        exit();
      }
      if(fa[i]){
        printf(1, "concreate duplicate file %s\n", de.name);
        exit();
      }
      fa[i] = 1;
      n++;
    }
  }
  close(fd);

  if(n != 40){
    printf(1, "concreate not enough files in directory listing\n");
    exit();
  }

  for(i = 0; i < 40; i++){
    file[1] = '0' + i;
    pid = fork();
    if(pid < 0){
      printf(1, "fork failed\n");
      exit();
    }
    if(((i % 3) == 0 && pid == 0) ||
       ((i % 3) == 1 && pid != 0)){
      fd = open(file, 0);
      close(fd);
    } else {
      unlink(file);
    }
    if(pid == 0)
      exit();
    else
      wait();
  }

  printf(1, "concreate ok\n");
}

// directory that uses indirect blocks
void
bigdir(void)
{
  int i, fd;
  char name[10];

  printf(1, "bigdir test\n");
  unlink("bd");

  fd = open("bd", O_CREATE);
  if(fd < 0){
    printf(1, "bigdir create failed\n");
    exit();
  }
  close(fd);

  for(i = 0; i < 500; i++){
    name[0] = 'x';
    name[1] = '0' + (i / 64);
    name[2] = '0' + (i % 64);
    name[3] = '\0';
    if(link("bd", name) != 0){
      printf(1, "bigdir link failed\n");
      exit();
    }
  }

  unlink("bd");
  for(i = 0; i < 500; i++){
    name[0] = 'x';
    name[1] = '0' + (i / 64);
    name[2] = '0' + (i % 64);
    name[3] = '\0';
    if(unlink(name) != 0){
      printf(1, "bigdir unlink failed");
      exit();
    }
  }

  printf(1, "bigdir ok\n");
}

void
subdir(void)
{
  int fd, cc;

  printf(1, "subdir test\n");

  unlink("ff");
  if(mkdir("dd") != 0){
    printf(1, "subdir mkdir dd failed\n");
    exit();
  }

  fd = open("dd/ff", O_CREATE | O_RDWR);
  if(fd < 0){
    printf(1, "create dd/ff failed\n");
    exit();
  }
  write(fd, "ff", 2);
  close(fd);
  
  if(unlink("dd") >= 0){
    printf(1, "unlink dd (non-empty dir) succeeded!\n");
    exit();
  }

  if(mkdir("/dd/dd") != 0){
    printf(1, "subdir mkdir dd/dd failed\n");
    exit();
  }

  fd = open("dd/dd/ff", O_CREATE | O_RDWR);
  if(fd < 0){
    printf(1, "create dd/dd/ff failed\n");
    exit();
  }
  write(fd, "FF", 2);
  close(fd);

  fd = open("dd/dd/../ff", 0);
  if(fd < 0){
    printf(1, "open dd/dd/../ff failed\n");
    exit();
  }
  cc = read(fd, buf, sizeof(buf));
  if(cc != 2 || buf[0] != 'f'){
    printf(1, "dd/dd/../ff wrong content\n");
    exit();
  }
  close(fd);

  if(link("dd/dd/ff", "dd/dd/ffff") != 0){
    printf(1, "link dd/dd/ff dd/dd/ffff failed\n");
    exit();
  }

  if(unlink("dd/dd/ff") != 0){
    printf(1, "unlink dd/dd/ff failed\n");
    exit();
  }
  if(open("dd/dd/ff", O_RDONLY) >= 0){
    printf(1, "open (unlinked) dd/dd/ff succeeded\n");
    exit();
  }

  if(chdir("dd") != 0){
    printf(1, "chdir dd failed\n");
    exit();
  }
  if(chdir("dd/../../dd") != 0){
    printf(1, "chdir dd/../../dd failed\n");
    exit();
  }
  if(chdir("dd/../../../dd") != 0){
    printf(1, "chdir dd/../../dd failed\n");
    exit();
  }
  if(chdir("./..") != 0){
    printf(1, "chdir ./.. failed\n");
    exit();
  }

  fd = open("dd/dd/ffff", 0);
  if(fd < 0){
    printf(1, "open dd/dd/ffff failed\n");
    exit();
  }
  if(read(fd, buf, sizeof(buf)) != 2){
    printf(1, "read dd/dd/ffff wrong len\n");
    exit();
  }
  close(fd);

  if(open("dd/dd/ff", O_RDONLY) >= 0){
    printf(1, "open (unlinked) dd/dd/ff succeeded!\n");
    exit();
  }

  if(open("dd/ff/ff", O_CREATE|O_RDWR) >= 0){
    printf(1, "create dd/ff/ff succeeded!\n");
    exit();
  }
  if(open("dd/xx/ff", O_CREATE|O_RDWR) >= 0){
    printf(1, "create dd/xx/ff succeeded!\n");
    exit();
  }
  if(open("dd", O_CREATE) >= 0){
    printf(1, "create dd succeeded!\n");
    exit();
  }
  if(open("dd", O_RDWR) >= 0){
    printf(1, "open dd rdwr succeeded!\n");
    exit();
  }
  if(open("dd", O_WRONLY) >= 0){
    printf(1, "open dd wronly succeeded!\n");
    exit();
  }
  if(link("dd/ff/ff", "dd/dd/xx") == 0){
    printf(1, "link dd/ff/ff dd/dd/xx succeeded!\n");
    exit();
  }
  if(link("dd/xx/ff", "dd/dd/xx") == 0){
    printf(1, "link dd/xx/ff dd/dd/xx succeeded!\n");
    exit();
  }
  if(link("dd/ff", "dd/dd/ffff") == 0){
    printf(1, "link dd/ff dd/dd/ffff succeeded!\n");
    exit();
  }
  if(mkdir("dd/ff/ff") == 0){
    printf(1, "mkdir dd/ff/ff succeeded!\n");
    exit();
  }
  if(mkdir("dd/xx/ff") == 0){
    printf(1, "mkdir dd/xx/ff succeeded!\n");
    exit();
  }
  if(mkdir("dd/dd/ffff") == 0){
    printf(1, "mkdir dd/dd/ffff succeeded!\n");
    exit();
  }
  if(unlink("dd/xx/ff") == 0){
    printf(1, "unlink dd/xx/ff succeeded!\n");
    exit();
  }
  if(unlink("dd/ff/ff") == 0){
    printf(1, "unlink dd/ff/ff succeeded!\n");
    exit();
  }
  if(chdir("dd/ff") == 0){
    printf(1, "chdir dd/ff succeeded!\n");
    exit();
  }
  if(chdir("dd/xx") == 0){
    printf(1, "chdir dd/xx succeeded!\n");
    exit();
  }

  if(unlink("dd/dd/ffff") != 0){
    printf(1, "unlink dd/dd/ff failed\n");
    exit();
  }
  if(unlink("dd/ff") != 0){
    printf(1, "unlink dd/ff failed\n");
    exit();
  }
  if(unlink("dd") == 0){
    printf(1, "unlink non-empty dd succeeded!\n");
    exit();
  }
  if(unlink("dd/dd") < 0){
    printf(1, "unlink dd/dd failed\n");
    exit();
  }
  if(unlink("dd") < 0){
    printf(1, "unlink dd failed\n");
    exit();
  }

  printf(1, "subdir ok\n");
}

void
bigfile(void)
{
  int fd, i, total, cc;

  printf(1, "bigfile test\n");

  unlink("bigfile");
  fd = open("bigfile", O_CREATE | O_RDWR);
  if(fd < 0){
    printf(1, "cannot create bigfile");
    exit();
  }
  for(i = 0; i < 20; i++){
    memset(buf, i, 600);
    if(write(fd, buf, 600) != 600){
      printf(1, "write bigfile failed\n");
      exit();
    }
  }
  close(fd);

  fd = open("bigfile", 0);
  if(fd < 0){
    printf(1, "cannot open bigfile\n");
    exit();
  }
  total = 0;
  for(i = 0; ; i++){
    cc = read(fd, buf, 300);
    if(cc < 0){
      printf(1, "read bigfile failed\n");
      exit();
    }
    if(cc == 0)
      break;
    if(cc != 300){
      printf(1, "short read bigfile\n");
      exit();
    }
    if(buf[0] != i/2 || buf[299] != i/2){
      printf(1, "read bigfile wrong data\n");
      exit();
    }
    total += cc;
  }
  close(fd);
  if(total != 20*600){
    printf(1, "read bigfile wrong total\n");
    exit();
  }
  unlink("bigfile");

  printf(1, "bigfile test ok\n");
}

void
fourteen(void)
{
  int fd;

  // DIRSIZ is 14.
  printf(1, "fourteen test\n");

  if(mkdir("12345678901234") != 0){
    printf(1, "mkdir 12345678901234 failed\n");
    exit();
  }
  if(mkdir("12345678901234/123456789012345") != 0){
    printf(1, "mkdir 12345678901234/123456789012345 failed\n");
    exit();
  }
  fd = open("123456789012345/123456789012345/123456789012345", O_CREATE);
  if(fd < 0){
    printf(1, "create 123456789012345/123456789012345/123456789012345 failed\n");
    exit();
  }
  close(fd);
  fd = open("12345678901234/12345678901234/12345678901234", 0);
  if(fd < 0){
    printf(1, "open 12345678901234/12345678901234/12345678901234 failed\n");
    exit();
  }
  close(fd);

  if(mkdir("12345678901234/12345678901234") == 0){
    printf(1, "mkdir 12345678901234/12345678901234 succeeded!\n");
    exit();
  }
  if(mkdir("123456789012345/12345678901234") == 0){
    printf(1, "mkdir 12345678901234/123456789012345 succeeded!\n");
    exit();
  }

  printf(1, "fourteen ok\n");
}

void
rmdot(void)
{
  printf(1, "rmdot test\n");
  if(mkdir("dots") != 0){
    printf(1, "mkdir dots failed\n");
    exit();
  }
  if(chdir("dots") != 0){
    printf(1, "chdir dots failed\n");
    exit();
  }
  if(unlink(".") == 0){
    printf(1, "rm . worked!\n");
    exit();
  }
  if(unlink("..") == 0){
    printf(1, "rm .. worked!\n");
    exit();
  }
  if(chdir("/") != 0){
    printf(1, "chdir / failed\n");
    exit();
  }
  if(unlink("dots/.") == 0){
    printf(1, "unlink dots/. worked!\n");
    exit();
  }
  if(unlink("dots/..") == 0){
    printf(1, "unlink dots/.. worked!\n");
    exit();
  }
  if(unlink("dots") != 0){
    printf(1, "unlink dots failed!\n");
    exit();
  }
  printf(1, "rmdot ok\n");
}

void
dirfile(void)
{
  int fd;

  printf(1, "dir vs file\n");

  fd = open("dirfile", O_CREATE);
  if(fd < 0){
    printf(1, "create dirfile failed\n");
    exit();
  }
  close(fd);
  if(chdir("dirfile") == 0){
    printf(1, "chdir dirfile succeeded!\n");
    exit();
  }
  fd = open("dirfile/xx", 0);
  if(fd >= 0){
    printf(1, "create dirfile/xx succeeded!\n");
    exit();
  }
  fd = open("dirfile/xx", O_CREATE);
  if(fd >= 0){
    printf(1, "create dirfile/xx succeeded!\n");
    exit();
  }
  if(mkdir("dirfile/xx") == 0){
    printf(1, "mkdir dirfile/xx succeeded!\n");
    exit();
  }
  if(unlink("dirfile/xx") == 0){
    printf(1, "unlink dirfile/xx succeeded!\n");
    exit();
  }
  if(link("README", "dirfile/xx") == 0){
    printf(1, "link to dirfile/xx succeeded!\n");
    exit();
  }
  if(unlink("dirfile") != 0){
    printf(1, "unlink dirfile failed!\n");
    exit();
  }

  fd = open(".", O_RDWR);
  if(fd >= 0){
    printf(1, "open . for writing succeeded!\n");
    exit();
  }
  fd = open(".", 0);
  if(write(fd, "x", 1) > 0){
    printf(1, "write . succeeded!\n");
    exit();
  }
  close(fd);

  printf(1, "dir vs file OK\n");
}

// test that iput() is called at the end of _namei()
void
iref(void)
{
  int i, fd;

  printf(1, "empty file name\n");

  // the 50 is NINODE
  for(i = 0; i < 50 + 1; i++){
    if(mkdir("irefd") != 0){
      printf(1, "mkdir irefd failed\n");
      exit();
    }
    if(chdir("irefd") != 0){
      printf(1, "chdir irefd failed\n");
      exit();
    }

    mkdir("");
    link("README", "");
    fd = open("", O_CREATE);
    if(fd >= 0)
      close(fd);
    fd = open("xx", O_CREATE);
    if(fd >= 0)
      close(fd);
    unlink("xx");
  }

  chdir("/");
  printf(1, "empty file name OK\n");
}

// test that fork fails gracefully
// the forktest binary also does this, but it runs out of proc entries first.
// inside the bigger usertests binary, we run out of memory first.
void
forktest(void)
{
  int n, pid;

  printf(1, "fork test\n");

  for(n=0; n<1000; n++){
    pid = fork();
    if(pid < 0)
      break;
    if(pid == 0)
      exit();
  }
  
  if(n == 1000){
    printf(1, "fork claimed to work 1000 times!\n");
    exit();
  }
  
  for(; n > 0; n--){
    if(wait() < 0){
      printf(1, "wait stopped early\n");
      exit();
    }
  }
  
  if(wait() != -1){
    printf(1, "wait got too many\n");
    exit();
  }
  
  printf(1, "fork test OK\n");
}

int
main(int argc, char *argv[])
{
  printf(1, "usertests starting\n");

  if(open("usertests.ran", 0) >= 0){
    printf(1, "already ran user tests -- rebuild fs.img\n");
    exit();
  }
  close(open("usertests.ran", O_CREATE));

  opentest();
  writetest();
  writetest1();
  createtest();

  mem();
  pipe1();
  preempt();
  exitwait();

  rmdot();
  fourteen();
  bigfile();
  subdir();
  concreate();
  linktest();
  unlinkread();
  createdelete();
  twofiles();
  sharedfd();
  dirfile();
  iref();
  forktest();
  bigdir(); // slow

  exectest();

  exit();
}
