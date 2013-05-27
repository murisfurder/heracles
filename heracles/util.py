import os

def get_heracles_path():
    h_path = os.path.abspath(__file__)
    return os.path.dirname(h_path)

SPACER = "    "

def str_tree(tree, indent=0):
    result = []
    for item in tree:
        result.append(SPACER * indent + "- label:'%s' value:'%s'" % (item.label, 
                item.value))
        result.extend(str_tree(item.children, indent+1))
    if indent == 0:
        return "\n".join(result)
    else:
        return result

def check_int(value):
    try:
        int(value)
        return True
    except:
        return False
