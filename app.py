import pandas as pd
from dash import Dash, html, dcc, dash_table, Input, Output
import plotly.express as px

# โหลดข้อมูล
df = pd.read_csv("filtered_tcas_cleaned.csv")
df['ค่าใช้จ่าย'] = df['ค่าใช้จ่าย'].astype(str).str.replace(',', '').astype(float)

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
        page_current=0,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '5px'},
        style_header={'fontWeight': 'bold', 'backgroundColor': '#f0f0f0'},
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': '#f9f9f9'}
        ],
        page_action='custom',
        filter_action='none',
        sort_action='none',
    ),

    html.Br(),

    html.H2("กราฟเปรียบเทียบค่าเทอมรายหลักสูตร (ตามหน้าตาราง)", style={'textAlign': 'center'}),
    dcc.Graph(id='bar-chart'),

    html.H2("Line Plot: ค่าเทอมเฉลี่ยรายมหาวิทยาลัย (ตามหน้าตาราง)", style={'textAlign': 'center'}),
    dcc.Graph(id='line-chart'),

    html.H2("Pie Chart: สัดส่วนจำนวนหลักสูตรในแต่ละมหาวิทยาลัย (ตามหน้าตาราง)", style={'textAlign': 'center'}),
    dcc.Graph(id='pie-chart'),
])

# Callback อัปเดตข้อมูลตารางตามมหาวิทยาลัยและช่วงราคา + pagination
@app.callback(
    Output('course-table', 'data'),
    Input('uni-dropdown', 'value'),
    Input('price-slider', 'value'),
    Input('course-table', 'page_current'),
    Input('course-table', 'page_size'),
)
def update_table(selected_unis, price_range, page_current, page_size):
    filtered_df = df.copy()
    if selected_unis:
        filtered_df = filtered_df[filtered_df['มหาวิทยาลัย'].isin(selected_unis)]
    filtered_df = filtered_df[
        (filtered_df['ค่าใช้จ่าย'] >= price_range[0]) &
        (filtered_df['ค่าใช้จ่าย'] <= price_range[1])
    ]

    start = page_current * page_size
    end = start + page_size
    page_data = filtered_df.iloc[start:end].to_dict('records')
    return page_data

# Callback อัปเดตกราฟ Bar, Line, Pie ตามข้อมูลในหน้าตารางที่แสดง
@app.callback(
    Output('bar-chart', 'figure'),
    Output('line-chart', 'figure'),
    Output('pie-chart', 'figure'),
    Input('course-table', 'data')
)
def update_charts(table_data):
    if not table_data:
        no_data_fig = px.bar(title="ไม่มีข้อมูลในหน้านี้")
        return no_data_fig, no_data_fig, no_data_fig

    page_df = pd.DataFrame(table_data)

    # Bar chart
    bar_fig = px.bar(
        page_df,
        x='ชื่อหลักสูตร',
        y='ค่าใช้จ่าย',
        color='มหาวิทยาลัย',
        labels={"ค่าใช้จ่าย": "ค่าเทอม (บาท/เทอม)", "ชื่อหลักสูตร": "หลักสูตร"},
        title="ค่าเทอมของหลักสูตรในหน้านี้"
    )
    bar_fig.update_layout(
        xaxis_tickangle=45,
        xaxis={
            'categoryorder': 'total descending',
            'showticklabels': False  # ซ่อน x-axis labels
        },
        height=500,
        margin=dict(t=50, b=50),  # ลด bottom margin เพราะไม่มี labels แล้ว
    )

    # Line chart (ค่าเทอมเฉลี่ยรายมหาวิทยาลัย)
    line_data = page_df.groupby('มหาวิทยาลัย')['ค่าใช้จ่าย'].mean().reset_index()
    line_fig = px.line(
        line_data,
        x='มหาวิทยาลัย',
        y='ค่าใช้จ่าย',
        markers=True,
        labels={"ค่าใช้จ่าย": "ค่าเทอมเฉลี่ย (บาท/เทอม)", "มหาวิทยาลัย": "มหาวิทยาลัย"},
        title="ค่าเทอมเฉลี่ยรายมหาวิทยาลัยในหน้านี้"
    )
    line_fig.update_layout(
        xaxis_tickangle=45,
        height=500,
        margin=dict(t=50, b=150),
    )

    # Pie chart (สัดส่วนจำนวนหลักสูตรในแต่ละมหาวิทยาลัย)
    pie_data = page_df['มหาวิทยาลัย'].value_counts().reset_index()
    pie_data.columns = ['มหาวิทยาลัย', 'จำนวนหลักสูตร']
    pie_fig = px.pie(
        pie_data,
        values='จำนวนหลักสูตร',
        names='มหาวิทยาลัย',
        title="สัดส่วนจำนวนหลักสูตรในแต่ละมหาวิทยาลัยในหน้านี้"
    )

    return bar_fig, line_fig, pie_fig


if __name__ == '__main__':
    app.run(debug=True)
