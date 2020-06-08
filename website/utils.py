from typing import List
from website.models import Tag


def clean_tags(s):
    return s.replace(","," ").split()

def create_tags(tags: List[str]):
    return list(map(lambda t: Tag.objects.get_or_create(name=t)[0],tags))

