import pandas as pd
from dash import Dash, html, dcc, dash_table, Input, Output
import plotly.express as px

# โหลดข้อมูล
df = pd.read_csv("final_filtered_tcas_cleaned.csv")
df['ค่าใช้จ่าย'] = df['ค่าใช้จ่าย'].astype(str).str.replace(',', '').astype(float)

min_price = int(df['ค่าใช้จ่าย'].min())
max_price = int(df['ค่าใช้จ่าย'].max())
price_marks = {i: f'{i}' for i in range(min_price, max_price+1, max(1000, (max_price-min_price)//10))}

table_columns = [
    {"name": "มหาวิทยาลัย", "id": "มหาวิทยาลัย"},
    {"name": "ชื่อหลักสูตร", "id": "ชื่อหลักสูตร"},
    {"name": "ค่าใช้จ่าย (บาท/เทอม)", "id": "ค่าใช้จ่าย"},
]

# สี pastel สำหรับ pie chart
pastel_colors = [
    '#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF',
    '#E1BAFF', '#FFBAE1', '#FFC9BA', '#C9FFBA', '#BAD1FF',
    '#D1BAFF', '#FFBAFF', '#BAFFE1', '#E1FFBA', '#FFD1BA'
]

app = Dash(__name__)
app.title = "Dashboard ค่าเทอมหลักสูตร TCAS"

app.layout = html.Div([
    html.H1("📚 Dashboard ค่าเทอมหลักสูตร TCAS", style={'textAlign': 'center'}),

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

    # เพิ่มส่วนแสดงสถิติ
    html.Div(id='stats-cards', style={'textAlign': 'center', 'margin': '20px'}),

    html.H2("ตารางหลักสูตร", style={'textAlign': 'center'}),
    dash_table.DataTable(
        id='course-table',
        columns=table_columns,
        data=df.to_dict('records'),
        page_size=5,
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

    html.H2("กราหเปรียบเทียบค่าเทอมรายหลักสูตร", style={'textAlign': 'center'}),
    html.Div([
        html.Div([
            html.H3("ตามหน้าตาราง", style={'textAlign': 'center', 'fontSize': '16px'}),
            dcc.Graph(id='bar-chart')
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            html.H3("Top 5 ค่าเทอมสูงสุด (ทั้งหมด)", style={'textAlign': 'center', 'fontSize': '16px'}),
            dcc.Graph(id='top5-chart')
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),

    html.H2("Line Plot: ค่าเทอมเฉลี่ยรายมหาวิทยาลัย (ตามหน้าตาราง)", style={'textAlign': 'center'}),
    dcc.Graph(id='line-chart'),

    html.H2("Pie Chart: สัดส่วนจำนวนหลักสูตรในแต่ละมหาวิทยาลัย (ตามหน้าตาราง)", style={'textAlign': 'center'}),
    dcc.Graph(id='pie-chart'),
])

# Callback อัปเดตข้อมูลตารางตามช่วงราคา + pagination
@app.callback(
    Output('course-table', 'data'),
    Input('price-slider', 'value'),
    Input('course-table', 'page_current'),
    Input('course-table', 'page_size'),
)
def update_table(price_range, page_current, page_size):
    filtered_df = df.copy()
    filtered_df = filtered_df[
        (filtered_df['ค่าใช้จ่าย'] >= price_range[0]) &
        (filtered_df['ค่าใช้จ่าย'] <= price_range[1])
    ]

    start = page_current * page_size
    end = start + page_size
    page_data = filtered_df.iloc[start:end].to_dict('records')
    return page_data

# Callback อัปเดตสถิติและกราฟ
@app.callback(
    Output('stats-cards', 'children'),
    Output('bar-chart', 'figure'),
    Output('top5-chart', 'figure'),
    Output('line-chart', 'figure'),
    Output('pie-chart', 'figure'),
    Input('course-table', 'data'),
    Input('price-slider', 'value')
)
def update_charts_and_stats(table_data, price_range):
    if not table_data:
        no_data_fig = px.bar(title="ไม่มีข้อมูลในหน้านี้")
        no_stats = html.Div("ไม่มีข้อมูลในหน้านี้")
        return no_stats, no_data_fig, no_data_fig, no_data_fig, no_data_fig

    page_df = pd.DataFrame(table_data)
    
    # สำหรับ Top 5 และ Stats Cards - ใช้ข้อมูลทั้งหมดที่ผ่านการกรอง
    filtered_df = df.copy()
    filtered_df = filtered_df[
        (filtered_df['ค่าใช้จ่าย'] >= price_range[0]) &
        (filtered_df['ค่าใช้จ่าย'] <= price_range[1])
    ]
    top5_df = filtered_df.nlargest(5, 'ค่าใช้จ่าย')
    
    # คำนวณสถิติจากข้อมูลทั้งหมด (ที่ผ่านการกรอง)
    max_price = filtered_df['ค่าใช้จ่าย'].max()
    min_price = filtered_df['ค่าใช้จ่าย'].min()
    mean_price = filtered_df['ค่าใช้จ่าย'].mean()
    
    # สร้าง stats cards
    stats_cards = html.Div([
        html.Div([
            html.H3(f"{max_price:,.0f}", style={'color': '#e74c3c', 'margin': '0'}),
            html.P("ค่าเทอมสูงสุด (บาท)", style={'margin': '0', 'fontSize': '14px'})
        ], style={
            'backgroundColor': '#ffe6e6', 'padding': '15px', 'borderRadius': '10px',
            'textAlign': 'center', 'margin': '0 10px', 'minWidth': '150px'
        }),
        
        html.Div([
            html.H3(f"{min_price:,.0f}", style={'color': '#27ae60', 'margin': '0'}),
            html.P("ค่าเทอมต่ำสุด (บาท)", style={'margin': '0', 'fontSize': '14px'})
        ], style={
            'backgroundColor': '#e6ffe6', 'padding': '15px', 'borderRadius': '10px',
            'textAlign': 'center', 'margin': '0 10px', 'minWidth': '150px'
        }),
        
        html.Div([
            html.H3(f"{mean_price:,.0f}", style={'color': '#3498db', 'margin': '0'}),
            html.P("ค่าเทอมเฉลี่ย (บาท)", style={'margin': '0', 'fontSize': '14px'})
        ], style={
            'backgroundColor': '#e6f3ff', 'padding': '15px', 'borderRadius': '10px',
            'textAlign': 'center', 'margin': '0 10px', 'minWidth': '150px'
        })
    ], style={'display': 'flex', 'justifyContent': 'center', 'flexWrap': 'wrap'})

    # Bar chart (ตามหน้าตาราง)
    bar_fig = px.bar(
        page_df,
        x='มหาวิทยาลัย_หลักสูตร',
        y='ค่าใช้จ่าย',
        color='มหาวิทยาลัย',
        labels={"ค่าใช้จ่าย": "ค่าเทอม (บาท/เทอม)", "ชื่อหลักสูตร": "หลักสูตร"},
        title=""
    )
    bar_fig.update_layout(
        xaxis_tickangle=45,
        xaxis={
            'categoryorder': 'total descending',
            'showticklabels': False
        },
        height=400,
        margin=dict(t=20, b=50),
    )

    # Top 5 Bar chart (แนวนอน)
    top5_fig = px.bar(
        top5_df,
        x='ค่าใช้จ่าย',
        y='ชื่อหลักสูตร',
        color='มหาวิทยาลัย',
        orientation='h',
        labels={"ค่าใช้จ่าย": "ค่าเทอม (บาท/เทอม)", "ชื่อหลักสูตร": "หลักสูตร"},
        title=""
    )
    top5_fig.update_layout(
        yaxis={'categoryorder': 'total ascending',
        'showticklabels': False
        },
        height=400,
        margin=dict(t=20, b=50, l=200),  # เพิ่ม left margin สำหรับชื่อหลักสูตร
    )

    # Line chart
    # line_data = page_df.groupby('มหาวิทยาลัย')['ค่าใช้จ่าย'].mean().reset_index()
    line_fig = px.line(
        page_df,
        x=[i+1 for i in range(len(page_df))],  # เริ่มที่ 1 แทน 0
        y='ค่าใช้จ่าย',
        markers=True,
        labels={"x": "ลำดับในตาราง", "ค่าใช้จ่าย": "ค่าเทอม (บาท/เทอม)"},
        title="ค่าเทอมแต่ละหลักสูตรในหน้านี้ (ตามลำดับในตาราง)",
        hover_data=['ชื่อหลักสูตร', 'มหาวิทยาลัย']
    )
    # ปรับแต่ง layout
    line_fig.update_layout(
        height=500,
        margin=dict(t=50, b=100),
        xaxis=dict(
            title="ลำดับในตาราง",
            tickmode='linear',
            tick0=1,  # เริ่มที่ 1 แทน 0
            dtick=1 if len(page_df) <= 10 else max(1, len(page_df)//10)
        )
    )

    # เพิ่มสีให้แต่ละจุดตามมหาวิทยาลัย (ถ้าต้องการ)
    line_fig.update_traces(
        line=dict(color='blue', width=2),
        marker=dict(size=8, color='red')
    )

    # Pie chart with same colors as bar chart
    pie_data = page_df['มหาวิทยาลัย'].value_counts().reset_index()
    pie_data.columns = ['มหาวิทยาลัย', 'จำนวนหลักสูตร']
    pie_fig = px.pie(
        pie_data,
        values='จำนวนหลักสูตร',
        names='มหาวิทยาลัย',
        title="สัดส่วนจำนวนหลักสูตรในแต่ละมหาวิทยาลัยในหน้านี้"
        # ลบ color_discrete_sequence เพื่อใช้สีเดียวกับ bar chart
    )
    pie_fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        textfont_size=12,
        insidetextorientation='radial'  # ข้อความแนวตามรัศมี
    )

    return stats_cards, bar_fig, top5_fig, line_fig, pie_fig


if __name__ == '__main__':
    app.run(debug=True)