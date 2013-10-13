#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    import numpy as np
    zeros = np.zeros
except ImportError:
    def py_zeros(dim, pytype):
        assert len(dim) == 2
        return [[pytype() for y in xrange(dim[1])]
                for x in xrange(dim[0])]
    zeros = py_zeros
from zss.compare import AnnotatedTree
from zss.simple_tree import Node, NodeTreesGenerator

get_children = Node.get_children
get_label = Node.get_label

INSERT = "insert"
REMOVE = "remove"
UPDATE = "update"

class EditPathGenerator(object):
    def __init__(self, A, B):
        A, B = AnnotatedTree(A, get_children), AnnotatedTree(B, get_children)
        self.A = A
        self.Al = A.lmds
        self.An = A.nodes
        self.B = B
        self.Bl = B.lmds
        self.Bn = B.nodes
        self.forest_dists = None
        self.tree_dists = None
        self.sx, self.sy = len(A.nodes), len(B.nodes)

    def remove_cost(self, node):
        return 1

    def insert_cost(self, node):
        return 1

    def update_cost(self, Anode, Bnode):
        return 0 if get_label(Anode) == get_label(Bnode) else 1

    def get_tree_edits(self):
        if self.forest_dists is None or self.tree_dists is None:
            self.update_matrices()
        sx, sy = self.tree_dists.shape
        return [ edit for edit in self.get_subtree_edits(sx-1, sy-1) ]

    def get_tree_dist(self):
        if self.forest_dists is None or self.tree_dists is None:
            self.update_matrices()
        return self.tree_dists[-1, -1]

    def update_matrices(self):
        self.forest_dists = {}
        self.tree_dists = zeros((self.sx, self.sy), int)
        for i in self.A.keyroots:
            for j in self.B.keyroots:
                self.update_tree_dist(i,j)

    def update_tree_dist(self, i, j):
        #import pdb; pdb.set_trace()
        m = i - self.Al[i] + 2
        n = j - self.Bl[j] + 2
        fd = zeros((m,n), int)
        self.forest_dists[(i,j)] = fd

        ioff = self.Al[i] - 1
        joff = self.Bl[j] - 1

        for x in xrange(1, m): # δ(l(i1)..i, θ) = δ(l(1i)..1-1, θ) + γ(v → λ)
            fd[x][0] = fd[x-1][0] + self.remove_cost(self.An[x-1])
        for y in xrange(1, n): # δ(θ, l(j1)..j) = δ(θ, l(j1)..j-1) + γ(λ → w)
            fd[0][y] = fd[0][y-1] + self.insert_cost(self.Bn[y-1])

        for x in xrange(1, m): ## the plus one is for the xrange impl
            for y in xrange(1, n):
                # only need to check if x is an ancestor of i
                # and y is an ancestor of j
                if self.Al[i] == self.Al[x+ioff] and self.Bl[j] == self.Bl[y+joff]:
                    #                   +-
                    #                   | δ(l(i1)..i-1, l(j1)..j) + γ(v → λ)
                    # δ(F1 , F2 ) = min-+ δ(l(i1)..i , l(j1)..j-1) + γ(λ → w)
                    #                   | δ(l(i1)..i-1, l(j1)..j-1) + γ(v → w)
                    #                   +-
                    fd[x][y] = min(
                        fd[x-1][y] + self.remove_cost(self.An[x+ioff]),
                        fd[x][y-1] + self.insert_cost(self.Bn[y+joff]),
                        fd[x-1][y-1] + self.update_cost(self.An[x+ioff], self.Bn[y+joff]),
                    )
                    self.tree_dists[x+ioff][y+joff] = fd[x][y]
                else:
                    #                   +-
                    #                   | δ(l(i1)..i-1, l(j1)..j) + γ(v → λ)
                    # δ(F1 , F2 ) = min-+ δ(l(i1)..i , l(j1)..j-1) + γ(λ → w)
                    #                   | δ(l(i1)..l(i)-1, l(j1)..l(j)-1)
                    #                   |                     + treedist(i1,j1)
                    #                   +-
                    p = self.Al[x+ioff]-1-ioff
                    q = self.Bl[y+joff]-1-joff
                    #print (p, q), (len(fd), len(fd[0]))
                    fd[x][y] = min(
                        fd[x-1][y] + self.remove_cost(self.An[x+ioff]),
                        fd[x][y-1] + self.insert_cost(self.Bn[y+joff]),
                        fd[p][q] + self.tree_dists[x+ioff][y+joff]
                    )

    def get_subtree_edits(self,i,j):
        fds = self.forest_dists[(i,j)]
        ioff = self.Al[i] - 1
        joff = self.Bl[j] - 1
        x, y = map(lambda x:x-1, fds.shape)
        while x > 0 or y > 0:
            #import pdb; pdb.set_trace()
            if x == 0:
                yield (INSERT, None, self.Bn[joff + y])
                y -= 1
            elif y == 0:
                yield (REMOVE, self.An[ioff + x], None)
                x -= 1
            elif self.Al[i] == self.Al[x+ioff] and self.Bl[j] == self.Bl[y+joff]:
                a11, a10, a01 = fds[x-1][y-1], fds[x-1][y], fds[x][y-1]
                m = min(a11, a01, a10)
                if a11 == m:
                    if fds[x][y] > fds[x-1][y-1]:
                        yield (UPDATE, self.An[ioff + x], self.Bn[joff + y])
                    x -= 1
                    y -= 1
                elif a10 == m:
                    if fds[x][y] > fds[x-1][y]:
                        yield (REMOVE, self.An[ioff + x], None)
                    x -= 1
                else:
                    if fds[x][y] > fds[x][y-1]:
                        yield (INSERT, None, self.Bn[joff + y])
                    y -= 1
            else:
                vx, vy = x-1 , y-1
                a11, a10, a01 = fds[vx][vy], fds[vx][y], fds[x][vy]
                m = min(a11, a01, a10)
                if a11 == m:
                    p = self.Al[x+ioff] - 1 - ioff
                    q = self.Bl[y+joff] - 1 - joff
                    if fds[x][y] > fds[p][q]:
                        for e in self.get_subtree_edits(x+ioff, y+joff):
                            yield e
                    x = p  
                    y = q 
                elif a10 == m:
                    if fds[x][y] > fds[x-1][y]:
                        yield (REMOVE, self.An[ioff + x], None)
                    x -= 1
                else:
                    if fds[x][y] > fds[x][y-1]:
                        yield (INSERT, None, self.Bn[joff + y])
                    y -= 1
                
def get_edit_path_generator_from_set_tree(original, set_tree):
    e = None
    for n_tree in NodeTreesGenerator(set_tree):
        edit = EditPathGenerator(original, n_tree)
        if e is None:
            n = edit.get_tree_dist()
            e = edit
        else:
            v = edit.get_tree_dist()
            if v < n:
                n = v
                e = edit
    return e
