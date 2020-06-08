from typing import List
from website.models import Tag, Post


def clean_tags(s):
    return s.replace(",", " ").split()


def clean_tags_str(s):
    # sorts the words in a string, returns a string
    return " ".join(sorted((s)))


def create_tags(tags: List[str]):
    return list(map(lambda t: Tag.objects.get_or_create(name=t)[0], tags))


def tags_as_strings(p: Post):
    return " ".join(sorted([i.name for i in p.tags.all()]))


def clean_create(s):
    return create_tags(clean_tags(s))
