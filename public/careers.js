// Careers Page JavaScript
// Job listings, search, filter, and application form handling

const jobs = [
    {
        id: 1,
        title: 'AI Research Assistant',
        department: 'AI Research',
        location: 'Remote',
        type: 'Full-time',
        summary: 'Support Thesidia AI development and research tasks. Work with cutting-edge AI systems for pattern recognition and deep research.',
        overview: 'We are seeking an AI Research Assistant to support the development and enhancement of Thesidia AI, our advanced research and pattern recognition system. You will work closely with the AI team to conduct research, analyze patterns, and contribute to the evolution of our AI capabilities.',
        responsibilities: [
            'Assist in research tasks related to AI pattern recognition and synthesis',
            'Analyze and document research findings and insights',
            'Support the development of Thesidia AI features and capabilities',
            'Conduct literature reviews and stay current with AI research trends',
            'Collaborate with the development team on AI integration',
            'Test and validate AI responses and research outputs',
            'Contribute to knowledge base development and maintenance'
        ],
        requirements: [
            'Bachelor\'s degree in Computer Science, AI, Cognitive Science, or related field',
            'Strong understanding of AI/ML concepts and research methodologies',
            'Experience with research tools and academic databases',
            'Excellent analytical and critical thinking skills',
            'Strong written and verbal communication skills'
        ],
        preferred: [
            'Master\'s degree or PhD in relevant field',
            'Experience with large language models and AI research',
            'Background in pattern recognition or knowledge synthesis',
            'Published research or contributions to AI projects'
        ],
        salary: '$60,000 - $80,000',
        benefits: 'Health insurance, remote work flexibility, professional development budget, equity options'
    },
    {
        id: 2,
        title: 'Human Development Coach',
        department: 'Community',
        location: 'Remote',
        type: 'Full-time',
        summary: 'Engage with the community, create content, and support practitioners in their development journey across the nine arts.',
        overview: 'We are looking for a Human Development Coach to engage with our community of practitioners, create educational content, and support members in their personal and professional development. You will help build meaningful connections and foster growth across diverse disciplines.',
        responsibilities: [
            'Engage with community members through forums, posts, and direct interactions',
            'Create educational content related to human development arts',
            'Moderate community discussions and ensure quality standards',
            'Develop and facilitate workshops or online sessions',
            'Support practitioners in setting and achieving development goals',
            'Build relationships with teachers, coaches, and practitioners',
            'Contribute to community guidelines and best practices'
        ],
        requirements: [
            'Bachelor\'s degree in Psychology, Education, Coaching, or related field',
            '3+ years of experience in coaching, teaching, or community engagement',
            'Strong understanding of human development principles',
            'Excellent interpersonal and communication skills',
            'Experience with online communities and social platforms'
        ],
        preferred: [
            'Certification in coaching or related discipline',
            'Experience across multiple human development arts',
            'Background in community building or social work',
            'Published content or teaching materials'
        ],
        salary: '$50,000 - $70,000',
        benefits: 'Health insurance, remote work, professional development, flexible schedule, equity options'
    },
    {
        id: 3,
        title: 'Tutor/Educator',
        department: 'Education',
        location: 'Remote',
        type: 'Part-time / Contract',
        summary: 'Develop educational content, create curriculum, and provide tutoring support for practitioners across various disciplines.',
        overview: 'We are seeking an experienced Tutor/Educator to develop educational content, create curriculum materials, and provide tutoring support for our community. You will help practitioners deepen their understanding and skills across the nine arts of human development.',
        responsibilities: [
            'Develop educational content and curriculum materials',
            'Create lesson plans, guides, and learning resources',
            'Provide one-on-one or group tutoring sessions',
            'Design assessments and learning progress tracking',
            'Collaborate with practitioners to identify learning needs',
            'Create video tutorials, written guides, and interactive content',
            'Maintain and update educational resources'
        ],
        requirements: [
            'Bachelor\'s degree in Education, relevant discipline, or equivalent experience',
            '3+ years of teaching or tutoring experience',
            'Strong curriculum development skills',
            'Excellent communication and presentation skills',
            'Ability to adapt teaching methods to diverse learners'
        ],
        preferred: [
            'Master\'s degree in Education or subject matter expertise',
            'Experience with online education platforms',
            'Background in multiple human development arts',
            'Certification in adult education or instructional design'
        ],
        salary: '$40,000 - $60,000 (pro-rated for part-time)',
        benefits: 'Flexible schedule, remote work, professional development, project-based compensation available'
    },
    {
        id: 4,
        title: 'Full-Stack Developer',
        department: 'Engineering',
        location: 'Remote',
        type: 'Full-time',
        summary: 'Build and enhance the katanx platform. Develop features, improve performance, and contribute to our technical infrastructure.',
        overview: 'We are looking for a Full-Stack Developer to join our engineering team and help build the katanx platform. You will work on both frontend and backend systems, develop new features, and contribute to the overall technical direction of the platform.',
        responsibilities: [
            'Develop and maintain frontend and backend features',
            'Build responsive, mobile-first user interfaces',
            'Design and implement API endpoints and data models',
            'Optimize application performance and scalability',
            'Collaborate with design and product teams',
            'Write clean, maintainable, and well-documented code',
            'Participate in code reviews and technical discussions'
        ],
        requirements: [
            'Bachelor\'s degree in Computer Science or equivalent experience',
            '3+ years of full-stack development experience',
            'Proficiency in JavaScript, Python, HTML, CSS',
            'Experience with modern web frameworks (React, Vue, or similar)',
            'Experience with backend frameworks (Flask, Django, or similar)',
            'Strong understanding of databases and data modeling',
            'Experience with version control (Git)'
        ],
        preferred: [
            'Experience with Flask and Python backend development',
            'Familiarity with AI/ML integration',
            'Experience with social media platforms or community features',
            'Knowledge of security best practices',
            'Experience with cloud platforms (AWS, Railway, Vercel)'
        ],
        salary: '$80,000 - $120,000',
        benefits: 'Health insurance, remote work, flexible schedule, professional development, equity options, hardware budget'
    },
    {
        id: 5,
        title: 'Social Media Marketing Specialist',
        department: 'Marketing',
        location: 'Remote',
        type: 'Full-time',
        summary: 'Develop and execute content strategy, grow our community, and build brand awareness across social media platforms.',
        overview: 'We are seeking a Social Media Marketing Specialist to develop and execute our content strategy, grow our community, and build brand awareness. You will create engaging content, manage social media accounts, and help spread the word about katanx.',
        responsibilities: [
            'Develop and execute social media content strategy',
            'Create engaging content for multiple platforms (Twitter, Instagram, LinkedIn, etc.)',
            'Manage social media accounts and community engagement',
            'Analyze metrics and optimize content performance',
            'Collaborate with community and product teams',
            'Build relationships with influencers and practitioners',
            'Monitor trends and adapt strategy accordingly'
        ],
        requirements: [
            'Bachelor\'s degree in Marketing, Communications, or related field',
            '2+ years of social media marketing experience',
            'Strong content creation skills (writing, design, video)',
            'Experience with social media analytics and tools',
            'Excellent communication and creative skills',
            'Understanding of community building and engagement'
        ],
        preferred: [
            'Experience with human development, arts, or practitioner communities',
            'Graphic design or video editing skills',
            'Experience with growth marketing and community building',
            'Knowledge of SEO and content marketing',
            'Portfolio of successful social media campaigns'
        ],
        salary: '$45,000 - $65,000',
        benefits: 'Health insurance, remote work, flexible schedule, professional development, equity options, content creation budget'
    }
];

