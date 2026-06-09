# DRM Diagnostic Assessment Tool

A web-based dashboard for evaluating a country's institutional setting for Disaster Risk Management (DRM) across six critical pillars.


## 📋 Features

- **Interactive Assessment Table**: Fill in DRM assessment values across multiple pillars and sub-pillars
- **Visual Analytics**: Automatically generates circular polar charts showing DRM system strengths and gaps
- **Data Export**: Download assessment results as PNG images
- **Reset Functionality**: Clear and restart assessments with confirmation dialogs
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## 🏗️ Project Structure

```
Cat_DDO_DRM_Diagnostic_Dashboard/
├── app.py                      # Main Dash application
├── figure_generator.py         # Chart generation module
├── requirements.txt            # Python dependencies
├── Procfile                    # Render deployment configuration
├── runtime.txt                 # Python version specification
├── .gitignore                  # Git ignore rules
├── assets/
│   ├── css/
│   │   └── app.css            # Custom styling
│   └── images/
│       ├── wb-full-logo.png   # World Bank logo
│       └── gfdrr-logo.png     # GFDRR logo
├── data/
│   └── DRM_system_assessment_template_filled_example.csv
└── scripts/
    └── Example_Summary_Figure_clean.py
```

## 🚀 Local Development

### Prerequisites
- Python 3.11+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/jqnmunozdiaz/Cat_DDO_DRM_Diagnostic_Dashboard.git
cd Cat_DDO_DRM_Diagnostic_Dashboard
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to:
```
http://localhost:8050
```

## 🌐 Deployment on Render

### Step 1: Prepare Your Repository
Ensure all files are committed and pushed to GitHub:
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### Step 2: Create a New Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:

**Settings:**
- **Name**: `drm-diagnostic-tool` (or your preferred name)
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Root Directory**: Leave empty
- **Runtime**: `Python 3`
- **Build Command**: 
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```bash
  gunicorn app:server
  ```
- **Instance Type**: Free (or paid for production)

5. Click **"Create Web Service"**

### Step 3: Environment Variables (if needed)
No environment variables are required for basic deployment.

### Step 4: Deploy
Render will automatically:
- Install dependencies from `requirements.txt`
- Use Python version from `runtime.txt`
- Start the application using the `Procfile` configuration

### Step 5: Access Your App
Once deployed, Render provides a URL like:
```
https://drm-diagnostic-tool.onrender.com
```

## 🔧 Configuration Files

### `requirements.txt`
Lists all Python dependencies with version constraints.

### `Procfile`
Tells Render how to run your application:
```
web: gunicorn app:server
```

### `runtime.txt`
Specifies the Python version:
```
python-3.11.7
```

### `.gitignore`
Excludes unnecessary files from version control.

## 📊 Assessment Pillars

1. **Legal and Institutional DRM Framework**
   - DRM policies and institutions
   - DRM in national and sectoral development plans

2. **Risk Identification**

3. **Risk Reduction**
   - Territorial and urban planning
   - Public investment at the central level
   - Sector-specific risk reduction measures

4. **Preparedness**
   - Early Warning Systems (EWS)
   - Emergency Preparedness & Response (EP&R)
   - Adaptive Social Protection (ASP)

5. **Financial Protection**
   - Fiscal risk management
   - Disaster Risk Financing strategies and instruments

6. **Resilient Reconstruction**

## 🎨 Customization

### Styling
Edit `assets/css/app.css` to customize colors, fonts, and layout.

### Logos
Replace images in `assets/images/` with your organization's logos.

### Assessment Structure
Modify `data/DRM_system_assessment_template_filled_example.csv` to change pillars and sub-pillars.

## 🐛 Troubleshooting

### Local Issues

**Port already in use:**
```bash
# Change port in app.py or kill the process using port 8050
```

**Module not found:**
```bash
pip install -r requirements.txt --upgrade
```

### Render Deployment Issues

**Build fails:**
- Check that `requirements.txt` has correct package names
- Verify `runtime.txt` uses a supported Python version

**Application crashes:**
- Check Render logs in the dashboard
- Ensure `Procfile` uses `gunicorn app:server`

**Static files not loading:**
- Verify `assets/` folder is committed to git
- Check file paths are relative, not absolute

## 📝 License

[Add your license here]

## 👥 Contributors

- World Bank Group
- Global Facility for Disaster Reduction and Recovery (GFDRR)

## 📧 Contact

[Add contact information]

## 🔄 Updates and Maintenance

To update the deployed application:
```bash
git add .
git commit -m "Update description"
git push origin main
```

Render automatically redeploys when changes are pushed to the main branch.

## 🙏 Acknowledgments

This tool was developed to support countries in assessing and strengthening their Disaster Risk Management systems.
