# Built-in modules
import os
import json
from datetime import datetime
import re
import io
import tempfile

# Third-party libraries
import fitz  # PyMuPDF
import pandas as pd
import matplotlib.pyplot as plt

import matplotlib
matplotlib.use('Agg') 

import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from fpdf import FPDF

# Local modules
from db_handler import insert_cheque_details, fetch_cheque_details, get_db_connection


from gemini import Model

from dotenv import load_dotenv
load_dotenv()



# Constants
TEMP_IMAGE_DIR = "temp_images"

LOGIN_EMAIL = os.getenv("LOGIN_EMAIL")
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD")



# Create temporary directory for image storage
if not os.path.exists(TEMP_IMAGE_DIR):
    os.makedirs(TEMP_IMAGE_DIR)

# Helper functions
def save_uploaded_file(uploaded_file):
    """Save the uploaded file to a temporary directory."""
    file_path = os.path.join(TEMP_IMAGE_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())
    return file_path

def clear_temp_files():
    """Clear all files in the temporary directory."""
    for file in os.listdir(TEMP_IMAGE_DIR):
        file_path = os.path.join(TEMP_IMAGE_DIR, file)
        try:
            os.remove(file_path)
        except OSError as e:
            print(f"Error deleting file {file_path}: {e}")

def convert_pdf_to_images(pdf_path):
    """Convert PDF to images using PyMuPDF and return paths to the images."""
    pdf_document = fitz.open(pdf_path)
    image_paths = []

    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        pixmap = page.get_pixmap()
        image_path = os.path.join(TEMP_IMAGE_DIR, f"Cheque_{page_number + 1}.jpg")
        pixmap.save(image_path)
        image_paths.append(image_path)

    pdf_document.close()
    return image_paths

def sanitize_micr_code(micr_code):
    """Sanitize MICR code by removing non-alphanumeric characters."""
    return re.sub(r'[^a-zA-Z0-9]', '', micr_code)

def preprocess_cheque_details(details):
    """Preprocess extracted cheque details to match the required database format."""
    details["payee_name"] = details.get("payeeName", "")
    details["cheque_number"] = details.get("chequeNumber", "N/A")
    details["amount_in_numbers"] = details.get("amountInNumbers", "").replace(",", "")
    details["amount_in_words"] = details.get("amountInWords", "")
    details["account_number"] = details.get("accountNumber", "")
    details["bank_name"] = details.get("bankName", "")
    details["branch"] = details.get("branch", "")
    details["micr_code"] = sanitize_micr_code(details.get("micrCode", ""))
    details["ifsc_code"] = details.get("ifscCode", "")
    date_str = details.get("date", "")
    if date_str:
        formatted_date = datetime.strptime(date_str, "%d%m%Y").strftime("%Y-%m-%d")
        details["date"] = formatted_date
    details["signature_name"] = details.get("signatureName", "")
    return details

def get_column_names():
    """Retrieve column names dynamically from the database."""
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM cheque_details LIMIT 0")
    column_names = [desc[0] for desc in cursor.description]
    cursor.close()
    connection.close()
    return column_names

# Streamlit App Pages

def home_page():
    """Render the home page with a welcome message, project overview, and user guide."""
    import streamlit as st

    # Welcome message
    st.title("Welcome to the Bank Cheque Extraction System")
    
    # Project Overview
    st.subheader("Project Overview")
    st.write("""
        **Project Title:** Automating Bank Cheque Extraction from Scanned PDFs  

        **Project Tasks:**  
        1. Reading and parsing PDF files.  
        2. Splitting files into pages and converting pages into images.  
        3. Identifying cheque borders and resizing cheques.  
        4. Extracting text using OCR and performing entity recognition.  
        5. Storing cheque details into a PostgreSQL database.  
        6. Visualizing analytics and exporting data.  
    """)

    # Instructions section
    st.subheader("How to Use the System")
    st.write("""
    ### Step-by-Step Guide:
    1. **Navigate to the Upload Page**  
       Use the sidebar to go to the "Upload" section.

    2. **Upload Your PDF or Images**  
       Select a PDF file or image containing scanned cheques. Ensure the file is clear, high-resolution, and properly aligned for best OCR results.

    3. **Extract Data with OCR**  
       Extract cheque images and text using Optical Character Recognition (OCR). The system will display the extracted details in a structured format.

    4. **Review Extracted Details**  
       Inspect the parsed cheque information, including amounts, account numbers, and payee details, in an organized table.

    5. **Analyze Data**  
       Navigate to the "Analytics" section to view summaries and visualizations, such as bar charts and pie charts, for insights into cheque data.

    6. **Export Results**  
       Download the extracted data and analysis in your preferred formats:
       - **CSV or Excel:** Download tabular data for use in spreadsheets or databases.
       - **PDF:** Export a comprehensive report of extracted details and visualizations.
       - **Chart Images (PNG):** Save visualizations like bar and pie charts as image files for presentations or reports.
       
    ---
    ### Tips for Best Results:
    - Use high-quality, properly scanned documents.
    - Ensure the file has no excessive noise or distortions.

    
    ### Next Steps:  
    Navigate using the sidebar to explore the system's features and start processing your documents.
    """)

    # Additional tip for users
    st.info("💡 Tip: Use the 'Help' button in the sidebar for troubleshooting common issues.")



