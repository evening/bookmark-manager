# bookmark manager

Django app 


---

Add to bookmarks:
javascript:q=location.href;p=document.title;void(t=open('http://127.0.0.1:8000/autoadd?url='+encodeURIComponent(q)+'&title='+encodeURIComponent(p),'Pinboard','toolbar=no,width=100,height=100'));t.onload=function(){t.close()}