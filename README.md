# Business Process Redesign Tool

Automated support for redesigning business process behavior with a modern web interface.

## Quick Start

### Prerequisites
- Python 3.10+
- Virtual environment (recommended)

### Installation & Setup

1. **Clone and navigate to the project:**
   ```bash
   cd business-process-redesign
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python run.py
   ```

5. **Open your browser to:**
   ```
   http://127.0.0.1:5000
   ```

## Features

### Fully Implemented - TODO: Check
- **Process Trace Analysis** - Analyze execution traces to discover dependencies
- **Dependency Matrix Generation** - Visualize temporal and existential relationships
- **Activity Deletion** - Remove activities while preserving dependencies
- **Interactive Threshold Controls** - Adjust temporal/existential thresholds
- **Real-time Visualization** - Dynamic matrix and dependency displays

### UI Placeholders (Backend Ready)
Features marked with red asterisk (*) have UI but need backend integration to my understanding (Mihail):
- Matrix Export (YAML/JSON)
- Acceptance Variants Generation
- Process Redesign Strategies
- Insert/Move/Swap Operations
- Performance Metrics & Charts
- Operation Preview & Undo

## Web Interface Guide - TO BE CONTINUED

### 1. Trace Analysis Tab
- **Input traces:** One per line, activities separated by commas
- **Adjust thresholds:** Use sliders for temporal/existential analysis
- **Load sample data:** Quick start with example traces
- **View results:** Discovered dependencies with detailed explanations

### 2. Dependency Matrix Tab
- **Generate matrix:** Create adjacency matrix from analyzed traces
- **Display options:** Toggle temporal/existential dependencies
- **Matrix visualization:** Clean tabular display of relationships
- **Dependency details:** Explanations for each discovered relationship

### 3. Process Redesign Tab
- **Configure redesign:** Set target activities and strategies
- **Generate variants:** Create alternative process designs
- **Compare variants:** Performance metrics and constraint analysis
- **Recommendation scoring:** AI-driven process improvement suggestions

### 4. Change Operations Tab
- **Delete operations:** Remove activities from process models
- **Operation history:** Track all applied modifications
- **Impact analysis:** Before/after matrix comparisons
- **Preservation options:** Control dependency handling

## API Endpoints

The web interface uses these REST API endpoints:

- `POST /api/analyze-traces` - Analyze process traces
- `POST /api/generate-matrix` - Generate dependency matrix
- `POST /api/delete-activity` - Delete activity from matrix
- `GET /api/matrix-status` - Get current matrix status

### Example API Usage

```bash
# Analyze traces
curl -X POST http://127.0.0.1:5000/api/analyze-traces \
  -H "Content-Type: application/json" \
  -d '{"traces": [["A","B","C"], ["A","C","B"]], "temporal_threshold": 1.0, "existential_threshold": 1.0}'

# Generate matrix
curl -X POST http://127.0.0.1:5000/api/generate-matrix \
  -H "Content-Type: application/json" \
  -d '{"traces": [["A","B","C"], ["A","C","B"]], "temporal_threshold": 1.0, "existential_threshold": 1.0}'

# Delete activity
curl -X POST http://127.0.0.1:5000/api/delete-activity \
  -H "Content-Type: application/json" \
  -d '{"activity": "B", "preserve_incoming": true, "preserve_outgoing": true}'
```

## Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

## Project Structure

```
business-process-redesign/
├── app.py                    # Flask web application
├── run.py                    # Application launcher
├── traces_to_matrix.py       # Core trace analysis algorithm
├── adjacency_matrix.py       # Matrix data structure
├── dependencies.py           # Dependency type definitions
├── constraint_logic.py       # Logic evaluation functions
├── acceptance_variants.py    # Process variant generation
├── change_operations/        # Process modification operations
│   └── delete_operation.py   # Activity deletion logic
├── templates/               # HTML templates
│   ├── base.html           # Base template
│   └── home.html           # Main interface
├── static/                 # Static assets
│   ├── site.css           # Stylesheet
│   └── app.js             # JavaScript functionality
├── tests/                  # Test suite
└── sample-matrices/        # Example data
```

## UI Design

- **Modern design** with professional color scheme, Following [TUM](https://gist.github.com/lnksz/51e3566af2df5c7aa678cd4dfc8305f7)
- **Responsive design** for desktop mainly
- **Interactive elements** with hover effects and animations
- **Clear visual hierarchy** with cards, tabs, and sections
- **Status indicators** for success, warning, and error states
- **Loading animations** for better user experience

## Algorithm Details


## License

See LICENSE file for details.

---

**Ready to redesign your business processes?**

Start the application with `python run.py` and open http://127.0.0.1:5000 in your browser!


### Mihail: This readme was written with the help of *AI Assistant*. Given was structure, content & formatting filled by AI