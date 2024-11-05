import dash
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import time

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
def check_parentheses(s: str):
    """
    Check if parentheses are balanced and return step-by-step info
    """
    stack = []
    steps = []
    
    for i, char in enumerate(s):
        current_step = {
            'index': i,
            'char': char,
            'stack': stack.copy(),
            'status': '',
            'message': ''
        }
        
        if char in '({[':
            stack.append(char)
            current_step['message'] = f"Push '{char}' to stack"
            current_step['status'] = 'valid'
            
        elif char in ')}]':
            if not stack:
                current_step['message'] = f"Error: Found closing bracket '{char}' without matching opening bracket"
                current_step['status'] = 'error'
                steps.append(current_step)
                return steps, False
                
            top = stack.pop()
            if (top == '(' and char != ')') or \
               (top == '{' and char != '}') or \
               (top == '[' and char != ']'):
                current_step['message'] = f"Error: Mismatched brackets. Found '{char}' but expected closing bracket for '{top}'"
                current_step['status'] = 'error'
                steps.append(current_step)
                return steps, False
                
            current_step['message'] = f"Pop '{top}' from stack - matched with '{char}'"
            current_step['status'] = 'valid'
            
        steps.append(current_step)
    
    if stack:
        steps.append({
            'index': len(s),
            'char': '',
            'stack': stack,
            'status': 'error',
            'message': f"Error: Unclosed brackets remaining: {''.join(stack)}"
        })
        return steps, False
        
    return steps, True

app.layout = html.Div([
    dbc.Container([
        html.H1("Parentheses Matching Visualizer", className="text-center my-4"),
        
        # Input Section
        dbc.Row([
            dbc.Col([
                dbc.Input(
                    id='input-string',
                    type='text',
                    placeholder='Enter brackets (e.g., {()}[])',
                    value='{()}[]',
                    className="mb-3"
                ),
                dbc.Button("Check", id='check-button', color="primary", className="me-2"),
                dbc.Button("Reset", id='reset-button', color="secondary"),
            ])
        ]),
        
        # Visualization Section
        html.Div([
            html.H4("Input String", className="mt-4"),
            html.Div(id='char-display', className="mb-4"),
            
            html.H4("Stack", className="mt-4"),
            html.Div(id='stack-display', className="mb-4"),
            
            html.H4("Status", className="mt-4"),
            html.Div(id='status-display', className="mb-4"),
            
            # Store the current step
            dcc.Store(id='current-steps'),
            dcc.Store(id='current-step-index', data=0),
            
            # Interval for animation
            dcc.Interval(
                id='animation-interval',
                interval=1000,  # 1 second
                disabled=True
            ),
        ]),
    ], fluid=True)
])

@app.callback(
    [Output('current-steps', 'data'),
     Output('animation-interval', 'disabled')],
    Input('check-button', 'n_clicks'),
    State('input-string', 'value'),
    prevent_initial_call=True
)
def start_animation(n_clicks, input_string):
    if not input_string:
        return [], True
    steps, is_valid = check_parentheses(input_string)
    return steps, False

@app.callback(
    [Output('char-display', 'children'),
     Output('stack-display', 'children'),
     Output('status-display', 'children'),
     Output('current-step-index', 'data'),
     Output('animation-interval', 'disabled', allow_duplicate=True)],
    [Input('animation-interval', 'n_intervals'),
     Input('reset-button', 'n_clicks')],
    [State('current-steps', 'data'),
     State('current-step-index', 'data'),
     State('input-string', 'value')],
    prevent_initial_call=True
)
def update_visualization(n_intervals, reset_clicks, steps, step_index, input_string):
    if reset_clicks is not None and dash.callback_context.triggered_id == 'reset-button':
        return [], [], [], 0, True
        
    if not steps or step_index >= len(steps):
        return dash.no_update, dash.no_update, dash.no_update, step_index, True
        
    # Display characters with current position highlighted
    chars = []
    for i, char in enumerate(input_string):
        style = {
            'display': 'inline-block',
            'margin': '5px',
            'padding': '10px',
            'border': '1px solid black',
        }
        if i == steps[step_index]['index']:
            style['backgroundColor'] = 'lightgreen'
            style['border'] = '2px solid green'
        chars.append(html.Span(char, style=style))
    
    # Display stack
    stack = steps[step_index]['stack']
    stack_display = [
        html.Span(char, style={
            'display': 'inline-block',
            'margin': '5px',
            'padding': '10px',
            'border': '1px solid blue',
            'backgroundColor': 'lightblue'
        }) for char in stack
    ]
    
    # Display status message
    status_style = {
        'padding': '10px',
        'margin': '10px',
        'border': '1px solid',
        'borderRadius': '5px'
    }
    if steps[step_index]['status'] == 'error':
        status_style['backgroundColor'] = '#ffebee'
        status_style['color'] = '#c62828'
        status_style['borderColor'] = '#ef9a9a'
    else:
        status_style['backgroundColor'] = '#e8f5e9'
        status_style['color'] = '#2e7d32'
        status_style['borderColor'] = '#a5d6a7'
        
    status = html.Div(steps[step_index]['message'], style=status_style)
    
    return chars, stack_display, status, step_index + 1, False

if __name__ == '__main__':
    app.run_server(debug=True)