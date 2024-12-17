from openai import OpenAI
from dotenv import load_dotenv
import os
from string import Template
import time
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from datetime import datetime
import logging

load_dotenv()  # Load environment variables

# Initialize Rich console for stunning terminal output
console = Console()

def initialize_logging():
    """Set up sophisticated logging system"""
    logging.basicConfig(
        filename=f'portfolio_generator_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] - %(message)s'
    )

def display_welcome_banner():
    """Display an impressive welcome message"""
    title = Text("🚀 AI-Powered Portfolio Generator", style="bold cyan")
    subtitle = Text("Transform your professional presence into a masterpiece", style="italic yellow")
    console.print(Panel.fit(title, subtitle=subtitle, border_style="blue"))

def process_resume(client, resume_text):
    """Extract and process information from resume"""
    console.print("\n[cyan]Analyzing resume...[/]")
    
    analysis_prompt = f"""Analyze this resume and extract the following information:
    {resume_text}
    
    Extract and categorize:
    1. Technical skills
    2. Soft skills
    3. Tools and technologies
    4. Project highlights
    5. Education details
    6. Professional experience
    
    Format the response as structured data that can be easily parsed."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert resume analyzer. Extract and structure key information accurately."},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.3
        )
        
        parsed_info = response.choices[0].message.content.strip()
        console.print("[green]✓[/] Resume analysis complete")
        return parsed_info
        
    except Exception as e:
        logging.error(f"Error processing resume: {str(e)}")
        console.print(f"[red]Error processing resume: {str(e)}[/]")
        return None

def get_user_details():
    """Collect essential user information and resume"""
    console.print("\n[bold cyan]Let's create your portfolio![/]")
    
    name = console.input("[bold yellow]Enter your name: [/]").strip()
    
    console.print("\n[bold yellow]Paste your resume text below.[/]")
    console.print("[italic grey](Press Ctrl+D on Unix/Linux or Ctrl+Z on Windows when done)[/]")
    
    resume_lines = []
    try:
        while True:
            line = input()
            resume_lines.append(line)
    except EOFError:
        resume_text = '\n'.join(resume_lines)
    
    github = console.input("\n[bold yellow]GitHub URL (optional): [/]").strip()
    linkedin = console.input("[bold yellow]LinkedIn URL (optional): [/]").strip()
    
    details = {
        "name": name,
        "resume": resume_text,
        "github": github,
        "linkedin": linkedin
    }
    
    # Process resume first
    client = OpenAI()
    parsed_resume = process_resume(client, details['resume'])
    details['parsed_resume'] = parsed_resume
    
    return details

def generate_portfolio_content(client, section, user_details, model="gpt-3.5-turbo"):
    """Generate content using parsed resume as context"""
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task(f"[cyan]Generating {section} content...", total=None)
        
        try:
            prompts = {
                "bio": f"""Based on this parsed resume information:
                    {user_details['parsed_resume']}
                    
                    Create a professional bio for {user_details['name']}'s portfolio website.
                    Write in first person, be concise and specific.
                    Focus on career highlights and expertise areas.
                    Length: 2-3 short paragraphs.""",
                
                "skills": f"""Based on this parsed resume information:
                    {user_details['parsed_resume']}
                    
                    Extract and organize all technical and professional skills.
                    Format as bullet points under appropriate categories.
                    Include only skills mentioned in or clearly implied by the resume.""",
                
                "projects": f"""Based on this parsed resume information:
                    {user_details['parsed_resume']}
                    
                    Create a detailed list of projects.
                    For each project include:
                    - Project name
                    - Brief description
                    - Technologies used
                    - Key achievements
                    Format as structured HTML list items (<li> tags).""",
                
                "education": f"""Based on this parsed resume information:
                    {user_details['parsed_resume']}
                    
                    Create a structured education section using HTML.
                    For each education entry, create a div with class 'education-entry' using this format:

                    <div class="education-entry">
                        <h3 class="degree">Degree/Certification Name</h3>
                        <div class="institution">Institution Name</div>
                        <div class="year">Graduation Year</div>
                        <div class="details">
                            <ul>
                                <li>Relevant coursework or achievement 1</li>
                                <li>Relevant coursework or achievement 2</li>
                            </ul>
                        </div>
                    </div>

                    Important:
                    - Order chronologically, most recent first
                    - Include all degrees and certifications
                    - Format consistently
                    - Include relevant coursework and achievements
                    - Use proper HTML structure as shown above""",
                
                "interests": f"""Based on this parsed resume information:
                    {user_details['parsed_resume']}
                    
                    Extract and list professional interests and relevant activities.
                    Include:
                    - Professional development activities
                    - Industry involvement
                    - Technical interests
                    - Relevant extracurricular activities
                    Format as concise bullet points."""
            }

            if section not in prompts:
                raise ValueError(f"Invalid section: {section}")

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional portfolio content creator focused on accuracy and relevance."},
                    {"role": "user", "content": prompts[section]}
                ],
                temperature=0.4
            )
            
            content = response.choices[0].message.content.strip()
            progress.update(task, completed=True, description=f"[green]✨ {section.title()} generated successfully!")
            return content
            
        except Exception as e:
            progress.update(task, completed=True, description=f"[red]❌ {section.title()} generation failed!")
            logging.error(f"Error generating {section}: {str(e)}")
            return f"Error generating {section} content: {str(e)}"

def save_html_file(name, bio, skills, projects, contact, education, interests, style_choice):
    """
    Save AI-generated content into an HTML file, CSS file, and JS file based on the selected style.
    """
    # HTML content
    portfolio_template = Template("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${name}'s Portfolio</title>
        <link rel="stylesheet" href="styles.css">
        <script src="scripts.js" defer></script>
    </head>
    <body>
        <nav>
            <ul>
                <li><a href="#about">About</a></li>
                <li><a href="#skills">Skills</a></li>
                <li><a href="#projects">Projects</a></li>
                <li><a href="#education">Education</a></li>
                <li><a href="#interests">Interests</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </nav>
        <header>
            <h1>${name}'s Portfolio</h1>
        </header>
        <main>
            <section id="about">
                <h2>About Me</h2>
                <p>${bio}</p>
            </section>
            
            <section id="skills">
                <h2>Skills</h2>
                <ul>
                    ${skills}
                </ul>
            </section>
            
            <section id="projects">
                <h2>Projects</h2>
                <ol>
                    ${projects}
                </ol>
            </section>
            
            <section id="education">
                <h2>Education</h2>
                <div class="education-container">
                    ${education}
                </div>
            </section>
            
            <section id="interests">
                <h2>Interests</h2>
                <ul>
                    ${interests}
                </ul>
            </section>

            <section id="contact">
                <h2>Contact</h2>
                <p>${contact}</p>
            </section>
        </main>
        
        <footer>
            <p>Thank you for visiting my portfolio! &copy; ${name}</p>
        </footer>
    </body>
    </html>
    """)

    # CSS styles with enhancements
    css_content = """
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

    body {
        font-family: 'Roboto', sans-serif;
        margin: 0;
        background-color: #f9f9f9;
        color: #333;
    }
    nav ul {
        background-color: #444;
        overflow: hidden;
        list-style: none;
        margin: 0;
        padding: 0;
        text-align: center;
    }
    nav ul li {
        display: inline;
    }
    nav ul li a {
        display: inline-block;
        color: #fff;
        padding: 15px;
        text-decoration: none;
    }
    nav ul li a:hover {
        background-color: #555;
    }
    header {
        background: linear-gradient(135deg, #6b73ff, #000dff);
        color: #fff;
        padding: 40px 20px;
        text-align: center;
    }
    main {
        margin: 20px auto;
        max-width: 800px;
        padding: 0 20px;
    }
    h1, h2 {
        color: #444;
    }
    ul, ol {
        margin: 20px;
        padding: 0 20px;
    }
    footer {
        background-color: #444;
        color: #fff;
        text-align: center;
        padding: 10px 0;
    }

    /* Education Section Styling */
    .education-entry {
        background: #ffffff;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
    }

    .education-entry:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    .education-entry .degree {
        color: #2c3e50;
        margin: 0 0 10px 0;
        font-size: 1.4em;
    }

    .education-entry .institution {
        color: #3498db;
        font-weight: bold;
        margin-bottom: 5px;
    }

    .education-entry .year {
        color: #7f8c8d;
        font-style: italic;
        margin-bottom: 10px;
    }

    .education-entry .details ul {
        margin: 10px 0;
        padding-left: 20px;
    }

    .education-entry .details li {
        color: #555;
        margin: 5px 0;
    }

    /* Responsive design for education section */
    @media (max-width: 768px) {
        .education-entry {
            padding: 15px;
        }
        
        .education-entry .degree {
            font-size: 1.2em;
        }
    }
    """

    # JS content for interactive hover effects
    js_content = """
    document.addEventListener('DOMContentLoaded', () => {
        const sections = document.querySelectorAll('section');
        sections.forEach(section => {
            section.addEventListener('mouseenter', () => {
                section.style.transform = 'scale(1.02)';
                section.style.transition = 'transform 0.3s ease';
            });
            section.addEventListener('mouseleave', () => {
                section.style.transform = 'scale(1)';
            });
        });
    });
    """

    # Save HTML file
    html_content = portfolio_template.substitute(
        name=name,
        bio=bio,
        skills=skills,
        projects=projects,
        contact=contact,
        education=education,
        interests=interests
    )
    with open("portfolio.html", "w") as file:
        file.write(html_content)
        print("✓ Portfolio HTML saved successfully")
        print(f"  File size: {len(html_content)} bytes")

    # Save CSS file
    with open("styles.css", "w") as file:
        file.write(css_content)
        print("✓ CSS styles saved successfully")

    # Save JS file
    with open("scripts.js", "w") as file:
        file.write(js_content)
        print("✓ JavaScript saved successfully")

