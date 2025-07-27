# Web Scraping TCAS Tuition Fees for Computer Engineering & AI Programs

This project focuses on extracting tuition fee data for Computer Engineering and Artificial Intelligence-related programs from the **TCAS website** using web scraping techniques, cleaning the data, and visualizing it using an interactive dashboard built with Dash.

## 🔧 Technologies Used

- **Python** – Main programming language
- **Playwright** – Automates web browser interactions and handles JavaScript-rendered content
- **BeautifulSoup** – Parses and extracts HTML content
- **Pandas** – Cleans and processes data
- **Dash (Plotly)** – Creates interactive web dashboards

## 📌 Main Features

1. **Web Scraping**
   - Targets programs related to *Computer Engineering* and *Artificial Intelligence* from the TCAS website
   - Uses `Playwright` to render JavaScript and access dynamic content
   - Uses `BeautifulSoup` to extract necessary data fields from HTML

2. **Data Cleaning (Two Rounds)**
   - Cleans and converts tuition data into numerical format
   - Standardizes diverse formats (e.g., per semester, per year, entire course)
   - Complements missing tuition data by scraping additional sources when necessary

3. **Data Visualization**
   - Displays the final dataset on a Dash-based web dashboard
   - Allows filtering by university or program
   - Includes interactive charts like Bar Charts, Pie Charts, and Line Graphs for comparison and analysis
