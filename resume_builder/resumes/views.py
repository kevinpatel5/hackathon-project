from django.shortcuts import render, redirect
from .forms import ResumeForm
from .models import Resume
import random 
from django.shortcuts import get_object_or_404
import requests


# Create your views here.

 # Simulate AI-based keyword suggestion


def get_ai_keywords(job_role):
    # Simulating a database of keywords related to job roles
    keywords_dict = {
        "Software Engineer": ["Python", "Java", "SQL", "Agile", "Git", "JavaScript", "C++"],
        "Data Scientist": ["Python", "Machine Learning", "Statistics", "Data Analysis", "R", "SQL", "TensorFlow"],
        "Web Developer": ["HTML", "CSS", "JavaScript", "React", "Node.js", "MongoDB", "Express"],
        "Digital Marketer": ["SEO", "Google Analytics", "Content Marketing", "AdWords", "Social Media Marketing"]
    }
    
    return keywords_dict.get(job_role, [])

#def create_resume(request):
    # if request.method == "POST":
    #     form = ResumeForm(request.POST)
    #     if form.is_valid():
    #         resume = form.save()
    #         # extract all form data for further use
    #         form_data = {
    #             "name": resume.name,
    #             "email": resume.email,
    #             "phone": resume.phone,
    #             "linkedin": resume.linkedin,
    #             "objective": resume.objective,
    #             "skills": resume.skills,
    #             "experience": resume.experience,
    #             "education": resume.education,
    #             "job_role": resume.job_role,
    #         }
    #         # Get AI-based keywords for the provided job role
    #        # suggested_keywords = get_ai_keywords(resume.job_role)
    #        # resume.skills = ', '.join(suggested_keywords)  # Suggest these skills in the resume
    #         resume.save()  # Save the updated resume
    #         print("Form Data:",form_data)
    #         return redirect('resume_list')
    # else:
    #     form = ResumeForm()
    # return render(request, 'resumes/create_resume.html', {'form': form})
def create_resume(request):
    if request.method == "POST":
        form = ResumeForm(request.POST)
        if form.is_valid():
            resume = form.save()
            # Prepare a prompt for the AI model
            prompt = (
                f"Generate an ATS-friendly professional resume for a person named {resume.name}. "
                f"Their contact details are email: {resume.email}, phone: {resume.phone}, and LinkedIn: {resume.linkedin}. "
                f"Their career objective is: {resume.objective}. They have the following skills: {resume.skills}. "
                f"Here is their work experience: {resume.experience}. "
                f"Their education background is: {resume.education}. "
                f"The job role they are interested in is {resume.job_role}. "
                f"Ensure that the resume is formatted with sections like 'Summary', 'Contact Information', 'Skills', 'Work Experience', and 'Education', and make it ATS-friendly."
                f"only generate the resume part of the resume"
)
            
            ai_generated_resume = generate_resume_with_llama(prompt)
            
            resume.ai_generated_resume = ai_generated_resume
            resume.save()
            return redirect('resume_list')
    else:
        form = ResumeForm()
    return render(request, 'resumes/create_resume.html', {'form': form})

def resume_list(request):
    resumes = Resume.objects.all()
    return render(request, 'resumes/resume_list.html', {'resumes': resumes})


# added later

def update_resume(request, pk):
    resume = get_object_or_404(Resume, pk=pk)
    if request.method == "POST":
        form = ResumeForm(request.POST, instance=resume)
        if form.is_valid():
            form.save()
            return redirect('resume_list')
    else:
        form = ResumeForm(instance=resume)
    return render(request, 'resumes/update_resume.html', {'form': form, 'resume': resume})

def delete_resume(request, pk):
    resume = get_object_or_404(Resume, pk=pk)
    if request.method == "POST":
        resume.delete()
        return redirect('resume_list')
    return render(request, 'resumes/delete_resume.html', {'resume': resume})


def generate_resume_with_llama(prompt):
    api_url = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B-Instruct"
    headers = {
        "Authorization": "Bearer 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"
    }
    data = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 500,
            "temperature": 0.7
        }
    }
    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()  
        result = response.json()
        if isinstance(result, list) and result:  
            return result[0]["generated_text"]
        return "Error: Unexpected response format from the model."
    except requests.exceptions.RequestException as e:
        print(f"Error while connecting to Hugging Face API: {e}")
        return "Error generating resume. Please try again."