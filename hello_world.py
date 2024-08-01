import streamlit as st
import pandas as pd
from st_click_detector import click_detector

# Define a function to be called when an item is clicked
def item_clicked(item):
    st.write(f"You clicked on {item}!")

# Sample data with dictionaries
data = {
    'Text Column': ['Item 1', 'Item 2', 'Item 3'],
    'Link Column': [
        [{'name': 'apple', 'url': 'apple'}, {'name': 'banana', 'url': 'banana'}, {'name': 'cherry', 'url': 'cherry'}],
        [{'name': 'dog', 'url': 'dog'}, {'name': 'cat', 'url': 'cat'}, {'name': 'bird', 'url': 'bird'}],
        [{'name': 'red', 'url': 'red'}, {'name': 'green', 'url': 'green'}, {'name': 'blue', 'url': 'blue'}]
    ]
}

df = pd.DataFrame(data)

# Generate HTML content for the links
html_content = """
<style>
    table {
        width: 100%;
        border-collapse: collapse;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
    }
    th {
        padding-top: 12px;
        padding-bottom: 12px;
        text-align: left;
        background-color: #f2f2f2;
    }
    a {
        text-decoration: none;
        color: blue;
    }
</style>
<table>
    <tr>
        <th>Text Column</th>
        <th>Link Column</th>
    </tr>
"""

for _, row in df.iterrows():
    html_content += f"<tr><td>{row['Text Column']}</td><td>"
    for link_dict in row['Link Column']:
        html_content += f'<a href="#" id="{link_dict["name"]}">{link_dict["name"]}</a> '
    html_content += "</td></tr>"

html_content += "</table>"

# Use click_detector to capture clicks
clicked = click_detector(html_content)

# Display the clicked item if any
if clicked:
    item_clicked(clicked)

# Show the content with the links
#st.markdown(html_content, unsafe_allow_html=True)
