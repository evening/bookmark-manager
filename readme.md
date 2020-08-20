# bookmark manager

Clone of [pinboard.in](http://pinboard.in) (which may be a clone of Delicious?)

![subpage](docs/img/demo.gif)

## features

- bookmark websites
- add tags to websites
- filter by tag, search
- archive websites
- share bookmarks with others (or put your profile on private)
- shortcuts in browser bookmark tab

---

## installation

- install [monolith](https://github.com/Y2Z/monolith)
- `conda env create -f environment.yml`
- `python manage.py runserver`

---

## bookmark shortcuts

automatically add:
```
javascript:q=location.href;p=document.title;void(t=open('http://127.0.0.1:8000/autoadd?url='+encodeURIComponent(q)+'&title='+encodeURIComponent(p),'bookmark-manager','toolbar=no,width=100,height=100'))
```

open popup to manually add:
```
javascript:q=location.href;if(document.getSelection){d=document.getSelection();}else{d='';};p=document.title;void(open('http://127.0.0.1:8000/add?url='+encodeURIComponent(q)+'&title='+encodeURIComponent(p)+'&close_after=1','bookmark-manager','toolbar=no,width=700,height=350'));
```