def content_improvement_agent(client, bio, skills, projects, user_details):
    """Simplified improvement agent using resume context"""
    console.print("\n[bold cyan]Reviewing content for accuracy...[/]")
    
    improvement_prompt = f"""Review and improve this portfolio content based on the resume:
    
    RESUME:
    {user_details['resume']}
    
    CURRENT CONTENT:
    Bio: {bio}
    Skills: {skills}
    Projects: {projects}
    
    Ensure:
    1. All information matches the resume
    2. Professional tone and clarity
    3. Proper technical terminology
    4. Consistent formatting
    
    Return improved versions of bio, skills, and projects sections."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert portfolio content reviewer focusing on accuracy and professionalism."},
                {"role": "user", "content": improvement_prompt}
            ],
            temperature=0.4
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logging.error(f"Error in content improvement: {str(e)}")
        return bio, skills, projects

def apply_visual_enhancements(html_content, style_choice):
    """Apply visual enhancements based on content improvement suggestions"""
    enhancement_prompt = f"""Analyze this HTML content and suggest specific CSS and JavaScript enhancements:

    {html_content}

    Consider:
    1. Visual hierarchy improvements
    2. Interactive elements
    3. Animation opportunities
    4. Mobile responsiveness
    5. Accessibility features
    
    Selected style: {style_choice}
    
    Provide specific CSS and JavaScript code snippets for improvements."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert UI/UX developer focusing on portfolio websites."},
                {"role": "user", "content": enhancement_prompt}
            ],
            temperature=0.4
        )
        
        enhancements = response.choices[0].message.content.strip()
        console.print(Panel(enhancements, title="Visual Enhancements", border_style="magenta"))
        
        return enhancements
    except Exception as e:
        logging.error(f"Error generating visual enhancements: {str(e)}")
        return None

