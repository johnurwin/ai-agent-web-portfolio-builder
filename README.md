# 🚀 AI Portfolio Builder

**AI Portfolio Builder** is a command-line tool that uses OpenAI’s GPT models to help you generate a professional portfolio website automatically. The script asks you for your resume as an input, collects your details, generates content, improves it for clarity and professionalism, and creates a polished portfolio website with clean HTML, CSS, and JS files.

---

## 📋 Features

- **AI Content Generation**: Generates professional content for:
  - Bio
  - Skills
  - Projects
  - Education
  - Interests
  - Contact Information
- **Content Improvement**: Automatically refines your content for clarity and professionalism.
- **Customizable Styles**: Choose between `Modern`, `Classic`, or `Dark` CSS themes.
- **Code Integration**: Generates clean HTML, CSS, and JavaScript files.
- **Deployment Guidance**: Provides instructions for deploying your portfolio to GitHub Pages, Netlify, or Vercel.

---

## ⚙️ Requirements

- Python 3.8+
- OpenAI API Key (sign up at [OpenAI](https://platform.openai.com/))
- Required Python packages:
  - `openai`
  - `python-dotenv`

---

## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ai-agent-web-portfolio-builder.git
   cd ai-portfolio-builder

## Explanation

The code for the app is on the master branch in main.py and the output files for the example that I performed are in portfolio.html, styles.css and scripts.js.  The code, when run correctly with your Openai API key, will automatically create these same files for you, but using the inputs from your resume.  This is an AI agent because of the multiple calls to different OpenAI models.
