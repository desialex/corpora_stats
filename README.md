# Corpora stats project

### __Tree stats__ :deciduous_tree:

* __Per node__ :
	- [x] weight = number of nodes
	- [x] depth = number of dependency levels
	- [x] MDD = sum(DD = number of nodes linearly separating a governor from its dependent) / (number of nodes - 1)
	- [x] MHD = max(HD = dependency level of a node) / (number of nodes - 1)
	- [x] DD sum
	- [x] HD sum

* __Per relaiton, per tree__
	- [x] count
	- [x] left/right branch count
	- [x] branch pattern counts = number of dependents of the node linked (directly) by the relation
	- [x] POS tag of governor/dependent pattern counts
	- [ ] branch length = branch depth
	- [ ] branch thickness = branch weight

* __Per POS tag, per tree__
	- [x] count
	- [x] left/right branch count
	- [x] branch pattern counts = number of dependents of the node with that POS tag
	- [ ] branch length = branch depth
	- [ ] branch thickness = branch weight

### __Corpus stats__ :ledger:

* __Global__	
	- [x] mean weight
	- [x] mean depth
	- [x] MDD
	- [x] HDD

	*Pos_rel_pos distribution stats*
	- [x] mean = all the numbers in the set / the amount of numbers in the set
	- [x] median = the middle point of the number set
	- [x] variance = measures dispersion within the data set
	- [x] standard deviation = measures spread around the mean
	- [x] range = the difference between the 75th and 25th percentile of the data (similar to _std_ but more robust against outliers)
	- [x] skew = horizontal position of the tail 
	- [x] kurtosis = vertical position of the tail 
	- [x] entropy = degree of randomness (diversity)
	- [x] anova = comparison of two distributions

* __Per POS / rel__

	*Counts*
	- [x] relative frequency of a pos = pos count / all pos counts

	*Branch counts*
	- [x] relative number of branch patterns = branch patterns / all branch patterns
	- [x] proportion of branches to the left of the node = left / all branches
	- [x] proportion of branches to the right of the node = right / all branches

* __Per POS / rel__

	*Branch distribution stats*
	- [x] mean = all the numbers in the set / the amount of numbers in the set
	- [x] median = the middle point of the number set
	- [x] variance = measures dispersion within the data set
	- [x] standard deviation = measures spread around the mean
	- [x] range = the difference between the 75th and 25th percentile of the data (similar to _std_ but more robust against outliers)
	- [x] skew = horizontal position of the tail 
	- [x] kurtosis = vertical position of the tail 
	- [x] entropy = degree of randomness (diversity)
	- [x] anova = comparison of two distributions

* __Per rel__

	*Pos_pairs distribution stats*
	- [x] mean = all the numbers in the set / the amount of numbers in the set
	- [x] median = the middle point of the number set
	- [x] variance = measures dispersion within the data set
	- [x] standard deviation = measures spread around the mean
	- [x] range = the difference between the 75th and 25th percentile of the data (similar to _std_ but more robust against outliers)
	- [x] skew = horizontal position of the tail 
	- [x] kurtosis = vertical position of the tail 
	- [x] entropy = degree of randomness (diversity)
	- [x] anova = comparison of two distributions

* __Misc__
	- [ ] mean branch length per relation
	- [ ] mean branch length per POS tag
	- [ ] mean branch thickness per relation
	- [ ] mean branch thickness per POS tag
	- [ ] coverage of a relation = the proportion of all sentences containing the relation

