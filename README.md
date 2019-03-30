# Corpus stats project

* __Per tree (node)__
	- [x] weight = number of nodes
	- [x] depth = number of dependency levels
	- [x] MDD = sum(DD = number of nodes linearly separating a governor from its dependent) / (number of nodes - 1)
	- [x] MHD = max(HD = dependency level of a node) / (number of nodes - 1)
    - [x] DD sum
    - [x] HD sum

* __Per relaiton, per tree__
	- [x] frequency (absolute)
	- [x] left/right branching	
	- [x] branching = number of dependents of the node linked (directly) by a relation
	- [x] POS tag of governor/dependent
	- [ ] branch length = branch depth
	- [ ] branch thickness = branch weight

* __Per POS tag, per tree__
	- [ ] frequency (absolute)
	- [ ] left/right branching
	- [ ] branching = number of dependents of the node linked (directly) by a relation
	- [ ] branch length = branch depth
	- [ ] branch thickness = branch weight
