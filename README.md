# Probate-Data-Extractor1📄

A Streamlit web application that extracts key information from PDF probate records, including names of the deceased and personal representatives, and searches for associated real estate assets.

## 🚀 Features

- **PDF Text Extraction**: Extract raw text from uploaded PDF probate records using PyMuPDF
- **Intelligent Parsing**: Automatically identify and categorize probate notices (Estate vs Trust vs Other)
- **Entity Extraction**: Extract deceased names, personal representatives, trustees, and contact information
- **Date Recognition**: Parse dates of birth and death using regex patterns
- **Property Search**: Search for associated real estate assets (currently simulated for demonstration)
- **Data Export**: Export processed data to CSV format
- **Web Interface**: User-friendly Streamlit interface for easy PDF upload and results viewing
- **Batch Processing**: Handle multiple probate records in a single PDF

## 📋 Requirements

- **Python**: 3.10 or higher
- **Tesseract OCR**: Required for processing image-based PDFs
- **Dependencies**: All Python packages are managed through `pyproject.toml`

## 🛠️ Installation & Setup

### 1. Install UV Package Manager

If you don't have `uv` installed, install it first:

```bash
pip install uv
```

### 2. Clone the Repository

```bash
git clone <repository-url>
cd probate-data-extractor
```

### 3. Create Virtual Environment

```bash
uv venv
```

### 4. Activate Virtual Environment

**Windows:**
```bash
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### 5. Install Dependencies

```bash
uv pip install -e .
```

### 6. Install Tesseract OCR

This application requires Google's Tesseract OCR engine for processing image-based PDFs:

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**Windows:**
1. Download the installer from the [official Tesseract GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer
3. Add the Tesseract installation directory to your system's PATH

### 7. Download spaCy Language Model

```bash
python -m spacy download en_core_web_sm
```

## 🚀 Usage

### Running the Application

Once setup is complete, start the Streamlit application:

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

### How to Use

1. **Upload PDF**: Click the file uploader and select a PDF containing probate records
2. **Processing**: The app will automatically extract text and process the records
3. **Review Results**: View the extracted information in the interactive data tables
4. **Filter Data**: Focus on deceased notices (Estate/Trust types) or view all records
5. **Property Search**: The app will simulate property searches for deceased individuals
6. **Export**: Download the processed data as a CSV file

### Supported Record Types

- **Estate Notices**: Records related to deceased individuals' estates
- **Trust Notices**: Records related to trust settlements
- **Other Notices**: General probate-related documents

## 📊 Data Extraction Fields

The application extracts the following information from probate records:

- **Notice Type**: Estate, Trust, or Other
- **Deceased/Settlor Name**: Name of the deceased person or trust settlor
- **Date of Birth**: Extracted birth date when available
- **Date of Death**: Extracted death date
- **Personal Representatives/Trustees**: Names of appointed representatives
- **Representative Addresses**: Contact addresses for representatives
- **Representative Phones**: Contact phone numbers
- **Property Addresses**: Associated real estate assets (when found)

## 🔧 Configuration

### Environment Variables

No environment variables are required for basic functionality. However, you can customize the following:

- **Output Directory**: Default is `output_data/` - automatically created if it doesn't exist
- **OCR Settings**: Tesseract configuration can be modified in the code if needed

### File Structure

```
probate-data-extractor/
├── app.py                    # Main Streamlit application
├── pyproject.toml           # Project dependencies and metadata
├── uv.lock                 # Dependency lock file
├── .gitignore             # Git ignore rules
├── output_data/           # Generated output directory (auto-created)
└── README.md              # This file
```

## 🏗️ Architecture

The application consists of several key components:

1. **PDF Processing**: Uses PyMuPDF (fitz) for text extraction from PDFs
2. **Text Parsing**: Regex-based patterns for identifying probate record structures
3. **Entity Recognition**: spaCy integration for name and entity extraction
4. **Data Processing**: Pandas for data manipulation and CSV export
5. **Web Interface**: Streamlit for the user interface
6. **Asset Search**: Simulated property search functionality

### Core Functions

- `extract_text_from_uploaded_pdf()`: PDF text extraction
- `parse_probate_records()`: Main parsing logic for probate data
- `search_for_property()`: Property asset search (currently simulated)
- `_notice_type()`: Classification of notice types
- `_iter_records()`: Record segmentation from full text

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Install development dependencies: `uv pip install -e ".[dev]"`
4. Make your changes
5. Add tests for new functionality
6. Run tests: `pytest`
7. Submit a pull request

### Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to new functions
- Update this README for any new features
- Ensure all tests pass before submitting
- Add type hints for new functions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Troubleshooting

### Common Issues

**Tesseract not found:**
- Ensure Tesseract is installed and added to your PATH
- Verify installation: `tesseract --version`

**PDF processing errors:**
- Check that the PDF is not corrupted
- Ensure the PDF contains text (not just images)
- For image-based PDFs, ensure Tesseract is properly configured

**Missing dependencies:**
- Ensure all dependencies are installed: `uv pip install -e .`
- Try recreating the virtual environment if issues persist

**Streamlit issues:**
- Clear Streamlit cache: `streamlit cache clear`
- Restart the Streamlit server

### Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Search existing GitHub issues
3. Create a new issue with detailed information about your problem

## 🔄 Future Enhancements

- [ ] Integration with real property databases
- [ ] Support for additional probate jurisdictions
- [ ] Advanced OCR configuration options
- [ ] Batch processing for multiple PDFs
- [ ] API endpoints for programmatic access
- [ ] Enhanced entity recognition models
- [ ] Integration with legal research databases

## 📚 Related Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- [spaCy Documentation](https://spacy.io/docs/)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)

## 👥 Authors

- **Arbaz Alam** - *Initial work* - [erarbazalam@gmail.com](mailto:erarbazalam@gmail.com)

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- PDF processing powered by [PyMuPDF](https://pymupdf.readthedocs.io/)
- OCR capabilities from [Tesseract](https://github.com/tesseract-ocr/tesseract)
- Natural language processing by [spaCy](https://spacy.io/)
