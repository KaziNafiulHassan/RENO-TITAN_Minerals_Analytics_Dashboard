# RENO-TITAN Intelligence Platform

**Critical Minerals Supply Chain Analytics & Visualization**

A comprehensive Streamlit-based analytics platform for analyzing the global supply chain of critical minerals: **Titanium**, **Zirconium**, and **Rare Earth Elements (REE)** from mine production through trade to processing.

---

## 🎯 Project Overview

This application aggregates data from authoritative sources (USGS, BGS, UN Comtrade) to provide:

- **Production Analysis**: Compare mining output trends across USGS and BGS data sources
- **Trade Quality Control**: Detect discrepancies through bilateral trade mirror analysis
- **Geospatial Visualization**: Choropleth maps for production intensity and flow maps for trade routes
- **Material Flow Modeling**: Sankey diagrams showing ore-to-product transformations with mass balance validation

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit |
| **Backend Database** | Supabase (PostgreSQL with PostGIS) |
| **Language** | Python 3.10+ |
| **Visualizations** | Plotly, Folium, Geopandas, Leaflet.js |
| **Data Processing** | Pandas, GeoPandas |

---

## 📊 Core Modules

### 1️⃣ Production Analysis
- Compare production trends from USGS vs BGS
- Identify top 10 producers by year
- Highlight discrepancies (>15%) between sources
- Time series visualization with multiple commodity support

### 2️⃣ Trade QC & Mirror Analysis  
- Bilateral trade flow analysis
- Compare exporter-reported vs partner-reported imports
- Unit value calculations (price per tonne)
- Identify outliers and data quality issues

### 3️⃣ Geospatial Maps
- Choropleth maps: Production intensity by country
- Flow maps: Trade routes with proportional line widths
- Interactive filtering by commodity and year

### 4️⃣ Material Flow (Sankey)
- Ore → Intermediate → Final product transformations
- Mass balance validation (P + I = E + PU + ΔS + L)
- Processing splits visualization
- Country-level domestic capacity modeling

---

## 📁 Project Structure

```
reno-titan-intelligence-platform/
├── data/
│   ├── raw/                    # Source CSV files
│   └── processed/              # Cleaned outputs (optional)
├── etl/
│   ├── config.py               # Supabase credentials, country mapping
│   ├── loaders/
│   │   ├── bgs_production.py
│   │   ├── usgs_production.py
│   │   └── trade_data.py
│   └── run_ingestion.py
├── app/
│   ├── app.py                  # Streamlit home page
│   ├── pages/
│   │   ├── 1_📊_Production_Analysis.py
│   │   ├── 2_🔄_Trade_QC.py
│   │   ├── 3_🗺️_Maps.py
│   │   └── 4_🌊_Material_Flow.py
│   └── utils/
│       ├── database.py         # Query functions
│       ├── visualizations.py   # Plotly/Folium charts
│       └── calculations.py     # Mass balance, unit values
├── .env                        # SUPABASE_URL, SUPABASE_KEY
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Supabase account with created project
- Git

### Installation

1. **Clone repository**
   ```bash
   git clone <repo-url>
   cd reno-titan-intelligence-platform
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

5. **Run ETL pipeline** (first time only)
   ```bash
   python etl/run_ingestion.py
   ```

6. **Launch Streamlit app**
   ```bash
   streamlit run app/app.py
   ```

The app will open at `http://localhost:8501`

---

## 🗄️ Database Schema

### Core Tables

| Table | Purpose |
|-------|---------|
| `countries` | Country reference with ISO3 codes and PostGIS geometries |
| `hs_codes` | HS-6 code reference for trade tracking |
| `production_data` | Annual production from USGS and BGS |
| `trade_data` | Bilateral trade flows with value and quantity |
| `processing_splits` | Material flow coefficients (ore → intermediate → product) |

### Views

| View | Purpose |
|------|---------|
| `mirror_discrepancies` | Bilateral comparison of export vs import reports |
| `top_routes` | Aggregated trade routes ranked by value |

See [database_schema_final.md](database_schema_final.md) for detailed specifications.

---

## 📦 Data Sources

