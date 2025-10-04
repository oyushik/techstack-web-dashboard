[English](./README.md) | [한국어](./README.ko.md) | [日本語](./README.ja.md)

---

# 🚀 IT Job Postings Analysis Dashboard

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An interactive dashboard that analyzes and visualizes job posting data collected from major IT recruitment platforms in Korea (Wanted, Jumpit, Rallit). It provides real-time tech stack trend analysis and recommendations for related learning materials.

![Dashboard Preview](data/wordcloud_TECH_STACK.png)

## 📋 Project Overview

- **Development Period**: 2025.04.16 ~ 2025.04.22
- **Team Composition**: 3 members (2 Backend, 1 Frontend)

## 👥 Team Composition & Roles

| Role         | Name         | Responsibilities                                         | GitHub                                |
| ------------ | ------------ | -------------------------------------------------------- | ------------------------------------- |
| **Backend**  | Yushik Oh    | Team Lead, Project Planning, Data Collection & Cleaning  | [oyushik](https://github.com/oyushik) |
| **Backend**  | Woojun Kim   | Data Visualization, Dashboard Integration & Optimization | [Ra1nJun](https://github.com/Ra1nJun) |
| **Frontend** | Minjeong Kim | Web Dashboard Implementation, UI/UX Improvement          | [Mineong](https://github.com/Mineong) |

## ✨ Key Features

- 📊 **Tech Stack Trend Analysis**: Visualize the TOP 20 tech stacks with interactive graphs.
- 🔍 **Job-specific Analysis**: Filter data by job category: All / Backend / Frontend.
- 🎯 **Skill-based Search**: Search for job postings by specific tech stacks or keywords.
- 📺 **Learning Material Recommendations**: Automatically search for YouTube tutorials for a selected technology.
- 💼 **Real-time Job Information**: Display related job postings via Work24 API integration.
- 📈 **Data Visualization**: Dynamic charts and word clouds based on Plotly.

## 🏗️ Project Structure

```
project-data-scraping/
├── src/
│   ├── scrapers/              # Data Collection
│   │   ├── data_utils.py      # Common Utilities
│   │   └── notebooks/         # Scraping Jupyter Notebooks
│   ├── processing/            # Data Preprocessing
│   │   └── csv_merge.py       # CSV Merging and Deduplication
│   ├── visualization/         # Data Visualization
│   │   └── notebooks/         # Visualization Notebooks
│   └── dashboard/             # Streamlit Dashboard
│       ├── app.py             # Main Application
│       ├── charts.py          # Chart Generation
│       ├── data_loader.py     # Data Loading
│       ├── renderer.py        # UI Rendering
│       └── search/            # External API Search
│           ├── youtube.py
│           └── work24.py
├── data/                      # Data Files
├── requirements.txt           # Python Dependencies
└── README.md
```

## 🚦 Getting Started

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Installation

1.  **Clone the repository**

    ```bash
    git clone https://github.com/your-username/project-data-scraping.git
    cd project-data-scraping
    ```

2.  **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Set environment variables** (Optional)

    To use the APIs, create a `.env` file and add your API keys:

    ```bash
    YOUR_YOUTUBE_API_KEY=your_api_key_here
    YOUR_WORK24_API_KEY=your_api_key_here
    ```

### Running the Dashboard

```bash
streamlit run src/dashboard/app.py
```

You can view the dashboard by navigating to `http://localhost:8501` in your browser.

### Allowing External Access (Optional)

```bash
streamlit run src/dashboard/app.py --server.address=0.0.0.0 --server.port=8501
```

## 📊 Data Collection and Processing

### 1. Data Scraping

Collect data from each recruitment platform using Jupyter notebooks:

- `src/scrapers/notebooks/scraping_wanted.ipynb` - Wanted
- `src/scrapers/notebooks/scraping_jumpit.ipynb` - Jumpit
- `src/scrapers/notebooks/scraping_rallit.ipynb` - Rallit

Run each notebook by selecting the job category (`total`, `backend`, `frontend`).

### 2. Data Merging

Merge the collected CSV files and remove duplicates:

```bash
python src/processing/csv_merge.py
```

The merged file is saved in the format `data/merged_data_{category}.csv`.

### 3. Data Visualization

Generate word clouds and other visualizations:

- `src/visualization/notebooks/visualization_wordcloud.ipynb`
- `src/visualization/notebooks/visualization_graph.ipynb`

## 🎯 How to Use Key Features

### Tech Stack Analysis

1.  Select the **"🧩 Tech Stack Analysis"** tab on the dashboard.
2.  Filter job categories with the All/Backend/Frontend buttons.
3.  Click on a bar in the graph to see detailed information for that technology.

### Skill Search

1.  Use the **"Select Main Skill"** dropdown in the sidebar.
2.  Or, enter keywords directly into the **"Keyword Search"** input box.
3.  YouTube tutorials and job postings for the selected skill will be displayed automatically.

### Data Filtering

- **Summary Info**: Shows the number of postings and companies related to the selected keyword.
- **Job Role Analysis**: A chart of the TOP 20 related job roles.
- **Data Table**: A detailed data table with pagination.

## 🔧 Tech Stack

### Data Collection & Processing

- **Python 3.9+**: Main language
- **Pandas**: Data processing and analysis
- **Requests**: HTTP requests

### Dashboard

- **Streamlit**: Web application framework
- **Plotly**: Interactive chart creation

### External APIs

- **YouTube Data API v3**: Tutorial search
- **Work24 API**: Job information retrieval

## 📝 Data Structure

### CSV File Format

The collected data includes the following columns:

| Column Name | Description                            |
| ----------- | -------------------------------------- |
| `company`   | Company name                           |
| `position`  | Job title/position                     |
| `skill`     | Required tech stacks (comma-separated) |

### Skill Data Cleaning

The `filter_skill_data()` function in `data_utils.py` performs the following tasks:

- Removes Korean characters
- Cleans up special characters (except # and +)
- Removes duplicate skills
- Converts to a normalized format

## 🤝 Contributing

Contributions are always welcome! Please follow these steps:

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📄 License

This project is distributed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## 🔗 References

- [Streamlit Documentation](https://docs.streamlit.io)
- [Plotly Python](https://plotly.com/python/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

## 📮 Contact

If you have any questions or suggestions about the project, please create an Issue.

---
