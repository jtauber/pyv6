// Physical memory allocator, intended to allocate
// memory for user processes. Allocates in 4096-byte "pages".
// Free list is kept sorted and combines adjacent pages into
// long runs, to make it easier to allocate big segments.
// One reason the page size is 4k is that the x86 segment size
// granularity is 4k.

#include "types.h"
#include "defs.h"
#include "param.h"
#include "spinlock.h"

struct run {
  struct run *next;
  int len; // bytes
};

struct {
  struct spinlock lock;
  struct run *freelist;
} kmem;

// Initialize free list of physical pages.
// This code cheats by just considering one megabyte of
// pages after end.  Real systems would determine the
// amount of memory available in the system and use it all.
void
kinit(void)
{
  extern char end[];
  uint len;
  char *p;

  initlock(&kmem.lock, "kmem");
  p = (char*)(((uint)end + PAGE) & ~(PAGE-1));
  len = 256*PAGE; // assume computer has 256 pages of RAM, 1 MB
  cprintf("mem = %d\n", len);
  kfree(p, len);
}

// Free the len bytes of memory pointed at by v,
// which normally should have been returned by a
// call to kalloc(len).  (The exception is when
// initializing the allocator; see kinit above.)
void
kfree(char *v, int len)
{
  struct run *r, *rend, **rp, *p, *pend;

  if(len <= 0 || len % PAGE)
    panic("kfree");

  // Fill with junk to catch dangling refs.
  memset(v, 1, len);

  acquire(&kmem.lock);
  p = (struct run*)v;
  pend = (struct run*)(v + len);
  for(rp=&kmem.freelist; (r=*rp) != 0 && r <= pend; rp=&r->next){
    rend = (struct run*)((char*)r + r->len);
    if(r <= p && p < rend)
      panic("freeing free page");
    if(rend == p){  // r before p: expand r to include p
      r->len += len;
      if(r->next && r->next == pend){  // r now next to r->next?
        r->len += r->next->len;
        r->next = r->next->next;
      }
      goto out;
    }
    if(pend == r){  // p before r: expand p to include, replace r
      p->len = len + r->len;
      p->next = r->next;
      *rp = p;
      goto out;
    }
  }
  // Insert p before r in list.
  p->len = len;
  p->next = r;
  *rp = p;

 out:
  release(&kmem.lock);
}

// Allocate n bytes of physical memory.
// Returns a kernel-segment pointer.
// Returns 0 if the memory cannot be allocated.
char*
kalloc(int n)
{
  char *p;
  struct run *r, **rp;

  if(n % PAGE || n <= 0)
    panic("kalloc");

  acquire(&kmem.lock);
  for(rp=&kmem.freelist; (r=*rp) != 0; rp=&r->next){
    if(r->len >= n){
      r->len -= n;
      p = (char*)r + r->len;
      if(r->len == 0)
        *rp = r->next;
      release(&kmem.lock);
      return p;
    }
  }
  release(&kmem.lock);

  cprintf("kalloc: out of memory\n");
  return 0;
}
