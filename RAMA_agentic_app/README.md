# 🏠 RAMA - Real Estate Agentic App

**RAMA** is an AI-powered assistant built for real estate investment and remodeling firms. It streamlines document handling, automates financial tracking, and supports natural language queries — all through an intuitive chat interface.

---

## ✨ Features

- 💬 **Conversational AI Interface**
  - Ask: “When do I pay Builder X?”
  - Retrieve: “Show documents for 456 Oak Ave”
  - Summarize: “What are the current properties for sale?”

- 📁 **Smart Document Management**
  - Upload renovation, purchase, and sales documents
  - Automatic classification and linking by property
  - Document search by type, status, or address

- 📊 **Financial Insights**
  - View property-level financial summaries
  - Track spending across acquisition, renovation, and sales phases

- ⚙️ **Agentic Automations**
  - Custom agents automate repetitive tasks
  - Email reminders, status updates, and more

- 🔐 **Admin Tools**
  - Custom SQL queries (admin-only)
  - Role-based access control (coming soon)

---

## 🚀 How to Run the App Locally

1. **Clone the Repository**

```bash
git clone https://github.com/mariasebarespersona/rama-app.git
cd rama-app
```

2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

3. **Run the App**

```bash
python app.py
```

4. **Access in Browser**

Go to: [http://localhost:7860](http://localhost:7860)

---

## 🧱 Project Structure

```plaintext
.
├── app.py                  # Launches the main app interface
├── agentic.py              # AI agents and routing logic
├── document_tool.py        # Document parsing, classification, and filtering
├── financial_tool.py       # Property-level financial summaries
├── requirements.txt        # Python dependencies
├── questions_rama_agentic_app.docx  # Example natural language queries
├── Business_plan_draft1.docx        # Strategy, market, and feature roadmap
```

---

## 🛤️ Roadmap

### ✅ Current Capabilities
- Chat interface with document and property queries
- Property-level status and financial summaries
- General GPT-powered real estate answers
- Document filtering by type and address

### 🔜 Coming Soon
- 🔐 Authentication & role-based access
- 📄 PDF parsing and OCR support
- 📤 Drag-and-drop document uploads with auto-classification
- ☁️ Deployment via Docker, Streamlit Sharing, Hugging Face Spaces
- 📊 Agent activity logs, user audit trail

---

## 🧪 Example Queries

```text
"What documents do we have so far?"
"Do we have any files for Calle Madrid 45?"
"How many properties are currently being renovated?"
"When was the last payment made to Builder Z?"
"What is a notary deed?"
```

---

## 🧠 Tech Stack

- **Backend**: Python, OpenAI GPT APIs
- **UI**: Gradio (local), Streamlit (optional)
- **Document Parsing**: PyMuPDF, Tesseract OCR (planned)
- **Task Automation**: Agentic logic (custom), n8n integration (planned)
- **Data Storage**: Local for dev, GDPR-compliant cloud planned
- **Security**: Role permissions, encryption, audit trail (coming)

---

## 👩‍💻 Developer

**Maria Sebares**  
Founder & Lead Developer  
Data Scientist | Agentic AI Systems | Real Estate Tech

---

## 📫 Contact

- GitHub: [https://github.com/mariasebarespersona/rama-app](https://github.com/mariasebarespersona/rama-app)
- Email: [your-email@example.com]
- Website: Coming Soon

---

## 📄 License

This project is licensed under the MIT License.  
See the full license terms below:

```text
MIT License

Copyright (c) 2025 Maria Sebares

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights  
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell  
copies of the Software, and to permit persons to whom the Software is  
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all  
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,  
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE  
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,  
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN  
THE SOFTWARE.
```

---

Feel free to submit issues or feature requests via GitHub.
