import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Charger les données
df = pd.read_excel("donnees_entreprise.xlsx")  # Remplacez par le chemin correct

# Vérifiez que toutes les colonnes nécessaires existent
required_columns = [
    "Categorie", "Mode_Paiement", "Montant_Total", "Satisfaction_Client", 
    "Segment_Client", "Ville", "Leads_Generes", "Conversions"
]
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    raise ValueError(f"Les colonnes suivantes sont manquantes dans vos données : {missing_columns}")

# Initialiser l'application Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# Mise en page
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Tableau de Bord Interactif", className="text-center mb-4"), width=12),
    ]),
    dbc.Row([
        # Indicateurs principaux
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H5("Chiffre d'affaires total"),
            html.H3(id="total-sales", className="text-primary")
        ])), width=3),
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H5("Nombre de clients uniques"),
            html.H3(id="unique-clients", className="text-success")
        ])), width=3),
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H5("Satisfaction moyenne"),
            html.H3(id="average-satisfaction", className="text-info")
        ])), width=3),
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H5("Taux de conversion (%)"),
            html.H3(id="conversion-rate", className="text-warning")
        ])), width=3),
    ]),
    # Filtres interactifs
    dbc.Row([
        dbc.Col([
            html.Label("Catégorie"),
            dcc.Dropdown(
                id="filter-categorie",
                options=[{"label": c, "value": c} for c in df["Categorie"].unique()],
                multi=True,
                placeholder="Filtrer par catégorie"
            ),
        ], width=3),
        dbc.Col([
            html.Label("Mode de paiement"),
            dcc.Dropdown(
                id="filter-paiement",
                options=[{"label": m, "value": m} for m in df["Mode_Paiement"].unique()],
                placeholder="Filtrer par mode de paiement"
            ),
        ], width=3),
        dbc.Col([
            html.Label("Segment client"),
            dcc.Dropdown(
                id="filter-segment",
                options=[{"label": s, "value": s} for s in df["Segment_Client"].unique()],
                placeholder="Filtrer par segment client"
            ),
        ], width=3),
        dbc.Col([
            html.Label("Ville"),
            dcc.Dropdown(
                id="filter-ville",
                options=[{"label": v, "value": v} for v in df["Ville"].unique()],
                placeholder="Filtrer par ville"
            ),
        ], width=3),
    ]),
    # Graphiques
    dbc.Row([
        dbc.Col(dcc.Graph(id="graph-sales", style={"height": "400px", "width": "100%"}), width=6),
        dbc.Col(dcc.Graph(id="graph-satisfaction", style={"height": "400px", "width": "100%"}), width=6),
    ])
], fluid=True)

# Callback pour mettre à jour les indicateurs principaux
@app.callback(
    [Output("total-sales", "children"),
     Output("unique-clients", "children"),
     Output("average-satisfaction", "children"),
     Output("conversion-rate", "children")],
    [Input("filter-categorie", "value"),
     Input("filter-paiement", "value"),
     Input("filter-segment", "value"),
     Input("filter-ville", "value")]
)
def update_indicators(categorie, paiement, segment, ville):
    filtered_df = df
    if categorie:
        filtered_df = filtered_df[filtered_df["Categorie"].isin(categorie)]
    if paiement:
        filtered_df = filtered_df[filtered_df["Mode_Paiement"] == paiement]
    if segment:
        filtered_df = filtered_df[filtered_df["Segment_Client"] == segment]
    if ville:
        filtered_df = filtered_df[filtered_df["Ville"] == ville]

    total_sales = f"{filtered_df['Montant_Total'].sum():,.0f} €"
    unique_clients = filtered_df["Segment_Client"].nunique()
    avg_satisfaction = f"{filtered_df['Satisfaction_Client'].mean():.2f}"
    conversion_rate = f"{(filtered_df['Conversions'].sum() / filtered_df['Leads_Generes'].sum()) * 100:.2f} %" if filtered_df['Leads_Generes'].sum() > 0 else "0 %"

    return total_sales, unique_clients, avg_satisfaction, conversion_rate

# Callback pour mettre à jour le graphique des ventes
@app.callback(
    Output("graph-sales", "figure"),
    [Input("filter-categorie", "value"),
     Input("filter-paiement", "value"),
     Input("filter-segment", "value"),
     Input("filter-ville", "value")]
)
def update_sales_graph(categorie, paiement, segment, ville):
    filtered_df = df
    if categorie:
        filtered_df = filtered_df[filtered_df["Categorie"].isin(categorie)]
    if paiement:
        filtered_df = filtered_df[filtered_df["Mode_Paiement"] == paiement]
    if segment:
        filtered_df = filtered_df[filtered_df["Segment_Client"] == segment]
    if ville:
        filtered_df = filtered_df[filtered_df["Ville"] == ville]

    if filtered_df.empty:
        return px.scatter(title="Aucune donnée disponible.")

    fig = px.bar(
        filtered_df,
        x="Categorie",
        y="Montant_Total",
        color="Mode_Paiement",
        title="Chiffre d'affaires par Catégorie"
    )
    return fig

# Callback pour mettre à jour le graphique de satisfaction client
@app.callback(
    Output("graph-satisfaction", "figure"),
    [Input("filter-categorie", "value"),
     Input("filter-paiement", "value"),
     Input("filter-segment", "value"),
     Input("filter-ville", "value")]
)
def update_satisfaction_graph(categorie, paiement, segment, ville):
    filtered_df = df
    if categorie:
        filtered_df = filtered_df[filtered_df["Categorie"].isin(categorie)]
    if paiement:
        filtered_df = filtered_df[filtered_df["Mode_Paiement"] == paiement]
    if segment:
        filtered_df = filtered_df[filtered_df["Segment_Client"] == segment]
    if ville:
        filtered_df = filtered_df[filtered_df["Ville"] == ville]

    if filtered_df.empty:
        return px.scatter(title="Aucune donnée disponible.")

    fig = px.histogram(
        filtered_df,
        x="Satisfaction_Client",
        color="Categorie",
        title="Distribution de la Satisfaction Client"
    )
    return fig

# Lancer l'application
if __name__ == "__main__":
    app.run_server(debug=True)
