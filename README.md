

# Automating Bank Cheque Extraction from Scanned PDFs

This project automates the extraction of key details from scanned bank cheque images and PDFs. It utilizes Optical Character Recognition (OCR) and advanced image processing techniques to extract vital cheque information such as the payee name, cheque number, bank name, amount in words and numbers, MICR code, and more. The extracted details are then stored in a structured format for further processing.

Preview [**Video Demo**](https://drive.google.com/file/d/1auC_fv5Wb1GInphJgwB6nwOCJ3nsFvEf/view?usp=sharing) for a detailed walkthrough.

## Project Overview



### <ul>
  <li><strong>Project Tasks:</strong>
    <ul>
      <li>Upload PDF or image files (PDF, JPG, JPEG, PNG).</li>
      <li>Process uploaded files through OCR (Gemini API) to extract cheque details.</li>
      <li>Store extracted details in a PostgreSQL database.</li>
      <li>Visualize analytics of the processed cheque data.</li>
    </ul>
  </li>

  <li><strong>How to Use the System:</strong>
    <ul>
      <li><strong>Login Page</strong>: Login to the system to access the main dashboard.</li>
      <li><strong>Home Page</strong>: Contains project overview and guidance on how to use the system.
        <ul>
          <li><strong>Project Title</strong>: Automating Bank Cheque Extraction from Scanned PDFs</li>
          <li><strong>How to Use the System</strong>: Step-by-step guide for processing documents.</li>
          <li><strong>Next Steps</strong>: Navigate through the sidebar to explore features.</li>
          <li><strong>Tips for Best Results</strong>: Use high-quality, properly scanned documents.</li>
        </ul>
      </li>
      <li><strong>Upload Page</strong>: Upload PDF or image files for cheque extraction.</li>
      <li><strong>Analytics Page</strong>: View summary statistics and visualizations of the extracted cheque data.</li>
    </ul>
  </li>

  <li><strong>Upload Page:</strong>
    <ul>
      <li>Supported formats: PDF, JPG, JPEG, PNG (limit 200MB per file).</li>
      <li>The extraction process involves:
        <ul>
          <li>Converting PDF to images using PyMuPDF.</li>
          <li>Using OCR (Gemini API) to extract details.</li>
          <li>Storing data in PostgreSQL.</li>
          <li>Viewing analytics such as total cheque amounts, total cheques, and bank names.</li>
        </ul>
      </li>
    </ul>
  </li>

  <li><strong>Analytics Dashboard:</strong>
    <ul>
      <li><strong>Summary Statistics</strong>:
        <ul>
          <li>Total Banks</li>
          <li>Total Cheque Amount</li>
          <li>Total Cheques</li>
        </ul>
      </li>
      <li><strong>Cheque Details Table</strong>: Sort and filter cheque details by columns such as payee name and cheque amount.</li>
      <li><strong>Cheque Amount Distribution Visualizations</strong>:
        <ul>
          <li>Pie Chart: Top 5 Banks by Cheque Amount.</li>
          <li>Bar Chart: Payee vs Amount.</li>
          <li>Scatter Chart: Bank Name vs Amount.</li>
          <li>Download buttons for PNG images of visualizations and full analytics report in Excel, CSV, or PDF format.</li>
        </ul>
      </li>
    </ul>
  </li>
</ul>

## Tech Stack:
<ul>
  <li><strong>Backend</strong>: Python, PostgreSQL</li>
  <li><strong>Frontend</strong>: Streamlit</li>
  <li><strong>OCR</strong>: Gemini API</li>
  <li><strong>Data Processing</strong>: Pandas, Matplotlib</li>
  <li><strong>File Handling</strong>: PyMuPDF, FPDF, ReportLab</li>
  <li><strong>Database</strong>: PostgreSQL</li>
  <li><strong>Other Libraries</strong>: psycopg2-binary, xlsxwriter, google-generativeai, python-dotenv</li>
</ul>



## Usage

<ul>
  <li>Upload a scanned cheque PDF or image to extract the relevant information.</li>
  <li>View the extracted data in JSON format.</li>
  <li>Explore the analytics dashboard for statistical insights and visualizations.</li>
  <li>Download the results in multiple formats (Excel, CSV, PDF).</li>
</ul>



