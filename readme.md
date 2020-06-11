# bookmark manager

Clone of [pinboard.in](pinboard.in)

## features

- bookmark websites
- add tags to websites
- filter by tag
- search by name 
- archive websites, search through them
- share bookmarks with others (or put your profile on private)
- shortcuts in browser bookmark tab

---

## bookmark shortcuts

automatically add:
```
javascript:q=location.href;p=document.title;void(t=open('http://127.0.0.1:8000/autoadd?url='+encodeURIComponent(q)+'&title='+encodeURIComponent(p),'bookmark-manager','toolbar=no,width=100,height=100'));t.onload=function(){t.close()}
```

open popup to manually add:
```
javascript:q=location.href;if(document.getSelection){d=document.getSelection();}else{d='';};p=document.title;void(open('http://127.0.0.1:8000/add?url='+encodeURIComponent(q)+'&description='+encodeURIComponent(d)+'&title='+encodeURIComponent(p),'bookmark-manager','toolbar=no,width=700,height=350'));
```