// DOM Elements
const searchInput = document.getElementById('searchInput');
const searchButton = document.getElementById('searchButton');
const departmentFilter = document.getElementById('departmentFilter');
const locationFilter = document.getElementById('locationFilter');
const clearFiltersBtn = document.getElementById('clearFilters');
const jobsGrid = document.getElementById('jobsGrid');
const noResults = document.getElementById('noResults');
const jobModal = document.getElementById('jobModal');
const applicationModal = document.getElementById('applicationModal');
const applicationForm = document.getElementById('applicationForm');
const successMessage = document.getElementById('successMessage');
const errorMessage = document.getElementById('errorMessage');

let currentJob = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    renderJobs(jobs);
    
    // Event listeners
    searchInput.addEventListener('input', filterJobs);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            filterJobs();
        }
    });
    searchButton.addEventListener('click', filterJobs);
    departmentFilter.addEventListener('change', filterJobs);
    locationFilter.addEventListener('change', filterJobs);
    clearFiltersBtn.addEventListener('click', clearFilters);
    
    // Modal close buttons
    document.getElementById('closeModal').addEventListener('click', closeJobModal);
    document.getElementById('closeApplicationModal').addEventListener('click', closeApplicationModal);
    document.getElementById('showApplicationForm').addEventListener('click', showApplicationForm);
    
    // Close modals on outside click
    jobModal.addEventListener('click', (e) => {
        if (e.target === jobModal) closeJobModal();
    });
    applicationModal.addEventListener('click', (e) => {
        if (e.target === applicationModal) closeApplicationModal();
    });
    
    // Form submission
    applicationForm.addEventListener('submit', handleApplicationSubmit);
});

