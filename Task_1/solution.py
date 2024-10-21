import os
import xml.etree.ElementTree as ET
from io import BytesIO
from typing import Any, Dict, List

import pandas as pd
from flask import Flask, jsonify, render_template_string, request, send_file

app = Flask(__name__)

def parse_tally_xml(xml_content: str) -> List[Dict[str, Any]]:
    """
    Parse the given Tally XML content and extract receipt transactions.

    Args:
        xml_content (str): The XML content as a string.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each representing a receipt transaction.
    """
    root = ET.fromstring(xml_content)
    transactions = []

    for voucher in root.findall('.//VOUCHER'):
        vch_type = voucher.find('VOUCHERTYPENAME')
        if vch_type is not None and vch_type.text == "Receipt":
            transaction = {}
            transaction['Date'] = voucher.findtext('DATE')
            
            # Checking if it's a parent, child, or other based on specific XML elements
            if voucher.find('.//PARENTVOUCHER') is not None:
                transaction['Transaction Type'] = 'Parent'
            elif voucher.find('.//CHILDVOUCHER') is not None:
                transaction['Transaction Type'] = 'Child'
            else:
                transaction['Transaction Type'] = 'Other'

            transaction['Vch No'] = voucher.findtext('VOUCHERNUMBER') or 'NA'
            transaction['Ref No'] = voucher.findtext('REFERENCE') or 'NA'
            transaction['Ref Type'] = voucher.findtext('REFERENCETYPE') or 'NA'
            transaction['Ref Date'] = voucher.findtext('REFERENCEDATE') or 'NA'
            transaction['Debtor'] = voucher.findtext('PARTYLEDGERNAME') or 'NA'
            transaction['Ref Amount'] = voucher.findtext('.//AMOUNT') or 'NA'
            transaction['Amount'] = voucher.find('.//AMOUNT').text if voucher.find('.//AMOUNT') is not None else 'NA'
            transaction['Particulars'] = voucher.findtext('PARTYLEDGERNAME') or 'NA'
            transaction['Vch Type'] = 'Receipt'
            transaction['Amount Verified'] = 'Yes' if transaction['Amount'] != 'NA' else 'NA'

            transactions.append(transaction)

    return transactions

def save_to_excel(transactions: List[Dict[str, Any]]) -> BytesIO:
    """
    Save the given transactions to an Excel file and return the file as a BytesIO object.

    Args:
        transactions (List[Dict[str, Any]]): The list of transaction dictionaries.

    Returns:
        BytesIO: A BytesIO object containing the Excel file.
    """
    df = pd.DataFrame(transactions, columns=[
        'Date', 'Transaction Type', 'Vch No', 'Ref No', 'Ref Type',
        'Ref Date', 'Debtor', 'Ref Amount', 'Amount', 'Particulars',
        'Vch Type', 'Amount Verified'
    ])

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    
    output.seek(0)
    return output

