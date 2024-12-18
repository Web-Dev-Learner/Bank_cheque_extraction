import google.generativeai as genai
from dotenv import load_dotenv

from dotenv import load_dotenv
load_dotenv()


import os
from PIL import Image

load_dotenv()


api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    raise ValueError("API key is missing. Please set the GEMINI_API_KEY in the .env file.")

def Model(image_path):
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(model_name="gemini-1.5-pro")
    prompt = '''
Extract all visible text present in the bank cheque image with high accuracy. Focus on capturing key details and output them in a structured JSON object format, with the following field names and precise formatting:

payeeName: Full name of the payee.
date: The cheque issuance date in 'ddmmyyyy' format, identified accurately without variations.
chequeNumber: Unique cheque number.
accountNumber: Complete bank account number.
bankName: Full name of the bank.
branch: Branch name and location, capturing all address details.
amountInWords: Cheque amount as written in words (e.g., "Ten Thousand Only").
amountInNumbers: Cheque amount as represented in numeric form (e.g., "10000").
signatureName: Name on the signature line.
micrCode: MICR code exactly as displayed on the cheque.
ifscCode: Bank’s IFSC code.
Ensure the JSON object format is clean, with each extracted field labeled precisely by the above field names, capturing all required information accurately. Do not omit or miss any details. If a field is not found, return it as an empty string or null to maintain consistency. Structure and separate each extracted field clearly to avoid any ambiguity in the output format.
'''

    opened_image = Image.open(image_path)
    response = model.generate_content([prompt, opened_image])

    return response.text.replace("\n", "").replace("```json", "").replace("```", "")