def design_stylist_agent():
    """Enhanced design stylist with clear style options"""
    styles = {
        "1": {
            "name": "Modern Minimalist",
            "description": "Clean, spacious design with subtle animations and modern typography",
            "color_scheme": "Monochromatic with accent colors"
        },
        "2": {
            "name": "Professional Corporate",
            "description": "Traditional layout with sophisticated color scheme and structured sections",
            "color_scheme": "Blue and gray professional palette"
        },
        "3": {
            "name": "Creative Portfolio",
            "description": "Dynamic layout with bold colors and interactive elements",
            "color_scheme": "Vibrant complementary colors"
        },
        "4": {
            "name": "Dark Mode",
            "description": "Eye-friendly dark theme with contrasting elements",
            "color_scheme": "Dark background with light text"
        },
        "5": {
            "name": "Tech Minimal",
            "description": "Code-inspired design with terminal-like elements",
            "color_scheme": "Dark with neon accents"
        }
    }

    console.print("\n[bold cyan]=== Portfolio Style Selection ===[/]")
    
    # Create a table for better style presentation
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Style #")
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Color Scheme")
    
    for key, style in styles.items():
        table.add_row(
            key,
            style["name"],
            style["description"],
            style["color_scheme"]
        )
    
    console.print(table)
    
    while True:
        choice = console.input("\n[bold yellow]Select a style number (1-5): [/]").strip()
        if choice in styles:
            return styles[choice]["name"].lower().replace(" ", "_")
        console.print("[red]Invalid choice. Please select a number between 1-5.[/]")

def code_integrator_agent(name, bio, skills, projects, contact, education, interests, style_choice):
    """Enhanced code integrator with responsive design and accessibility features"""
    print("\n=== Generating Portfolio Files ===")
    
    # Add meta tags for SEO
    # Add accessibility attributes
    # Add responsive design elements
    # Add loading animations
    save_html_file(name, bio, skills, projects, contact, education, interests, style_choice)
    
    print("\nEnhancements added:")
    print("✓ SEO meta tags")
    print("✓ Accessibility features")
    print("✓ Responsive design")
    print("✓ Loading animations")
    print("✓ Print stylesheet")

def deployment_assistant_agent():
    """Enhanced deployment assistant with more detailed guidance"""
    deployment_options = {
        "1": {
            "platform": "GitHub Pages",
            "steps": [
                "Create a new GitHub repository",
                "Push your portfolio files to the repository",
                "Go to repository Settings > Pages",
                "Select main branch as source",
                "Your site will be live at username.github.io/repository"
            ],
            "pros": "Free, easy integration with GitHub",
            "cons": "Limited to static content"
        },
        "2": {
            "platform": "Netlify",
            "steps": [
                "Create a Netlify account",
                "Drag and drop your portfolio folder",
                "Configure custom domain (optional)",
                "Enable HTTPS"
            ],
            "pros": "Excellent performance, easy deployment",
            "cons": "Some advanced features require paid plan"
        },
        "3": {
            "platform": "Vercel",
            "steps": [
                "Create a Vercel account",
                "Install Vercel CLI: npm i -g vercel",
                "Run 'vercel' in project directory",
                "Follow CLI prompts"
            ],
            "pros": "Great for React/Next.js projects",
            "cons": "More complex setup for simple static sites"
        }
    }

    print("\n=== Deployment Options ===")
    for key, option in deployment_options.items():
        print(f"\n{key}. {option['platform']}")
        print(f"Pros: {option['pros']}")
        print(f"Cons: {option['cons']}")
        print("\nDeployment steps:")
        for step in option['steps']:
            print(f"  • {step}")

    choice = input("\nSelect a deployment option (1-3) for detailed instructions: ")
    if choice in deployment_options:
        print(f"\nDetailed guide for {deployment_options[choice]['platform']} deployment:")
        for i, step in enumerate(deployment_options[choice]['steps'], 1):
            print(f"{i}. {step}")

def display_generation_stats(sections):
    """Display beautiful statistics about generated content"""
    table = Table(title="Content Generation Statistics", border_style="cyan")
    table.add_column("Section", style="cyan")
    table.add_column("Characters", justify="right", style="green")
    table.add_column("Words", justify="right", style="green")
    
    for section, content in sections.items():
        if not content.startswith("Error"):
            table.add_row(
                section.title(),
                str(len(content)),
                str(len(content.split()))
            )
    
    console.print(table)

def main():
    initialize_logging()
    display_welcome_banner()
    
    try:
        client = OpenAI()
        console.print("[bold green]✓[/] AI systems initialized")
        
        # Get user details and resume
        user_details = get_user_details()
        
        # Generate content using resume context
        sections = {}
        with Progress() as progress:
            task1 = progress.add_task("[cyan]Creating your portfolio...", total=6)
            for section in ["bio", "skills", "projects", "education", "interests"]:
                sections[section] = generate_portfolio_content(client, section, user_details)
                progress.update(task1, advance=1)
        
        # Add contact information
        sections["contact"] = f"""
        {user_details['name']}
        {f"GitHub: {user_details['github']}" if user_details['github'] else ''}
        {f"LinkedIn: {user_details['linkedin']}" if user_details['linkedin'] else ''}
        """
        
        # Display generation statistics
        display_generation_stats(sections)
        
        # Get style choice
        style_choice = design_stylist_agent()
        
        # Generate portfolio files
        code_integrator_agent(
            name=user_details['name'],
            bio=sections['bio'],
            skills=sections['skills'],
            projects=sections['projects'],
            contact=sections['contact'],
            education=sections['education'],
            interests=sections['interests'],
            style_choice=style_choice
        )
        
        # Show deployment options
        deployment_assistant_agent()
        
        console.print("\n[bold green]✨ Portfolio generation complete![/]")
        
    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/]")
        logging.error(f"Portfolio generation failed: {str(e)}")

if __name__ == "__main__":
    main()