def upload_page():
    """Render the Upload Page for cheque PDFs or images."""
    import streamlit as st
    import json

    st.title("Upload Cheque PDFs or Images")

    # File uploader widget
    uploaded_file = st.file_uploader(
        "Upload a PDF or image file (Supported formats: PDF, JPG, JPEG, PNG)", 
        type=["pdf", "jpg", "jpeg", "png"]
    )

    # Check if a file is uploaded
    if uploaded_file:
        st.info("File uploaded successfully. Processing will start automatically.")
        
        # Save the uploaded file
        file_path = save_uploaded_file(uploaded_file)
        progress = st.progress(0)  # Progress indicator

        if uploaded_file.type == "application/pdf":
            st.info("Converting PDF to images...")
            progress.progress(20)
            
            try:
                image_paths = convert_pdf_to_images(file_path)
                progress.progress(50)

                for image_path in image_paths:
                    st.image(image_path, caption="Extracted Image", use_container_width=True)  # Updated line
                    extracted_details = Model(image_path)
                    
                    print(extracted_details ,"here is details")
                    
                    try:
                        details = json.loads(extracted_details)
                        st.json(details)
                        progress.progress(70)

                        processed_details = preprocess_cheque_details(details)
                        insert_cheque_details(processed_details)
                        st.success("Cheque details saved to the database.")
                        progress.progress(100)
                    except Exception as e:
                        st.error(f"Error extracting details: {e}")
                        progress.empty()
                        break
            except Exception as e:
                st.error(f"Failed to process the PDF: {e}")
                progress.empty()
        else:
            # Process image file
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)  # Updated line
            extracted_details = Model(file_path)
            progress.progress(50)

            try:
                details = json.loads(extracted_details)
                st.json(details)
                progress.progress(70)

                processed_details = preprocess_cheque_details(details)
                insert_cheque_details(processed_details)
                st.success("Cheque details saved to the database.")
                progress.progress(100)
            except Exception as e:
                st.error(f"Error: {e}")
                progress.empty()

        # Clear temporary files after processing
        clear_temp_files()
    else:
        # Warning if no file is uploaded
        st.warning("Please upload a PDF or image file to start the extraction process.")




# Function to clean the amount string
def clean_amount(amount_str):
    """Remove non-numeric characters and convert to float."""
    if not amount_str or not amount_str.strip().replace(",", "").replace("/-", "").isnumeric():
        return 0.0
    return float(amount_str.replace(",", "").replace("/-", "").strip())

# Visualization Functions
def plot_pie_chart(amounts, labels):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(amounts, labels=labels, autopct='%1.1f%%', startangle=100, wedgeprops={'edgecolor': 'black'})
    ax.axis('equal')
    # ax.set_title("Top 5 Bankfgchghgh Names by Cheque Amount", fontsize=16, pad=20)
    plt.tight_layout()
    return fig

def plot_bar_chart(amounts, labels):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(labels, amounts, color='skyblue', alpha=0.7, edgecolor='black')
    ax.set_xlabel('Payee Names', fontsize=12)
    ax.set_ylabel('Amount', fontsize=12)
    ax.set_title(' Highest Cheque Amounts by Payee Name', fontsize=14, pad=10)
    ax.tick_params(axis='x', rotation=45, labelsize=10)
    plt.tight_layout()
    return fig

def plot_scatter_chart(amounts, labels):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(labels, amounts, color='green', alpha=0.7, edgecolor='black', s=100)
    ax.set_xlabel('Bank Names', fontsize=12)
    ax.set_ylabel('Cheque Amount', fontsize=12)
    ax.set_title('Cheque Amount vs Bank Name', fontsize=14, pad=10)
    ax.tick_params(axis='x', rotation=45, labelsize=10)
    plt.tight_layout()
    return fig

# Save plot as PNG in memory
def save_plot_as_png(fig):
    img_stream = io.BytesIO()
    fig.savefig(img_stream, format='png', bbox_inches='tight')
    img_stream.seek(0)
    return img_stream

# Export DataFrame as Excel
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return output

# Convert DataFrame and plots to a PDF
def convert_df_to_pdf(df, figs=None):
    output = io.BytesIO()
    c = canvas.Canvas(output, pagesize=letter)

    # Add title
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 750, "Analytics Report")
    c.setFont("Helvetica", 10)

    # Add table headers
    x, y = 50, 720
    c.setFont("Helvetica-Bold", 10)
    for header in df.columns:
        c.drawString(x, y, str(header))
        x += 100
    y -= 20

    # Add table rows
    c.setFont("Helvetica", 10)
    for _, row in df.iterrows():
        x = 50
        for value in row:
            c.drawString(x, y, str(value))
            x += 100
        y -= 20
        if y < 100:  # Add a new page if content exceeds current page
            c.showPage()
            y = 750

    # Add plots
    if figs:
        for fig in figs:
            img_path = save_plot_as_temp_png(fig)
            c.showPage()
            c.drawImage(img_path, 50, 400, width=500, height=300)
            os.remove(img_path)  # Cleanup temporary file

    c.save()
    output.seek(0)
    return output

