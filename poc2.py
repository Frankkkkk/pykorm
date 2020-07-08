#!/usr/bin/env python3
# frank.villaro@infomaniak.com - DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE, etc.


pp = Pykorm()

class Node(pp.Base):
    pass


n = Node()
n.query.all()

# vim: set ts=4 sw=4 et:

