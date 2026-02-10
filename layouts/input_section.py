"""
Input section layout - introduction, guidelines, country dropdown, paste area
"""
from dash import dcc, html
import dash_bootstrap_components as dbc

# Country list
COUNTRIES = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda",
    "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain",
    "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan",
    "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria",
    "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada",
    "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros",
    "Congo (Republic of)", "Congo (DRC)", "Costa Rica", "Croatia", "Cuba",
    "Cyprus", "Czech Republic", "Denmark", "Djibouti", "Dominica", "Dominican Republic",
    "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia",
    "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Gambia", "Georgia",
    "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau",
    "Guyana", "Haiti", "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran",
    "Iraq", "Ireland", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan",
    "Kenya", "Kiribati", "Kosovo", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon",
    "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg",
    "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands",
    "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia",
    "Montenegro", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal",
    "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Korea",
    "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Palestine", "Panama",
    "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Qatar",
    "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia",
    "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe",
    "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore",
    "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Korea",
    "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland",
    "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Timor-Leste", "Togo",
    "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu",
    "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States",
    "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam",
    "Yemen", "Zambia", "Zimbabwe"
]

EXAMPLE_DATA = "Q1,Yes,1;Q2,No,1;Q3,No,0.5;Q4,Yes,0.5;Q5,No,1;Q6,Yes,1;Q7,No,1;Q8,Yes,0.5;Q9,Yes,0.5;Q10,Yes,1;Q11,No,1;Q12,No,0.5;Q13,Yes,0.5;Q14,Yes,1;Q15,No,1;Q16,Yes,1;Q17,Yes,1;Q18,No,0.25;Q19,No,0.25;Q20,Yes,0.25;Q21,Yes,0.25;Q22,No,1;Q23,Yes,1;Q24,No,1;Q25,No,1;Q26,No,0.5;Q27,No,0.5;Q28,Yes,1;Q29,Yes,1;Q30,Yes,1;Q31,Yes,1;Q32,No,0.5;Q33,No,0.5;Q34,Yes,1;Q35,Yes,1;Q36,Yes,1;Q37,Yes,1;Q38,Yes,1;Q39,Yes,1;Q40,Yes,0.5;Q41,Yes,0.5;Q42,Yes,1;Q43,Yes,1;Q44,Yes,1;Q45,Yes,1;Q46,No,1;Q47,Yes,1"


def get_input_section():
    """Return the input section with introduction, guidelines, and form"""
    return html.Div([
        # Introduction
        html.Div([
            html.H3("Introduction", className="mb-3"),
            html.P([
                html.Strong("A sound Disaster Risk Management (DRM) policy assessment requires a system-wide perspective. "), 
                "Unlike traditional sectors, DRM cuts across infrastructure sectors, such as energy, water, transport, urban development, as well as socioenvironmental sectors, such as education, health, social protection and environmental management. Disaster risk also affects economic growth, fiscal stability and jobs. In short, disaster risk is a development challenge arising from the interaction of hazard, exposure, and vulnerability. While managing the immediate impacts of disasters is vital, building disaster resilience therefore requires a more comprehensive, multisectoral policy approach."
            ], className="text-muted"),
            html.P([
                html.Strong("Recognizing this, the World Bank DRM framework provides a structured approach to evaluate a country's policy and institutional setup for DRM. "), 
                "Drawing on practical country experiences and global good practices, this framework was first proposed in 'The Sendai Report' (Ghesquiere et al. 2012) and is aligned with the Sendai Framework for Disaster Risk Reduction. It is organized around six essential components of DRM encompassing not only legal and institutional DRM frameworks, but also key policy dimensions related to risk information, risk reduction at the sectoral and territorial level, emergency preparedness and response, financial protection and resilient recovery."
            ], className="text-muted"),
            html.Div([
                html.Img(src="/assets/images/Policy_Framework.png", 
                         style={"maxWidth": "100%", "height": "auto", "display": "block", "margin": "0 auto", "marginBottom": "20px"})
            ], className="text-center mt-3"),
            html.P([
                html.Strong("Building upon this framework, the proposed diagnostic tool enables task teams to conduct a standardized assessment of the maturity of a country's DRM system. The goal is to identify the main policy gaps that may be constraining resilience-building efforts across each DRM pillar.")
            ], className="text-muted"),
        ], className="mb-4"),
        
        # Guidelines section
        html.Div([
            html.H3("Guidelines for Using the Tool", className="mb-3"),
            html.P([
                html.Strong("The tool assesses each DRM pillar using a set of closed questions presented in an Excel-based questionnaire."), 
                " Task teams can download the file for offline completion. To ensure objectivity and speed, teams are asked to provide a \"Yes\" or \"No\" answer. This answer must be based on official documents that justify the existence of a series of legal, regulatory, institutional, and budgetary conditions that are considered fundamental for managing disaster risk."
            ], className="text-muted"),
            html.P([
                "This is a high-level assessment designed to be completed quickly. If information for a question is unavailable, teams are encouraged to consult other Global Practice (GP) colleagues or national counterparts. This is particularly relevant under Pillar 3, where inputs from colleagues in the Water, Transport, Education, Health, and Agriculture GP can greatly help in gathering information. Users can also answer \"Unknown\", in which case the question will be scored as \"No\"."
            ], className="text-muted"),
            html.P([
                "Once all questions are completed, copy/paste the content of the Excel below to generate key metrics and visual outputs."
            ], className="text-muted"),

        ], className="mb-4"),
        
        # Input Form
        html.Div([
            # Country selection dropdown
            dbc.Row([
                dbc.Col([
                    html.Label("Select Country:", className="fw-bold mb-2"),
                    dcc.Dropdown(
                        id="country-dropdown",
                        options=[{"label": country, "value": country} for country in COUNTRIES],
                        value="Angola",
                        placeholder="Select a country...",
                        clearable=False,
                        className="mb-3"
                    )
                ], width=12)
            ], className="mb-3"),
            
            # Download template button
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        [html.I(className="fas fa-download me-2"), "Download Diagnostic Questionnaire"],
                        id="download-template-button",
                        color="primary",
                        className="mb-3 me-2",
                        n_clicks=0
                    ),
                    dcc.Download(id="download-template"),
                    html.A(
                        [html.I(className="fas fa-file-pdf me-2"), "Download Methodological Note"],
                        href="/assets/documents/DRM Policy Tool - Methodological Note.pdf",
                        download="DRM Policy Tool - Methodological Note.pdf",
                        className="btn btn-primary mb-3"
                    ),
                ], width=12)
            ]),
            
            # Paste area
            html.Div([
                html.Label("Please paste the data from cell B10 of your spreadsheet after completing the diagnostic:", className="form-label fw-semibold"),
                dcc.Textarea(id="paste-input", placeholder="",
                            style={"width": "100%", "height": "110px", "fontFamily": "monospace"}),
                html.Div([
                    dbc.Button("See Results", id="paste-apply", color="primary", className="mt-2 me-2"),
                    dbc.Button("Show Example", id="example-button", color="info", outline=True, className="mt-2")
                ]),
                html.Div(id="paste-feedback", className="mt-2"),

                # Collapsible example section
                dbc.Collapse(
                    [
                        html.P(
                            "Enter the text following the required format. You can copy and paste the following example to proceed.",
                            className="form-text text-muted mb-2"
                        ),
                        dbc.Card(dbc.CardBody([
                            html.Pre(
                                EXAMPLE_DATA,
                                style={"whiteSpace": "pre-wrap", "fontFamily": "monospace", "fontSize": "0.85rem"}
                            )
                        ]))
                    ],
                    id="example-collapse",
                    is_open=False,
                    className="mt-2"
                )
            ], className="mb-4")
        ], id="section-1"),
    ])
