# Corpora stats project

* __Per tree (node)__ :white_check_mark:
	- [x] weight = number of nodes
	- [x] depth = number of dependency levels
	- [x] MDD = sum(DD = number of nodes linearly separating a governor from its dependent) / (number of nodes - 1)
	- [x] MHD = max(HD = dependency level of a node) / (number of nodes - 1)
    - [x] DD sum
    - [x] HD sum

* __Per relaiton, per tree__
	- [x] count
	- [x] left/right branching count
	- [x] branching pattern counts = number of dependents of the node linked (directly) by a relation
	- [x] POS tag of governor/dependent pattern counts
	- [ ] branch length = branch depth
	- [ ] branch thickness = branch weight

* __Per POS tag, per tree__
	- [x] count
	- [x] left/right branching count
	- [x] branching pattern counts = number of dependents of the node linked (directly) by a relation
	- [ ] branch length = branch depth
	- [ ] branch thickness = branch weight

* __Per corpus__ :bangbang:
	- [ ] mean weight
	- [ ] mean depth
	- [ ] MDD
	- [ ] HDD
	- [ ] relative frequency of a relation
	- [ ] relative frequency of a POS tag
	- [ ] left/right branching preference of a corpus (=root)
	- [ ] left/right branching preference of a relation
	- [ ] left/right branching preference of a POS tag
	- [ ] branching pattern distribution per relation
	- [ ] branching pattern distribution per POS tag
	- [ ] POS tag of governor/dependent pattern distribution per relation
	- [ ] mean branch length per relation
	- [ ] mean branch length per POS tag
	- [ ] mean branch thickness per relation
	- [ ] mean branch thickness per POS tag
	- [ ] coverage of a relation = the proportion of all sentences containing the relation