### Current Data (CSV)
- `Titanium Minerals Production Data from USGS.csv`
- `Titanium Minerals Production Data from BGS.csv`
- `Zirconium Production Data from BGS.csv`
- `Rare Earth Minerals Production Data from BGS.csv`
- `Titanium Import & Export_sample_not complete.csv`

### Future APIs (Phase 6+)
- WITS API for recent trade data
- CEPII BACI for cleaned bilateral flows
- USGS Mineral Commodity Summaries

---

## 🔄 Development Roadmap

| Phase | Timeline | Deliverable |
|-------|----------|-------------|
| **1** | Week 1 | Supabase setup, ETL pipeline, project scaffold |
| **2** | Week 2 | Module 1 (Production), Module 2 (Trade QC) |
| **3** | Week 3 | Module 3 (Geospatial Maps) |
| **4** | Week 4 | Module 4 (Material Flow/Sankey) |
| **5** | Week 5 | Polish, testing, deployment |

---

## ✅ Success Criteria

**Must Have**
- ✅ All CSV data loaded and queryable
- ✅ Production module shows top 10 producers + USGS/BGS comparison
- ✅ Trade module identifies mirror discrepancies >10%
- ✅ Maps display production choropleths
- ✅ Sankey diagram for at least one commodity (Titanium)

**Nice to Have**
- ⭐ Automated data refresh from APIs
- ⭐ Flow maps with animated routes
- ⭐ PDF export reports
- ⭐ User authentication for custom views

---

## 📋 Data Quality Standards

- Country names mapped to ISO3 codes (>95% coverage target)
- Quality flags: `Official`, `Estimated`, `Mirror-Derived`
- Uncertainty factors tracked for all calculations
- Zero/negative quantities filtered from unit value analysis
- Outliers identified at >3σ threshold

---

## 🤝 Contributing

1. Create a feature branch from `main`
2. Follow coding conventions in [reno_titan_guide.txt](reno_titan_guide.txt)
3. Test locally with `streamlit run app/app.py`
4. Submit merge request with test results

---

## 📚 Documentation

- [reno_titan_guide.txt](reno_titan_guide.txt) - Implementation guide (comprehensive)
- [database_schema_final.md](database_schema_final.md) - Database design details
- [mass_balance_equation_requirements.md](mass_balance_equation_requirements.md) - Material flow equations

---

## 📧 Support & Feedback

For issues, feature requests, or questions:
1. Check existing documentation in [reno_titan_guide.txt](reno_titan_guide.txt)
2. Open an issue on GitLab with context and reproducible steps

---

## 📄 License

Specify license here (TBD)

---

**Last Updated**: January 2026  
**Project Status**: In Active Development (Phase 1)

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

- [ ] [Create](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
- [ ] [Add files using the command line](https://docs.gitlab.com/topics/git/add_files/#add-files-to-a-git-repository) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://gitlab.h2.de/ingenieuroekologie/reno-titan-intelligence-platform.git
git branch -M main
git push -uf origin main
```

## Integrate with your tools

- [ ] [Set up project integrations](https://gitlab.h2.de/ingenieuroekologie/reno-titan-intelligence-platform/-/settings/integrations)

## Collaborate with your team

- [ ] [Invite team members and collaborators](https://docs.gitlab.com/ee/user/project/members/)
- [ ] [Create a new merge request](https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html)
- [ ] [Automatically close issues from merge requests](https://docs.gitlab.com/ee/user/project/issues/managing_issues.html#closing-issues-automatically)
- [ ] [Enable merge request approvals](https://docs.gitlab.com/ee/user/project/merge_requests/approvals/)
- [ ] [Set auto-merge](https://docs.gitlab.com/user/project/merge_requests/auto_merge/)

## Test and Deploy

Use the built-in continuous integration in GitLab.

- [ ] [Get started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/)
- [ ] [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/ee/user/application_security/sast/)
- [ ] [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/ee/topics/autodevops/requirements.html)
- [ ] [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/ee/user/clusters/agent/)
- [ ] [Set up protected environments](https://docs.gitlab.com/ee/ci/environments/protected_environments.html)

***

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thanks to [makeareadme.com](https://www.makeareadme.com/) for this template.

## Suggestions for a good README

Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name
Choose a self-explaining name for your project.

## Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