// Render jobs
function renderJobs(jobsToRender) {
    if (jobsToRender.length === 0) {
        jobsGrid.style.display = 'none';
        noResults.style.display = 'block';
        return;
    }
    
    jobsGrid.style.display = 'grid';
    noResults.style.display = 'none';
    
    // Use DocumentFragment for better performance
    const fragment = document.createDocumentFragment();
    const tempDiv = document.createElement('div');
    
    jobsToRender.forEach(job => {
        const jobCard = document.createElement('div');
        jobCard.className = 'job-card';
        jobCard.dataset.jobId = job.id;
        jobCard.innerHTML = `
            <h3 class="job-title">${job.title}</h3>
            <div class="job-meta">
                <span>${job.department}</span>
                <span>${job.location}</span>
                <span>${job.type}</span>
            </div>
            <p class="job-summary">${job.summary}</p>
            <a href="#" class="job-view-details" data-job-id="${job.id}">View Details →</a>
        `;
        
        // Add click listener directly
        jobCard.addEventListener('click', (e) => {
            e.preventDefault();
            if (e.target.classList.contains('job-view-details') || e.target.closest('.job-card')) {
                showJobDetails(job.id);
            }
        });
        
        fragment.appendChild(jobCard);
    });
    
    jobsGrid.innerHTML = '';
    jobsGrid.appendChild(fragment);
}

// Filter jobs
function filterJobs() {
    const searchTerm = searchInput.value.toLowerCase();
    const department = departmentFilter.value;
    const location = locationFilter.value;
    
    const filtered = jobs.filter(job => {
        const matchesSearch = !searchTerm || 
            job.title.toLowerCase().includes(searchTerm) ||
            job.summary.toLowerCase().includes(searchTerm) ||
            job.department.toLowerCase().includes(searchTerm);
        
        const matchesDepartment = !department || job.department === department;
        const matchesLocation = !location || job.location === location;
        
        return matchesSearch && matchesDepartment && matchesLocation;
    });
    
    renderJobs(filtered);
}

// Clear filters
function clearFilters() {
    searchInput.value = '';
    departmentFilter.value = '';
    locationFilter.value = '';
    filterJobs();
}

