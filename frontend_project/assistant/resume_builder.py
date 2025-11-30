import os
from datetime import datetime
from speech import speak, takecommand
from ai import ask_ai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from PIL import Image as PILImage, ImageDraw

# ---------------------------------------------------------
# AI Resume Builder 2.0 – Smart + Designed PDF
# ---------------------------------------------------------
def build_resume(lang="en"):
    try:
        speak("Sure! Let's create your professional resume with design.", lang)

        # -----------------------------
        # Collect Details
        # -----------------------------
        speak("What is your full name?", lang)
        name = takecommand(lang).title()

        speak("Please tell me your email or contact number.", lang)
        contact = takecommand(lang)

        speak("Which company or job are you applying for?", lang)
        company = takecommand(lang)

        speak("Please provide your LinkedIn profile link or username. If you don’t have one, say no.", lang)
        linkedin = takecommand(lang)

        speak("Would you like to add your picture? Please say the picture filename if available.", lang)
        picture_name = takecommand(lang)

        speak("Tell me something about yourself or your career objective.", lang)
        objective = takecommand(lang)

        speak("Now, tell me your highest qualification and institution.", lang)
        education = takecommand(lang)

        speak("Do you have any certifications or online courses?", lang)
        certifications = takecommand(lang)

        speak("List your top technical or professional skills.", lang)
        skills = takecommand(lang)

        speak("Any projects or achievements you want to highlight?", lang)
        projects = takecommand(lang)

        speak("Do you have any work experience? If not, just say no.", lang)
        experience = takecommand(lang)

        # -----------------------------
        # Combine all info for AI
        # -----------------------------
        user_data = f"""
        Name: {name}
        Contact: {contact}
        Company: {company}
        LinkedIn: {linkedin}
        Objective: {objective}
        Education: {education}
        Certifications: {certifications}
        Skills: {skills}
        Projects: {projects}
        Experience: {experience}
        """

        speak("Generating your professional resume using AI.", lang)

        ai_prompt = f"""
        You are a professional resume writer and designer.
        Using the following details, write a clean, concise, and ATS-friendly resume for the user.
        The tone should be confident and professional.
        Add sections: Summary, Education, Skills, Certifications, Projects, and Experience.
        Emphasize relevance to the company: {company}.
        Details:\n{user_data}
        """

        response, _ = ask_ai(ai_prompt)
        resume_text = response

        # -----------------------------
        # PDF Output Setup
        # -----------------------------
        folder = os.path.join("resume")
        os.makedirs(folder, exist_ok=True)

        filename = f"Resume_{name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(folder, filename)

        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        # Header Section Style
        header_style = ParagraphStyle(
            'Header',
            fontSize=18,
            textColor=colors.white,
            alignment=TA_CENTER,
            spaceAfter=12,
            leading=22,
        )

        # Body Text Style
        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            spaceAfter=10,
            alignment=TA_LEFT,
        )

        # Section Title Style
        section_title = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            textColor=colors.HexColor("#007ACC"),
            spaceAfter=8,
        )

        # Draw colored header background (top bar)
        elements.append(Paragraph(f"<b>{name}</b>", header_style))
        elements.append(Paragraph(contact, body_style))
        if linkedin.lower() != "no":
            elements.append(Paragraph(f"LinkedIn: {linkedin}", body_style))
        elements.append(Spacer(1, 12))

        # Try adding picture if found
        resume_name = name.replace(" ", "_")  # Default fallback resume name

        if picture_name and picture_name.lower() != "no":
            try:
                # Auto-add .png if user said only the name
                if not picture_name.lower().endswith((".png", ".jpg", ".jpeg")):
                    picture_name = picture_name + ".png"

                img_path = os.path.join("backend", "photos", picture_name)

                # Retry if not found
                if not os.path.exists(img_path):
                    speak(f"I couldn't find {picture_name} in the photos folder. Please say the picture name again.",
                          lang)
                    new_name = takecommand(lang)
                    if new_name and new_name.lower() != "none":
                        if not new_name.lower().endswith((".png", ".jpg", ".jpeg")):
                            new_name = new_name + ".png"
                        img_path = os.path.join("backend", "photos", new_name)
                        picture_name = new_name  # Update name

                if os.path.exists(img_path):
                    # Create circular photo
                    with PILImage.open(img_path).convert("RGBA") as im:
                        im = im.resize((160, 160))

                        # Create circular mask
                        mask = PILImage.new("L", im.size, 0)
                        draw = ImageDraw.Draw(mask)
                        draw.ellipse((0, 0, im.size[0], im.size[1]), fill=255)

                        # Apply mask to image
                        circular_img = PILImage.new("RGBA", im.size, (0, 0, 0, 0))
                        circular_img.paste(im, (0, 0), mask=mask)

                        # Save temporary circular image
                        temp_img_path = os.path.join("photos", "temp_circular.png")
                        circular_img.save(temp_img_path, format="PNG")

                    # Add circular image to resume
                    elements.append(Image(temp_img_path, width=120, height=120))
                    elements.append(Spacer(1, 12))

                    # Resume filename same as picture name (without extension)
                    resume_name = os.path.splitext(os.path.basename(picture_name))[0]

                else:
                    speak("Still couldn’t find the image. I’ll continue without it.", lang)

            except Exception as e:
                print(f"Image error: {e}")
                speak("Couldn't add the picture. Proceeding without it.", lang)

        # Fallback resume file name if no picture found
        filename = f"{resume_name}_Resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(folder, filename)
        # Add sectioned AI text
        elements.append(Paragraph(f"<b>Applying for:</b> {company}", section_title))
        elements.append(Spacer(1, 8))

        for line in resume_text.split("\n"):
            if line.strip():
                # Highlight section headers (like "Education:", "Skills:" etc.)
                if line.strip().endswith(":") or line.strip().lower().startswith(("education", "skills", "experience", "projects", "certifications", "summary", "objective")):
                    elements.append(Paragraph(f"<b>{line.strip()}</b>", section_title))
                else:
                    elements.append(Paragraph(line.strip(), body_style))

        doc.build(elements)

        speak(f"Your resume for {company} has been created successfully and saved as {filename}.", lang)
        print(f"✅ Resume saved at: {filepath}")

        return filepath

    except Exception as e:
        print(f"Resume builder error: {e}")
        speak("Sorry, I couldn’t build the resume right now.", lang)
