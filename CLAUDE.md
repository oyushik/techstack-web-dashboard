# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an IT job posting analysis dashboard that scrapes job data from Korean IT job boards (Wanted, Jumpit, Rallit), processes and visualizes technology stack trends, and provides related educational resources. The project combines data scraping, data processing, and an interactive Streamlit dashboard.

## Setup

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Running the Application

### Main Dashboard
```bash
streamlit run src/dashboard/app.py
```

### Data Collection Notebooks
The project uses Jupyter notebooks for scraping data from different job boards:
- `src/scrapers/notebooks/scraping_wanted.ipynb` - Scrapes Wanted job postings
- `src/scrapers/notebooks/scraping_jumpit.ipynb` - Scrapes Jumpit job postings
- `src/scrapers/notebooks/scraping_rallit.ipynb` - Scrapes Rallit job postings

Each notebook follows the same pattern:
1. Import utilities from `src.scrapers.data_utils`
2. Set job category (`"total"`, `"backend"`, or `"frontend"`)
3. Configure scraping with `DEFAULT_HEADERS` from `data_utils`
4. Save results to CSV using `save_data_to_csv()`

### Data Processing
```bash
python src/processing/csv_merge.py  # Merges CSV files and removes duplicates
```

### Visualization Notebooks
- `src/visualization/notebooks/visualization_graph.ipynb` - Creates data visualizations
- `src/visualization/notebooks/visualization_wordcloud.ipynb` - Generates wordcloud

## Architecture

### Data Flow
1. **Scraping** → Notebooks collect job data and save to `data/data_{source}_{category}.csv`
2. **Merging** → `src/processing/csv_merge.py` combines files into `data/merged_data_{category}.csv`
3. **Dashboard** → Streamlit app loads merged CSVs and renders interactive visualizations

### Project Structure
```
project-data-scraping/
├── src/
│   ├── scrapers/              # 스크래핑 관련
│   │   ├── data_utils.py      # 공통 유틸리티
│   │   └── notebooks/         # 스크래핑 노트북
│   ├── processing/            # 데이터 처리
│   │   └── csv_merge.py
│   ├── visualization/         # 시각화 관련
│   │   └── notebooks/
│   └── dashboard/             # Streamlit 대시보드
│       ├── app.py
│       ├── charts.py
│       ├── data_loader.py
│       ├── renderer.py
│       └── search/
│           ├── youtube.py
│           └── work24.py
├── data/                      # 데이터 파일
├── requirements.txt           # Python 의존성
├── README.md
└── CLAUDE.md
```

### Core Modules

**src/dashboard/app.py** - Application entry point
- Orchestrates page setup, data loading, filtering, and rendering
- Delegates to specialized render functions in `renderer.py`

**src/scrapers/data_utils.py** - Shared data utilities
- `filter_skill_data()` - Normalizes skill strings (removes Korean, special chars, duplicates)
- `save_data_to_csv()` / `load_data_from_csv()` - CSV persistence with error handling
- `DEFAULT_HEADERS` - Common request headers for scraping

**src/dashboard/data_loader.py** - Data loading and filtering
- `load_all_data()` - Loads all CSV files with Streamlit caching (`@st.cache_data`)
- `filter_data()` - Filters by search term and selected skill
- `count_skills()` - Counts skill frequencies, excludes generic terms (AI, UI, API, etc.)

**src/dashboard/renderer.py** - UI rendering logic
- Manages session state for user interactions (chart clicks, sidebar selections)
- `get_active_selection()` - Priority: graph clicks > sidebar skill > search term
- `handle_chart_click()` - Processes Plotly chart clicks, updates `st.session_state.clicked_skills`
- `render_skill_analysis()` - Shows top 20 skills with animated bar charts
- `render_job_analysis()` - Shows top 20 positions with normalized job titles
- `render_related_information()` - Displays Work24 jobs and YouTube tutorials for selected skill

**src/dashboard/charts.py** - Plotly chart generation
- `create_animated_bar_chart()` - Creates animated bar charts (vertical/horizontal)
- 7-frame animation using `go.Frame`, supports both orientations

**src/dashboard/search/youtube.py** - YouTube API integration
- Searches YouTube for tutorial videos based on selected skill
- Requires API key from `.env` file

**src/dashboard/search/work24.py** - Work24 job board API integration
- Fetches real job postings from Korean government employment API
- Displays results in a table format

**src/processing/csv_merge.py** - CSV file merging
- Merges data from multiple sources (Wanted, Jumpit, Rallit)
- Removes duplicates based on specified columns
- Outputs merged files for total, backend, and frontend categories

### State Management

Session state keys:
- `render_id` - Forces re-renders when incremented
- `skill_chart_type` - Current chart type (`"total"`, `"backend"`, `"frontend"`)
- `clicked_skills` - List of skills clicked in graphs (single selection)
- `sb_selected_skill` - Sidebar dropdown selection
- `sb_search_term` - Sidebar text input

Priority for active selection (in `get_active_selection()`):
1. Graph clicks (`clicked_skills`)
2. Sidebar skill selection (`sb_selected_skill` != "직접 입력")
3. Sidebar search term (`sb_search_term`)

### Data Structure

CSV columns:
- `position` - Job title/position
- `skill` - Comma-separated list of skills
- `company` - Company name
- Additional columns vary by source

## Key Implementation Details

### Skill Filtering Logic
`filter_skill_data()` performs aggressive cleaning:
1. Remove Korean characters
2. Remove line separators (`\n`, `\u2028`)
3. Keep only letters, `#`, `+`, and spaces
4. Remove standalone numbers (keep version numbers like "Vue3")
5. Deduplicate and join with commas

### Chart Interaction Flow
1. User clicks chart bar → `plotly_events` captures click
2. `handle_chart_click()` updates `clicked_skills` in session state
3. Increments `render_id` and calls `st.rerun()`
4. `render_related_information()` uses `get_active_selection()` to show relevant content

### Callback Pattern
Sidebar widgets use `on_change` callbacks to manage state priority:
- `sb_selectbox_on_change()` - Clears `clicked_skills` when dropdown changes
- `sb_text_input_on_change()` - Clears both `clicked_skills` and resets dropdown to "직접 입력"

This ensures the most recent user action takes precedence without conflicting state updates.

### Data Caching
`load_csv_data()` uses `@st.cache_data(ttl=3600)` to cache CSV files for 1 hour, improving performance by avoiding repeated disk reads.