// Show job details
function showJobDetails(jobId) {
    currentJob = jobs.find(job => job.id === jobId);
    if (!currentJob) return;
    
    document.documentElement.classList.add('modal-open');
    document.body.classList.add('modal-open');
    document.getElementById('modalJobTitle').textContent = currentJob.title;
    
    const detailsHTML = `
        <div class="modal-section">
            <p><strong>Department:</strong> ${currentJob.department}</p>
            <p><strong>Location:</strong> ${currentJob.location}</p>
            <p><strong>Type:</strong> ${currentJob.type}</p>
            <p><strong>Salary:</strong> ${currentJob.salary}</p>
        </div>
        
        <div class="modal-section">
            <h3>Overview</h3>
            <p>${currentJob.overview}</p>
        </div>
        
        <div class="modal-section">
            <h3>Key Responsibilities</h3>
            <ul>
                ${currentJob.responsibilities.map(resp => `<li>${resp}</li>`).join('')}
            </ul>
        </div>
        
        <div class="modal-section">
            <h3>Required Qualifications</h3>
            <ul>
                ${currentJob.requirements.map(req => `<li>${req}</li>`).join('')}
            </ul>
        </div>
        
        <div class="modal-section">
            <h3>Preferred Qualifications</h3>
            <ul>
                ${currentJob.preferred.map(pref => `<li>${pref}</li>`).join('')}
            </ul>
        </div>
        
        <div class="modal-section">
            <h3>Benefits</h3>
            <p>${currentJob.benefits}</p>
        </div>
    `;
    
    document.getElementById('jobDetails').innerHTML = detailsHTML;
    jobModal.classList.add('active');
}

// Close job modal
function closeJobModal() {
    jobModal.classList.remove('active');
    document.documentElement.classList.remove('modal-open');
    document.body.classList.remove('modal-open');
    currentJob = null;
}

// Show application form
function showApplicationForm() {
    if (!currentJob) return;
    
    document.getElementById('applicationJobTitle').value = currentJob.title;
    jobModal.classList.remove('active');
    applicationModal.classList.add('active');
    document.documentElement.classList.add('modal-open');
    document.body.classList.add('modal-open');
    applicationForm.reset();
    successMessage.classList.remove('active');
    errorMessage.classList.remove('active');
}

// Close application modal
function closeApplicationModal() {
    applicationModal.classList.remove('active');
    document.documentElement.classList.remove('modal-open');
    document.body.classList.remove('modal-open');
}

// Handle application submit
async function handleApplicationSubmit(e) {
    e.preventDefault();
    
    const submitBtn = document.getElementById('submitApplication');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';
    
    successMessage.classList.remove('active');
    errorMessage.classList.remove('active');
    
    const formData = new FormData(applicationForm);
    const resumeFile = document.getElementById('applicantResume').files[0];
    
    if (!resumeFile) {
        errorMessage.textContent = 'Please upload your resume/CV.';
        errorMessage.classList.add('active');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Application';
        return;
    }
    
    // Create email body
    const emailBody = `
Job Application: ${formData.get('jobTitle')}

Applicant Information:
- Name: ${formData.get('name')}
- Email: ${formData.get('email')}
- Phone: ${formData.get('phone') || 'Not provided'}
- Portfolio: ${formData.get('portfolio') || 'Not provided'}

Cover Letter:
${formData.get('coverLetter')}

---
This application was submitted through the katanx careers page.
    `.trim();
    
    // Create mailto link (fallback if API not available)
    const subject = encodeURIComponent(`Job Application: ${formData.get('jobTitle')}`);
    const body = encodeURIComponent(emailBody);
    const mailtoLink = `mailto:jack@praxislabs.technology?subject=${subject}&body=${body}`;
    
    // Try to submit via API if available
    try {
        const response = await fetch('/api/careers/apply', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            successMessage.textContent = 'Thank you! Your application has been submitted successfully. We will review it and get back to you soon.';
            successMessage.classList.add('active');
            applicationForm.reset();
            
            setTimeout(() => {
                closeApplicationModal();
            }, 3000);
        } else {
            throw new Error('API submission failed');
        }
    } catch (error) {
        // Fallback to mailto
        window.location.href = mailtoLink;
        
        successMessage.textContent = 'Your application is being prepared. If your email client didn\'t open, please send your application to careers@katanx.com';
        successMessage.classList.add('active');
        
        // Note: In a real implementation, you'd want to handle file attachments differently
        // For now, we'll use mailto as a fallback
    }
    
    submitBtn.disabled = false;
    submitBtn.textContent = 'Submit Application';
}

