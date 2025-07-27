import pandas as pd
from dash import Dash, html, dcc, dash_table, Input, Output
import plotly.express as px

# โหลดข้อมูล
df = pd.read_csv("filtered_tcas_cleaned.csv")
df['ค่าใช้จ่าย'] = df['ค่าใช้จ่าย'].astype(str).str.replace(',', '').astype(float)

# ตัวเลือกมหาวิทยาลัย
uni_options = [{'label': uni, 'value': uni} for uni in sorted(df['มหาวิทยาลัย'].unique())]

# ขอบเขตราคา
min_price = int(df['ค่าใช้จ่าย'].min())
max_price = int(df['ค่าใช้จ่าย'].max())
price_marks = {i: f'{i}' for i in range(min_price, max_price+1, max(1000, (max_price-min_price)//10))}

# คอลัมน์ตาราง
table_columns = [
    {"name": "มหาวิทยาลัย", "id": "มหาวิทยาลัย"},
    {"name": "ชื่อหลักสูตร", "id": "ชื่อหลักสูตร"},
    {"name": "ค่าใช้จ่าย (บาท/เทอม)", "id": "ค่าใช้จ่าย"},
]

# สร้างแอป Dash
app = Dash(__name__)
app.title = "Dashboard ค่าเทอมหลักสูตร TCAS"

# Layout
app.layout = html.Div([
    html.H1("\ud83d\udcda Dashboard ค่าเทอมหลักสูตร TCAS", style={'textAlign': 'center'}),

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

    html.Div([
        html.Label("เลือกหลักสูตรที่ต้องการดูกราฟ (สูงสุด 5 หลักสูตร):", style={'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='course-dropdown',
            multi=True,
            placeholder="เลือกหลักสูตร...",
            options=[],
            maxHeight=300
        )
    ], style={'width': '80%', 'margin': 'auto'}),

    html.Br(),

    html.Div(id='stats-cards', style={
        "display": "flex",
        "justifyContent": "center",
        "gap": "20px",
        "flexWrap": "wrap"
    }),

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

# Callback: อัปเดตรายชื่อหลักสูตรใน Dropdown
@app.callback(
    Output('course-dropdown', 'options'),
    Output('course-dropdown', 'value'),
    Input('uni-dropdown', 'value'),
    Input('price-slider', 'value')
)
def update_course_dropdown(selected_unis, price_range):
    filtered_df = df.copy()
    if selected_unis and len(selected_unis) > 0:
        filtered_df = filtered_df[filtered_df['มหาวิทยาลัย'].isin(selected_unis)]
    filtered_df = filtered_df[
        (filtered_df['ค่าใช้จ่าย'] >= price_range[0]) &
        (filtered_df['ค่าใช้จ่าย'] <= price_range[1])
    ]
    course_options = [{'label': c, 'value': c} for c in sorted(filtered_df['ชื่อหลักสูตร'].unique())]
    return course_options, [c['value'] for c in course_options[:5]]

# Callback หลัก: อัปเดตตาราง กราฟ และการ์ดสถิติ
@app.callback(
    Output('course-table', 'data'),
    Output('bar-chart', 'figure'),
    Output('box-plot', 'figure'),
    Output('pie-chart', 'figure'),
    Output('stats-cards', 'children'),
    Input('uni-dropdown', 'value'),
    Input('price-slider', 'value'),
    Input('course-dropdown', 'value')
)
def update_dashboard(selected_unis, price_range, selected_courses):
    filtered_df = df.copy()
    if selected_unis and len(selected_unis) > 0:
        filtered_df = filtered_df[filtered_df['มหาวิทยาลัย'].isin(selected_unis)]

    filtered_df = filtered_df[
        (filtered_df['ค่าใช้จ่าย'] >= price_range[0]) & 
        (filtered_df['ค่าใช้จ่าย'] <= price_range[1])
    ]

    if filtered_df.empty:
        bar_fig = px.bar(title="ไม่มีข้อมูลในช่วงที่เลือก")
        box_fig = px.box(title="ไม่มีข้อมูลในช่วงที่เลือก")
        pie_fig = px.pie(title="ไม่มีข้อมูลในช่วงที่เลือก")
        return [], bar_fig, box_fig, pie_fig, []

    # กรองเฉพาะหลักสูตรที่เลือกสำหรับ bar chart
    bar_df = filtered_df[filtered_df['ชื่อหลักสูตร'].isin(selected_courses)] if selected_courses else filtered_df.copy()

    # Bar Chart
    bar_fig = px.bar(
        bar_df,
        x="ชื่อหลักสูตร",
        y="ค่าใช้จ่าย",
        color="มหาวิทยาลัย",
        labels={"ค่าใช้จ่าย": "ค่าเทอม (บาท/เทอม)", "ชื่อหลักสูตร": "หลักสูตร"},
        title="ค่าเทอมรายหลักสูตรตามเงื่อนไขการกรอง",
    )
    bar_fig.update_layout(
        xaxis_tickangle=45,
        xaxis={'categoryorder': 'total descending'},
        height=500,
        margin=dict(t=50, b=150),
    )

    # Box Plot
    box_fig = px.box(
        filtered_df,
        x="มหาวิทยาลัย",
        y="ค่าใช้จ่าย",
        points="all",
        labels={"ค่าใช้จ่าย": "ค่าเทอม (บาท/เทอม)", "มหาวิทยาลัย": "มหาวิทยาลัย"},
        title="การกระจายตัวของค่าเทอมแต่ละมหาวิทยาลัย"
    )

    # Pie Chart
    pie_data = filtered_df['มหาวิทยาลัย'].value_counts().reset_index()
    pie_data.columns = ['มหาวิทยาลัย', 'จำนวนหลักสูตร']
    pie_fig = px.pie(
        pie_data,
        values='จำนวนหลักสูตร',
        names='มหาวิทยาลัย',
        title="สัดส่วนจำนวนหลักสูตรในแต่ละมหาวิทยาลัย"
    )

    # สถิติการ์ด
    max_cost = filtered_df['ค่าใช้จ่าย'].max()
    min_cost = filtered_df['ค่าใช้จ่าย'].min()
    avg_cost = filtered_df['ค่าใช้จ่าย'].mean()

    stats_cards = [
        html.Div([
            html.Div("Max", style={"fontWeight": "bold", "color": "white"}),
            html.Div(f"{max_cost:,.0f} บาท", style={"fontSize": "20px", "color": "white"})
        ], style={"backgroundColor": "#003f5c", "padding": "15px", "borderRadius": "10px", "textAlign": "center"}),

        html.Div([
            html.Div("Min", style={"fontWeight": "bold", "color": "white"}),
            html.Div(f"{min_cost:,.0f} บาท", style={"fontSize": "20px", "color": "white"})
        ], style={"backgroundColor": "#bc5090", "padding": "15px", "borderRadius": "10px", "textAlign": "center"}),

        html.Div([
            html.Div("Average", style={"fontWeight": "bold", "color": "white"}),
            html.Div(f"{avg_cost:,.0f} บาท", style={"fontSize": "20px", "color": "white"})
        ], style={"backgroundColor": "#ffa600", "padding": "15px", "borderRadius": "10px", "textAlign": "center"})
    ]

    return filtered_df.to_dict('records'), bar_fig, box_fig, pie_fig, stats_cards

# Run app
if __name__ == '__main__':
    app.run(debug=True)
