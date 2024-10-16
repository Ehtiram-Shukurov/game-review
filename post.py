
def build_hierarchy(replies, parent_id=None):
    hierarchy = []
    for reply in replies:
        if reply['parent_id'] == int(parent_id):
            reply['replies'] = build_hierarchy(replies, reply['post_id'])
            hierarchy.append(reply)
    return hierarchy
