# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a web-based application for automated redesign of business processes using a modeling language-independent approach. The tool uses **activity relations** (adjacency matrix) and **acceptance sequences** (execution paths) to systematically apply behavioral change operations and automatically capture secondary effects.

## Core Architecture

### Three-Step Transformation Pipeline

The application follows a fundamental transformation pattern:

1. **Adjacency Matrix → Acceptance Sequences**: Business process defined by pairwise activity relations is converted to all valid execution traces
2. **Apply Change Operations**: Operations are applied directly to the acceptance sequences (list manipulations)
3. **Acceptance Sequences → Adjacency Matrix**: Modified sequences are converted back to an adjacency matrix, automatically discovering all primary and secondary changes

This workflow is implemented across multiple modules:
- `adjacency_matrix.py`: Defines the `AdjacencyMatrix` class and YAML parsing
- `optimized_acceptance_variants.py`: Generates acceptance sequences with caching, bitwise operations, and backtracking (replaces the older `acceptance_variants.py`)
- `variants_to_matrix.py`: Converts acceptance sequences back to adjacency matrix

### Dependency System

The `dependencies.py` module defines two types of dependencies between activities:

- **Temporal Dependencies** (`TemporalDependency`): Ordering constraints
  - `DIRECT`: Activity must directly follow another (adjacent)
  - `EVENTUAL`: Activity must eventually follow another (not necessarily adjacent)
  - `INDEPENDENCE`: No ordering constraint
  - Direction: `FORWARD`, `BACKWARD`, or `BOTH`

- **Existential Dependencies** (`ExistentialDependency`): Occurrence constraints
  - `IMPLICATION`: If A occurs, B must occur
  - `EQUIVALENCE`: A and B must both occur or both not occur
  - `NEGATED_EQUIVALENCE`: Exactly one of A or B must occur (XOR)
  - `NAND`: A and B cannot both occur
  - `OR`: At least one of A or B must occur
  - `INDEPENDENCE`: No occurrence constraint
  - Direction: `FORWARD`, `BACKWARD`, or `BOTH`

The `constraint_logic.py` module provides helper functions to evaluate these dependencies.

### Change Operations

All change operations are in `change_operations/` and follow a consistent pattern:
1. Generate acceptance variants from the input matrix
2. Apply the operation to the variants (list manipulations)
3. Convert the modified variants back to a matrix
4. Return the new adjacency matrix

**11 Supported Operations:**
- Basic: `insert_operation.py`, `delete_operation.py`, `modify_operation.py`
- Composite: `move_operation.py`, `replace_operation.py`, `parallelize_operation.py`, `collapse_operation.py`, `de_collapse_operation.py`, `swap_operation.py`, `skip_operation.py`, `condition_update.py`

Each operation validates input and checks for violations of locked dependencies using utilities in `utils/`.

### Flask Application

`app.py` is the Flask web server that:
- Serves the UI from `templates/home.html`
- Handles file uploads (YAML process models)
- Applies change operations via POST requests
- Calculates and returns matrix diffs for visualization
- Exports modified matrices as YAML

The frontend (`static/app.js` and `static/site.css`) provides:
- Side-by-side matrix visualization with diff highlighting (green/red/yellow)
- Form-based operation configuration
- Dependency locking interface
- YAML import/export

## Development Commands

### Running the Application
```bash
python run.py
```
Access at `http://127.0.0.1:5000`

### Testing
```bash
# Install test dependencies
pip install -r dev-requirements.txt

# Run all tests
pytest

# Run specific test file
pytest tests/test_insert_operation.py

# Run tests with verbose output
pytest -v

# Run tests matching a pattern
pytest -k "test_delete"
```

### Dependencies
```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (includes production deps)
pip install -r dev-requirements.txt
```

## Key Implementation Details

### Performance Optimizations

The `optimized_acceptance_variants.py` module uses several optimizations for generating acceptance sequences:
- **Caching**: `@lru_cache` decorator for existential constraint validation
- **Bitwise operations**: Activities represented as bitsets for faster subset operations
- **Index mapping**: Activities converted to integer indices for array operations
- **Directed graph logic**: Direct/eventual temporal constraints stored as adjacency lists for early pruning
- **Backtracking**: Early termination when invalid permutations are detected

These optimizations make the tool practical for real-world processes. Use `optimized_acceptance_variants.generate_optimized_acceptance_variants()` instead of the older `acceptance_variants.generate_acceptance_variants()`.

### YAML Format

Process models are defined in YAML with two sections:
- `metadata.activities`: List of all activity names
- `dependencies`: List of pairwise dependencies with `from`, `to`, `temporal`, and `existential` fields

Example files are in `sample-matrices/`.

### Dependency Locking

The `utils/lock_dependencies_violations.py` module checks if operations would violate user-specified "locks" on critical dependencies. If a violation is detected, the operation is aborted. This ensures process integrity.

### Testing Structure

Tests in `tests/` follow naming convention `test_<operation>_operation.py`. Each test file:
- Tests valid operations with various dependency configurations
- Tests invalid inputs and edge cases
- Uses fixtures from `conftest.py` for common test data
- Verifies both the resulting matrix structure and behavior (acceptance sequences)

## Working with Change Operations

When implementing or modifying change operations:
1. Import from `optimized_acceptance_variants` (not `acceptance_variants`)
2. Use `utils/split_dependencies.py` to separate temporal/existential dependencies
3. Use `utils/check_valid_input.py` to validate operation inputs
4. Check for lock violations using `utils/lock_dependencies_violations.py`
5. Follow the generate→modify→convert pattern
6. Raise `ValueError` with clear messages for invalid operations
7. Add comprehensive test coverage in `tests/`
