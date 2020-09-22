from typing import List
from website.models import Tag, Post
from django.forms.models import model_to_dict
from django.http import Http404, HttpResponse


def clean_tags(s: str) -> List[str]:
    return s.replace(",", " ").split()


def clean_tags_str(s: str) -> str:
    # sorts the words in a string, returns a string
    return " ".join(sorted((s)))


def create_tags(tags: List[str]) -> List[Tag]:
    return list(map(lambda t: Tag.objects.get_or_create(name=t)[0], tags))


def clean_create(s: str):
    return create_tags(clean_tags(s))


def post_to_dict(p: Post):
    ret = model_to_dict(p)
    ret["tags"] = list(map(lambda t: t.name, ret["tags"]))
    ret["snapshot"] = str(ret["snapshot"])
    return ret


def post_or_404(request):
    try:
        return Post.objects.get(id=request.POST.get("id"))
    except Post.DoesNotExist:
        raise Http404
