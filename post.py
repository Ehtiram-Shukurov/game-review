
def build_hierarchy(replies, parent_id=None):
    hierarchy = []
    for reply in replies:
        if reply['parent_id'] == int(parent_id):
    
            reply_structure = {
                'post_id': reply['post_id'],
                'parent_id': reply['parent_id'],
                'author': reply['username'], 
                'sub': reply['user_sub'],
                'content': reply['content'],
                'replies': build_hierarchy(replies, reply['post_id']) 
            }
            hierarchy.append(reply_structure)
    return hierarchy
