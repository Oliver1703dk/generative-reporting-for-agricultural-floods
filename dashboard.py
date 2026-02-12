"""
Dash dashboard application for flood monitoring
"""
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import os
from typing import List, Dict
from config import COLORS, CLASSIFICATION
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from llm_report import generate_report, save_report_to_file, STAKEHOLDER_PROMPTS
import dash_bootstrap_components as dbc
from dash import dcc



def create_dashboard_app(sensors: List[Dict], map_file: str) -> dash.Dash:
    """Create and configure the Dash application"""
    app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

    app.layout = html.Div([
        html.Div([
            html.H1(
                "🌊 Flood Monitoring Dashboard - Fyn Island",
                style={
                    'textAlign': 'center',
                    'color': COLORS['primary'],
                    'marginBottom': '10px',
                    'fontFamily': 'Arial, sans-serif'
                }
            ),

        ], style={'padding': '20px', 'background': COLORS['card']}),

        html.Div([
            html.Div([
                create_stats_card("Total Sensors", len(sensors), "📡"),
                create_stats_card("Flood Alerts",
                                count_by_prediction(sensors, 2), "🔴"),
                create_stats_card("Suspicious",
                                count_by_prediction(sensors, 1), "🟠"),
                create_stats_card("Normal",
                                count_by_prediction(sensors, 0), "🟢"),
            ], style={
                'display': 'flex',
                'justifyContent': 'space-around',
                'flexWrap': 'wrap',
                'marginBottom': '20px'
            }),
        ], style={'padding': '0 20px'}),
        html.Div([
            dcc.Loading(
                id="loading-report",
                type="default",
                children=html.Div(id="loading-output"),
                fullscreen=True,
                style={'background': 'rgba(0,0,0,0.3)'}
            ),
            html.Div([
                dcc.Dropdown(
                    id='stakeholder-selector',
                    options=[
                        {'label': cfg['label'], 'value': key}
                        for key, cfg in STAKEHOLDER_PROMPTS.items()
                    ],
                    value='general',
                    clearable=False,
                    style={
                        'width': '220px',
                        'fontSize': '16px',
                    }
                ),
                html.Button(
                    '📊 Generate AI Report',
                    id='generate-report-btn',
                    n_clicks=0,
                    style={
                        'padding': '15px 30px',
                        'fontSize': '18px',
                        'background': COLORS['primary'],
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '8px',
                        'cursor': 'pointer',
                        'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                        'fontWeight': 'bold',
                        'transition': 'all 0.3s'
                    }
                ),
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'gap': '15px',
            }),
            html.P(
                '⏱️ Report generation takes 10-15 seconds',
                style={
                    'marginTop': '10px',
                    'color': '#666',
                    'fontSize': '14px',
                    'fontStyle': 'italic'
                }
            )
        ], style={'textAlign': 'center', 'margin': '20px'}),

        # Modal for report
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("🌊 AI-Generated Flood Monitoring Report", id="report-modal-title"), close_button=True),
            dbc.ModalBody([
                html.Div(id='report-content', style={
                    'maxHeight': '500px',
                    'overflowY': 'auto',
                    'padding': '20px',
                    'background': '#f8f9fa',
                    'borderRadius': '5px'
                }),
                html.Div(id='report-loading')
            ]),
            dbc.ModalFooter(
                html.Button(
                    "Close",
                    id="close-report-btn",
                    style={
                        'padding': '10px 20px',
                        'background': '#6c757d',
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '5px',
                        'cursor': 'pointer'
                    }
                )
            ),
        ], id='report-modal', size='xl', is_open=False, scrollable=True),

        html.Div([
            html.Iframe(
                id='map-iframe',
                src='/map',  # Reference the map file via URL
                style={
                    'width': '100%',
                    'height': '700px',
                    'border': 'none',
                    'borderRadius': '10px',
                    'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
                }
            )

        ], style={'padding': '0 20px 20px 20px'}),

        html.Div([
            html.H3("Legend", style={'color': COLORS['primary'], 'marginBottom': '15px'}),
            html.Div([
                create_legend_item("🔴 Red Pin", "Flood Detected (Level 2)"),
                create_legend_item("🟠 Orange Pin", "Suspicious Activity (Level 1)"),
                create_legend_item("🟢 Green Pin", "Normal Conditions (Level 0)"),
            ], style={'display': 'flex', 'gap': '20px', 'flexWrap': 'wrap'})
        ], style={
            'padding': '20px',
            'margin': '20px',
            'background': COLORS['card'],
            'borderRadius': '10px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
        }),

    ], style={
        'fontFamily': 'Arial, sans-serif',
        'background': COLORS['background'],
        'minHeight': '100vh',
        'padding': '0',
        'margin': '0'
    })
    # Store sensors data for callbacks
    app.sensors_data = sensors

    # Callback for generating report
    @app.callback(
        [Output('report-modal', 'is_open'),
         Output('report-content', 'children'),
         Output('report-loading', 'children'),
         Output('loading-output', 'children'),
         Output('report-modal-title', 'children')],
        [Input('generate-report-btn', 'n_clicks'),
         Input('close-report-btn', 'n_clicks')],
        [State('report-modal', 'is_open'),
         State('stakeholder-selector', 'value')],
        prevent_initial_call=True
    )
    def toggle_report_modal(generate_clicks, close_clicks, is_open, stakeholder):
        from dash import ctx

        if ctx.triggered_id == 'generate-report-btn':
            stakeholder = stakeholder or "general"
            label = STAKEHOLDER_PROMPTS.get(stakeholder, STAKEHOLDER_PROMPTS["general"])["label"]

            # Generate report (this takes time)
            report_text = generate_report(app.sensors_data, stakeholder=stakeholder)

            # Save to file for download
            filename = save_report_to_file(report_text)

            # Display in modal with markdown formatting
            report_display = dcc.Markdown(
                report_text,
                style={
                    'whiteSpace': 'pre-wrap',
                    'fontFamily': 'Arial, sans-serif',
                    'lineHeight': '1.6'
                }
            )

            download_button = html.Div([
                html.Hr(),
                html.A(
                    '📥 Download Report (.txt)',
                    href=f'/{filename}',
                    download=filename,
                    style={
                        'display': 'inline-block',
                        'padding': '12px 24px',
                        'background': COLORS['primary'],
                        'color': 'white',
                        'borderRadius': '5px',
                        'textDecoration': 'none',
                        'fontWeight': 'bold',
                        'textAlign': 'center'
                    }
                )
            ], style={'textAlign': 'center', 'marginTop': '20px'})

            title = f"🌊 AI Flood Report - {label}"
            return True, report_display, download_button, "", title

        return False, "", "", "", "🌊 AI-Generated Flood Monitoring Report"

    return app

def create_stats_card(title: str, value: int, icon: str) -> html.Div:
    """Create a statistics card component"""
    return html.Div([
        html.Div(icon, style={'fontSize': '36px', 'marginBottom': '10px'}),
        html.H2(str(value), style={'margin': '10px 0', 'color': COLORS['primary']}),
        html.P(title, style={'margin': '0', 'color': COLORS['text'], 'fontSize': '14px'}),
    ], style={
        'background': COLORS['card'],
        'padding': '25px',
        'borderRadius': '10px',
        'textAlign': 'center',
        'minWidth': '150px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
        'margin': '10px'
    })

def create_legend_item(symbol: str, description: str) -> html.Div:
    """Create a legend item"""
    return html.Div([
        html.Span(symbol, style={'marginRight': '10px', 'fontSize': '18px'}),
        html.Span(description, style={'color': COLORS['text']})
    ], style={'display': 'flex', 'alignItems': 'center'})

def count_by_prediction(sensors: List[Dict], prediction_level: int) -> int:
    """Count sensors with specific prediction level"""
    return sum(1 for s in sensors if s.get('prediction') == prediction_level)
