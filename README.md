# Evaluating DRM Policy Frameworks: A DRM Policy Diagnostic Tool

A web-based dashboard for evaluating a country's institutional and policy setting for Disaster Risk Management (DRM) across six critical pillars.

---

## 📋 Features

- **Interactive Assessment**: Copy-paste structured diagnostic data to instantly visualize results.
- **Visual Analytics**: Generates circular polar (petal) charts showing DRM system strengths and gaps.
- **Data Export**: Easily download high-quality assessment charts as PNG images.
- **Clean Responsive UI**: Designed with bootstrap for seamless mobile and desktop use.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+

### Installation & Run

1. Clone the repository and navigate to the project directory:
   ```bash
   git clone https://github.com/jqnmunozdiaz/Cat_DDO_DRM_Diagnostic_Dashboard.git
   cd Cat_DDO_DRM_Diagnostic_Dashboard
   ```

2. Set up a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   # Activate:
   # Windows: venv\Scripts\activate | macOS/Linux: source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   python app.py
   ```
   Open [http://localhost:8050](http://localhost:8050) in your browser.

---

## 🌐 Deployment (Render)

Render automatically deploys when you push changes to your GitHub repository.

- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:server`

---

## 🏗️ Project Structure

- `app.py`: Main entry point for the Dash application.
- `layouts/`: Contains UI layout sections (header, input, results).
- `callbacks/`: Handles user interactions, data parsing, and image download triggers.
- `config/`: Contains the question mappings and country lists.
- `data/`: Holds the offline diagnostic spreadsheet template (`DRM Rapid Screening Tool - Questionnaire.xlsx`).
- `LLM/`: JSON files containing response pattern narrative summaries.

---

## 📊 Assessment Pillars

1. **Legal and Institutional DRM Framework**: DRM policies, institutions, and development plan integration.
2. **Risk Identification**: Geospatial and hazard risk data management.
3. **Risk Reduction**: Urban planning, central public investments, and sector-specific design standards.
4. **Preparedness**: Early warning systems, emergency response protocols, and adaptive social protection.
5. **Financial Protection**: Fiscal risk management, sovereign risk finance strategies, and catastrophe insurance.
6. **Resilient Reconstruction**: Post-disaster recovery planning and build-back-better zoning.

---

## 👥 Contributors & Support

- Developed by the **World Bank Group** and the **Global Facility for Disaster Reduction and Recovery (GFDRR)**.