@app.route('/')
def index() -> str:
    """
    Render the HTML upload page.

    Returns:
        str: The HTML content for the upload page.
    """
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>XML to Excel</title>
      <style>
        body {
          font-family: 'Arial', sans-serif;
          background-color: #f4f7fa;
          margin: 0;
          padding: 0;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100vh;
        }
        h1 {
          color: #333;
        }
        .drag-drop-area {
          width: 300px;
          height: 150px;
          border: 2px dashed #ccc;
          display: flex;
          justify-content: center;
          align-items: center;
          text-align: center;
          margin: 20px;
          padding: 10px;
          border-radius: 10px;
          background-color: #fff;
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
          transition: border-color 0.3s, box-shadow 0.3s;
        }
        .drag-drop-area.drag-over {
          border-color: #28a745;
          box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
        }
        #file-input {
          display: none;
        }
        button {
          cursor: pointer;
        }
        .upload-button {
          padding: 10px 20px;
          background-color: #28a745;
          color: white;
          border: none;
          border-radius: 5px;
          cursor: pointer;
          font-size: 16px;
          transition: background-color 0.3s;
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .upload-button:disabled {
          background-color: #ccc;
          cursor: not-allowed;
        }
        .upload-button:hover:not(:disabled) {
          background-color: #218838;
        }
        button:hover {
          background-color: #ddd;
        }
        .hide {
          display: none;
        }
        .browse-btn {
          background-color: #007bff;
          color: white;
          border: none;
          padding: 5px 15px;
          border-radius: 5px;
          cursor: pointer;
          transition: background-color 0.3s;
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .browse-btn:hover {
          background-color: #0056b3;
        }
        .file-name {
          font-size: 14px;
          color: #333;
          margin-top: 10px;
        }
        footer {
          position: fixed;
          bottom: 10px;
          font-size: 12px;
          color: #888;
        }
      </style>
    </head>
    <body>
      <h1>Upload XML File and Download Excel</h1>
      
      <div id="drag-drop-area" class="drag-drop-area">
        <div id="upload-instructions">Drag and drop your XML file here or <br>
        <button class="browse-btn" onclick="document.getElementById('file-input').click()">Browse</button></div>
        <div id="file-name" class="file-name hide"></div>
      </div>
      <input type="file" id="file-input" accept=".xml">

      <br><br>
      <button id="upload-button" class="upload-button" disabled>Upload</button>

      <script>
        const dragDropArea = document.getElementById('drag-drop-area');
        const fileInput = document.getElementById('file-input');
        const uploadButton = document.getElementById('upload-button');
        const uploadInstructions = document.getElementById('upload-instructions');
        const fileNameDiv = document.getElementById('file-name');
        let selectedFile = null;

        dragDropArea.addEventListener('dragover', (e) => {
          e.preventDefault();
          dragDropArea.classList.add('drag-over');
        });

        dragDropArea.addEventListener('dragleave', (e) => {
          e.preventDefault();
          dragDropArea.classList.remove('drag-over');
        });

        dragDropArea.addEventListener('drop', (e) => {
          e.preventDefault();
          dragDropArea.classList.remove('drag-over');
          selectedFile = e.dataTransfer.files[0];
          if (selectedFile && selectedFile.name.endsWith('.xml')) {
            uploadButton.disabled = false;
            uploadInstructions.classList.add('hide');
            fileNameDiv.textContent = `File: ${selectedFile.name}`;  // Show the file name
            fileNameDiv.classList.remove('hide');
          } else {
            alert("Please drop an XML file.");
            uploadButton.disabled = true;
          }
        });

        fileInput.addEventListener('change', (e) => {
          selectedFile = e.target.files[0];
          if (selectedFile && selectedFile.name.endsWith('.xml')) {
            uploadButton.disabled = false;
            uploadInstructions.classList.add('hide');
            fileNameDiv.textContent = `File: ${selectedFile.name}`;  // Show the file name
            fileNameDiv.classList.remove('hide');
          } else {
            alert("Please select an XML file.");
            uploadButton.disabled = true;
          }
        });

        uploadButton.addEventListener('click', async () => {
          if (selectedFile) {
            try {
              const formData = new FormData();
              formData.append('file', selectedFile);

              const response = await fetch('/upload', {
                method: 'POST',
                body: formData
              });

              if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = 'Receipt_Vouchers.xlsx';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);

                alert('File downloaded successfully! Click "OK" to clear the selection.');
                resetDragDropArea();
              } else {
                alert('Error: ' + (await response.text()));
              }
            } catch (error) {
              alert('Error uploading file: ' + error.message);
            }
          }
        });

        function resetDragDropArea() {
          fileInput.value = "";  // Reset file input
          selectedFile = null;
          uploadButton.disabled = true;
          uploadInstructions.classList.remove('hide');  // Show the instructions again
          fileNameDiv.classList.add('hide');  // Hide the file name
        }
      </script>

      <footer>Developed with using Flask</footer>
    </body>
    </html>
    ''')

@app.route('/upload', methods=['POST'])
def upload_file() -> str:
    """
    Handle the file upload and process the XML to generate an Excel file.
    Returns:
        str: A response containing either an error message or the Excel file download.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        transactions = parse_tally_xml(file.read())  # Read XML content
        excel_file = save_to_excel(transactions)

        return send_file(
            excel_file,
            as_attachment=True,
            download_name="Receipt_Vouchers.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
