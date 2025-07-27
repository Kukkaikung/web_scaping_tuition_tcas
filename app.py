import pandas as pd
from dash import Dash, html, dcc, dash_table, Input, Output
import plotly.express as px

df = pd.read_csv("filtered_tcas_cleaned.csv")

uni_options = [{'label': uni, 'value': uni} for uni in sorted(df['มหาวิทยาลัย'].unique())]

min_price = int(df['ค่าใช้จ่าย'].min())
max_price = int(df['ค่าใช้จ่าย'].max())
price_marks = {i: f'{i}' for i in range(min_price, max_price+1, max(1000, (max_price-min_price)//10))}

table_columns = [
    {"name": "มหาวิทยาลัย", "id": "มหาวิทยาลัย"},
    {"name": "ชื่อหลักสูตร", "id": "ชื่อหลักสูตร"},
    {"name": "ค่าใช้จ่าย (บาท/เทอม)", "id": "ค่าใช้จ่าย"},
]

app = Dash(__name__)
app.title = "Dashboard ค่าเทอมหลักสูตร TCAS"

app.layout = html.Div([
    html.H1("📚 Dashboard ค่าเทอมหลักสูตร TCAS", style={'textAlign': 'center'}),

    html.Div([
        html.Label("เลือกมหาวิทยาลัย:", style={'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='uni-dropdown',
            options=uni_options,
            multi=True,
            placeholder="เลือกมหาวิทยาลัย (ถ้าว่างจะแสดงทั้งหมด)"
        )
    ], style={'width': '50%', 'margin': 'auto'}),

    html.Br(),

    html.Div([
        html.Label("ช่วงราคาค่าเทอม (บาท/เทอม):", style={'fontWeight': 'bold'}),
        dcc.RangeSlider(
            id='price-slider',
            min=min_price,
            max=max_price,
            step=500,
            marks=price_marks,
            value=[min_price, max_price],
            tooltip={"placement": "bottom", "always_visible": True}
        )
    ], style={'width': '80%', 'margin': 'auto'}),

    html.Br(),

    html.H2("ตารางหลักสูตร", style={'textAlign': 'center'}),
    dash_table.DataTable(
        id='course-table',
        columns=table_columns,
        data=df.to_dict('records'),
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '5px'},
        style_header={'fontWeight': 'bold', 'backgroundColor': '#f0f0f0'},
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': '#f9f9f9'}
        ]
    ),

    html.Br(),

    html.H2("กราฟเปรียบเทียบค่าเทอมรายหลักสูตร", style={'textAlign': 'center'}),
    dcc.Graph(id='bar-chart'),

    html.H2("Box Plot: การกระจายตัวของค่าเทอมแต่ละมหาวิทยาลัย", style={'textAlign': 'center'}),
    dcc.Graph(id='box-plot'),

    html.H2("Pie Chart: สัดส่วนจำนวนหลักสูตรในแต่ละมหาวิทยาลัย", style={'textAlign': 'center'}),
    dcc.Graph(id='pie-chart'),
])


@app.callback(
    Output('course-table', 'data'),
    Output('bar-chart', 'figure'),
    Output('box-plot', 'figure'),
    Output('pie-chart', 'figure'),
    Input('uni-dropdown', 'value'),
    Input('price-slider', 'value')
)
def update_dashboard(selected_unis, price_range):
    filtered_df = df.copy()
    if selected_unis and len(selected_unis) > 0:
        filtered_df = filtered_df[filtered_df['มหาวิทยาลัย'].isin(selected_unis)]

    filtered_df = filtered_df[
        (filtered_df['ค่าใช้จ่าย'] >= price_range[0]) & 
        (filtered_df['ค่าใช้จ่าย'] <= price_range[1])
    ]

    # Bar chart
    if filtered_df.empty:
        bar_fig = px.bar(title="ไม่มีข้อมูลในช่วงที่เลือก")
        box_fig = px.box(title="ไม่มีข้อมูลในช่วงที่เลือก")
        pie_fig = px.pie(title="ไม่มีข้อมูลในช่วงที่เลือก")
    else:
        bar_fig = px.bar(
            filtered_df, 
            x="ชื่อหลักสูตร", 
            y="ค่าใช้จ่าย", 
            color="มหาวิทยาลัย",
            labels={"ค่าใช้จ่าย": "ค่าเทอม (บาท/เทอม)", "ชื่อหลักสูตร": "หลักสูตร"},
            title="ค่าเทอมรายหลักสูตรตามเงื่อนไขการกรอง",
        )
        bar_fig.update_layout(xaxis_tickangle=45, xaxis={'categoryorder':'total descending'})

        box_fig = px.box(
            filtered_df, 
            x="มหาวิทยาลัย", 
            y="ค่าใช้จ่าย", 
            points="all",
            labels={"ค่าใช้จ่าย": "ค่าเทอม (บาท/เทอม)", "มหาวิทยาลัย": "มหาวิทยาลัย"},
            title="การกระจายตัวของค่าเทอมแต่ละมหาวิทยาลัย"
        )

        pie_data = filtered_df['มหาวิทยาลัย'].value_counts().reset_index()
        pie_data.columns = ['มหาวิทยาลัย', 'จำนวนหลักสูตร']
        pie_fig = px.pie(
            pie_data, 
            values='จำนวนหลักสูตร', 
            names='มหาวิทยาลัย',
            title="สัดส่วนจำนวนหลักสูตรในแต่ละมหาวิทยาลัย"
        )

    return filtered_df.to_dict('records'), bar_fig, box_fig, pie_fig


if __name__ == '__main__':
    app.run(debug=True)
