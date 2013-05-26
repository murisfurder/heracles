import os

def get_heracles_path():
    h_path = os.path.abspath(__file__)
    return os.path.dirname(h_path)

SPACER = "    "

def print_tree(tree, indent=0):
    for item in tree:
        print SPACER * indent + "- label:'%s' value:'%s'" % (item.label, 
                item.value)
        print_tree(item.children, indent+1)

def check_int(value):
    try:
        int(value)
        return True
    except:
        return False
