# Cold Email Generator Web Application

A web-based interface for generating personalized cold emails based on job descriptions and portfolio links.

## Features

- Modern and clean user interface
- Real-time email generation using OpenAI's LLM
- Integration with portfolio database
- Copy to clipboard functionality
- Responsive design

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Required Python packages (listed in requirements.txt)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd webapp
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the webapp directory with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

5. Make sure you have the `my_portfolio.csv` file in the root directory with the following columns:
   - Techstack
   - Links

## Running the Application

1. Start the Flask development server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Usage

1. Fill in the job details:
   - Job Role
   - Experience Required
   - Required Skills (comma-separated)
   - Job Description

2. Click "Generate Email" to create a personalized cold email

3. The generated email will appear below the form

4. Click "Copy to Clipboard" to copy the email to your clipboard

## Error Handling

- If there's an error during email generation, an alert will show the error message
- Make sure your OpenAI API key is valid and properly set in the `.env` file
- Ensure the portfolio CSV file is properly formatted and accessible

## Contributing

Feel free to submit issues and enhancement requests! 