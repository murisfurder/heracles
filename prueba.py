from heracles import Heracles

class P(object):
    def __init__(self):
        print "entro"

    def __del__(self):
        print "salgo"

p = P()

h = Heracles() 
l=h.get_lens_by_path('/etc/sudoers') 
text = file('/tmp/sudoers').read()
t = l.get(text)
del t
