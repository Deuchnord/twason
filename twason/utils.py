#!/usr/bin/env python3


def parse_tags(tags_str: str) -> {str: str}:
    tags_list = []
    for tag in tags_str.split(";"):
        tags_list.append((tag.split("=")))

    return dict(tags_list)
