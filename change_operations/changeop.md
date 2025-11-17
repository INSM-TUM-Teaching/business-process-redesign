# Fix for Modify Change Operation Implementation

## Context
This fix addresses the implementation of the "Modify Change Operation" in the business process redesign repository. The modify operation allows putting a set of new dependencies as input, including both existential and temporal modifications.

## Problem Statement
The current implementation has issues with handling directional modifications and ensuring that contradictions are properly detected when modifications cannot be implemented. In the new fixed implementation there should be no direction modifications for temporal dependencies.

## Algorithm to Implement

### Input
- Original dependency matrix
- Set of modifications (tuples to be modified)

### Processing Steps

1. **Create Modified Matrix**
   - (A) Convert all defined direct temporal dependencies to eventual ones
   - (B) Overwrite tuples that should be modified with the provided modifications
   - (C) Save the modified matrix

2. **Generate Powerset P(A) for Each Modified Activity**
   - For each activity that has been modified, generate its powerset

3. **Validate Subsets Against Existential Dependencies**
   - Get all valid subsets of P(A) by checking for each subset if existential dependencies of the modified matrix are satisfied
   - If for a subset existential dependencies hold → add to valid subsets
   - Else → continue with next subset

4. **Create Permutations**
   - Create permutations for each valid subset
   - **Error Case:** If there is no valid subset → return error stating that there are (existential) contradictions. For proper modification, more than the provided modifications are required
   - **Success Case:** If there is a valid subset → create permutations

5. **Check Against Temporal Dependencies**
   - For each permutation, check against temporal dependencies of modified matrix
   - If temporal dependencies hold → add permutation to valid permutations
   - If temporal dependencies do not hold → continue; skip permutation

6. **Rediscover Resulting Matrix**
   - Rediscover resulting matrix based on acceptance sequences
   - **Error Case:** If accepted sequences == ∅ → return same error/contradiction message as above in step 4
   - **Success Case:** If there are accepted sequences → discover matrix (changed matrix) from these sequences

7. **Compare and Identify Changes**
   - Compare original matrix and discovered/changed matrix
   - Identify which cells have changed

## Implementation Requirements

### Output Validation
- If a changed matrix is generated, the tuples in the modification set should be exactly the ones that appear as changed in the comparison

## Test Cases to Implement

### Test Case 1: Single Consequence with Possible Implementation
**Description:** Test case with 1 consequence + possible implementation

**Input Matrix:**
```
    a    b     c        d
a   x  (<d,<=) (<d,<=) (<,<=>)
b       x  (-, NAND)   (<d, =>)
c           x   (<d, =>)
d               x
```

**Operation:** Modify (a,d) = (<,<=)
Note: only existential dependency is modified

**Expected Process:**

1. **Create modified matrix**
    a    b     c        d
a   x  (<,<=) (<,<=) (<,<=)
b       x  (-, NAND)   (<, =>)
c           x   (<, =>)
d               x
```

2. **Get P(A) for {c}:**
   - {a}, {b}, {c}, {d}
   - {a,b}, {a,c}, {a,d}, {b,c}, {b,d}, {c,d}
   - {a,b,c}, {a,b,d}, {a,c,d}, {b,c,d}
   - {a,b,c,d}

3. **Get all valid subsets of P(A) for existential constraints:**
   - {a}
   - {a,b}
   - {a,b,d}
   - {a,c,d}

4. **Check with temporal dependencies:**
   Permutations to check:
(a)  yes
(a,d)  yes
(d,a)  no

(a,b,d)  yes
(a,d,b) no
(d,a,b)  no
(d,b,a)  no
(b,a,d) no
(b,d,a) no
(a,c,d) yes
(a,d,c) no
(c,a,d) no
(c,d,a) no

5. **Rediscover matrix:**
   Valid accepted sequences should produce a matrix where:
```
    a    b     c        d
a   x  (<d,<=) (<d,<=) (<,<=) <- only change
b       x  (-, NAND)   (<d, =>)
c           x   (<d, =>)
d               x
```

6. **Compare with original matrix**
   - Only (a,d) should show as changed

### Test Case 2: 2 consequences + possible implementation

**Input Matrix:**
```
    a    b     c        d
a   x  (<d,<=) (<d,<=) (<,<=>)
b       x  (-, <=/=>)   (<d, =>)
c           x   (<d, =>)
d               x
```

**Operation:** Modify (c,d) = (-, V)

1. modified matrix
2 + 3. powerset + check existential dependencies
4. permutations + temporal dependencies
test case 2 is wrong
Because the modified matrix does not allow for {c}
Because c implies a
So at the end we have the very same matrix

### Test Case 3: testcase that does not work and requires further modification tuples
```
    a    b     c        d
a   x  (<d,<=>) (<,<=>) (<,<=>)
b       x  (<d, <=>)   (<, <=>)
c           x   (<d,<=>)
d               x
```

**Operation:** Modify (b,c) = (-, <=/=>)

1. modified watrix
```
    a    b     c        d
a   x  (<,<=>) (<,<=>) (<,<=>)
b       x  (-,<=/=>)   (<, <=>)
c           x   (<,<=>)
d               x
```
2 + 3. powerset + check existential dependencies
after this step we have an empty matrix -> contradiction! change operation cannot be implemented. set of modifications required.

### Test Case 4: testcase with 4 consequences + possible implementation
```
    a    b     c        d
a   x  (<d,<=) (<d,<=) (<,<=>)
b       x  (-,NAND)   (<d, =>)
c           x   (<d,=>)
d               x
```

**Operation:** Modify (b,c) = (<d, <=>)

1. modified watrix
```
    a    b     c        d
a   x  (<,<=) (<,<=) (<,<=>)
b       x  (<d, <=>)   (<, =>)
c           x   (<d,=>)
d               x
```

2. {a,d}
{a,b,c,d}

3. check with temporal
(a,d) yes
(d,a) no
(a,b,c,d) yes
(a,b,d,c) no
(a,d,b,c) no
(d,a,b,c) no
(b,a,c,d) no
(b,c,a,d) no
(b,c,d,a) no
(c,b,d,a) no
(c,d,b,a) no
(c,d,a,b) no
(a,c,b,d) no
(a,c,d,b) no
(a,d,c,b) no
(b,a,d,c) no
(b,c,d,a) no
(b,d...

result:
```
    a    b     c        d
a   x  (<d,<=) (<,<=) (<,<=>)
b       x  (<d, <=>)   (<, =>)
c           x   (<,=>)
d               x
```

highlighted:
(a,c) temporal
(b,c) temporal and existential
(b,d) temporal
(c,d) temporal