# Save plot temporarily for PDF
def save_plot_as_temp_png(fig):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    fig.savefig(temp_file.name, format="png", bbox_inches="tight")
    return temp_file.name

# Main analytics page function

# Main analytics page function
def analytics_page():
    st.title("Analytics Dashboard")

    # Fetch and preprocess cheque details
    rows = fetch_cheque_details()  # Replace with your database fetch function

    if rows:
        df = pd.DataFrame(rows, columns=get_column_names())  # Replace with your column names
        df['amount_in_numbers'] = df['amount_in_numbers'].apply(clean_amount)
        df['amount_in_numbers'] = pd.to_numeric(df['amount_in_numbers'], errors='coerce')
        df.dropna(subset=['amount_in_numbers'], inplace=True)

        # Display aggregate data
        st.subheader("Summary Statistics")
        st.metric("Total Banks", df['bank_name'].nunique())
        st.metric("Total Cheque Amount", f"${df['amount_in_numbers'].sum():,.2f}")
        st.metric("Total Cheques", len(df))

        # Sorting and filtering options
        st.subheader("Cheque Details Table")
        sort_by = st.selectbox("Sort by", df.columns[1:], key="sort_by")
        sort_order = st.radio("Sort order", ["Ascending", "Descending"], key="sort_order")
        df = df.sort_values(by=sort_by, ascending=(sort_order == "Ascending"))
        st.dataframe(df)

        # Visualization
        st.subheader("Cheque Amount Distribution Visualizations")

        # Pie Chart
        st.subheader("Pie Chart: Top 5 Bank Names by Cheque Amount")
        pie_data = df.groupby("bank_name")["amount_in_numbers"].sum().nlargest(5).reset_index()
        pie_fig = plot_pie_chart(pie_data["amount_in_numbers"], pie_data["bank_name"])
        st.pyplot(pie_fig)
        st.download_button(
            "Download Pie Chart as PNG",
            save_plot_as_png(pie_fig).getvalue(),
            file_name="pie_chart.png"
        )

        # Bar Chart
        st.subheader("Bar Chart: Highest Cheque Amounts by Payee Name")
        bar_data = df.nlargest(5, "amount_in_numbers")
        bar_fig = plot_bar_chart(bar_data["amount_in_numbers"], bar_data["payee_name"])
        st.pyplot(bar_fig)
        st.download_button(
            "Download Bar Chart as PNG",
            save_plot_as_png(bar_fig).getvalue(),
            file_name="bar_chart.png"
        )

        # Scatter Plot
        st.subheader("Scatter Chart: Cheque Amount vs Bank Name")
        scatter_fig = plot_scatter_chart(df["amount_in_numbers"], df["bank_name"])
        st.pyplot(scatter_fig)
        st.download_button(
            "Download Scatter Chart as PNG",
            save_plot_as_png(scatter_fig).getvalue(),
            file_name="scatter_chart.png"
        )

        # Download options for full analytics
        st.subheader("Download Options")
        st.download_button(
            "Download Full Analytics as PDF",
            convert_df_to_pdf(df, figs=[pie_fig, bar_fig, scatter_fig]),
            file_name="analytics_report.pdf"
        )

        st.download_button(
            "Download Table as Excel",
            convert_df_to_excel(df),
            file_name="cheque_data.xlsx"
        )

        st.download_button(
            "Download Table as CSV",
            df.to_csv(index=False).encode('utf-8'),
            file_name="cheque_data.csv"
        )

    else:
        st.info("No data available in the database.")



# Login Page


# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "Login Page"



# Login Page Function
def login_page():
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")
    if login_button:
        if email == LOGIN_EMAIL and password == LOGIN_PASSWORD:
            st.session_state.logged_in = True
            st.session_state.page = "Home Page"
            st.success("Logged in successfully! Redirecting to the Home Page...")
        else:
            st.error("Invalid email or password!")


# Main App with Navigation
def main():
    """Main app function to handle navigation and user login."""
    import streamlit as st

    # Session state for login
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "page" not in st.session_state:
        st.session_state.page = "Login Page"

    if not st.session_state.logged_in:
        login_page()  # Redirect to login page if not logged in
    else:
        # Sidebar for navigation
        st.sidebar.title("Navigation")
        page = st.sidebar.radio("Go to", ["Home Page", "Upload Page", "Analytics Dashboard"])

        # Help Section in Sidebar
        st.sidebar.title("Help")
        with st.sidebar.expander("💡 Need Assistance?"):
            st.write("""
                - **Upload Issues:** Ensure the file is a valid PDF and not password-protected.
                - **OCR Accuracy:** Use high-quality scans for better results.
                - **Navigation:** Use the sidebar to switch between pages.
            """)
            st.info("📧 Contact support at support@example.com for further help.")

        # Page routing
        if page == "Home Page":
            home_page()
        elif page == "Upload Page":
            upload_page()
        elif page == "Analytics Dashboard":
            analytics_page()



if __name__ == "__main__":
    main()