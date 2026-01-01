/**
 * AI Chat Assistant for Portfolio Website
 * Dynamically reads portfolio data and answers questions
 */

class ChatAssistant {
    constructor() {
        this.portfolioData = null;
        this.isOpen = false;
        this.isMinimized = false;
        this.chatHistory = [];
        
        this.init();
    }
    
    async init() {
        // Load portfolio data
        await this.loadPortfolioData();
        
        // Initialize UI elements
        this.chatButton = document.getElementById('chatButton');
        this.chatBox = document.getElementById('chatBox');
        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.chatSend = document.getElementById('chatSend');
        this.chatClose = document.getElementById('chatClose');
        this.chatMinimize = document.getElementById('chatMinimize');
        this.chatTyping = document.getElementById('chatTyping');
        
        // Event listeners - support both click and touch events for mobile
        this.chatButton.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.toggleChat();
        });
        this.chatButton.addEventListener('touchend', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.toggleChat();
        });
        
        this.chatClose.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.closeChat();
        });
        this.chatClose.addEventListener('touchend', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.closeChat();
        });
        
        this.chatMinimize.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.minimizeChat();
        });
        this.chatMinimize.addEventListener('touchend', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.minimizeChat();
        });
        
        this.chatSend.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.sendMessage();
        });
        this.chatSend.addEventListener('touchend', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.sendMessage();
        });
        
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Close chat when clicking outside on mobile
        if (window.innerWidth <= 768) {
            document.addEventListener('click', (e) => {
                if (this.isOpen && !this.chatBox.contains(e.target) && !this.chatButton.contains(e.target)) {
                    this.closeChat();
                }
            });
        }
        
        // Welcome message
        this.addWelcomeMessage();
    }
    
    async loadPortfolioData() {
        try {
            const response = await fetch('/api/portfolio-data');
            this.portfolioData = await response.json();
        } catch (error) {
            console.error('Error loading portfolio data:', error);
            this.portfolioData = {};
        }
    }
    
    addWelcomeMessage() {
        // Welcome message is already in HTML, but we can add it here if needed
    }
    
    toggleChat() {
        if (this.isOpen) {
            this.closeChat();
        } else {
            this.openChat();
        }
    }
    
    openChat() {
        this.isOpen = true;
        this.isMinimized = false;
        this.chatBox.classList.add('chat-box-open');
        this.chatBox.classList.remove('chat-box-minimized');
        this.chatButton.classList.add('chat-button-active');
        
        // Hide notification when chat is opened
        const notification = document.querySelector('.chat-notification');
        if (notification) {
            notification.classList.remove('active');
        }
        
        // Prevent body scroll on mobile when chat is open
        if (window.innerWidth <= 768) {
            document.body.style.overflow = 'hidden';
        }
        
        // Focus input with a small delay to ensure it works on mobile
        setTimeout(() => {
            this.chatInput.focus();
        }, 100);
    }
    
    closeChat() {
        this.isOpen = false;
        this.isMinimized = false;
        this.chatBox.classList.remove('chat-box-open', 'chat-box-minimized');
        this.chatButton.classList.remove('chat-button-active');
        
        // Restore body scroll on mobile
        if (window.innerWidth <= 768) {
            document.body.style.overflow = '';
        }
    }
    
    minimizeChat() {
        this.isMinimized = true;
        this.chatBox.classList.add('chat-box-minimized');
        this.chatBox.classList.remove('chat-box-open');
    }
    
    sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message) return;
        
        // Add user message
        this.addMessage(message, 'user');
        this.chatInput.value = '';
        
        // Show typing indicator
        this.showTyping();
        
        // Process message and get response
        setTimeout(() => {
            const response = this.processMessage(message);
            this.hideTyping();
            this.addMessage(response, 'assistant');
        }, 500 + Math.random() * 1000); // Simulate thinking time
    }
    
    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message chat-message-${sender}`;
        
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = `chat-bubble chat-bubble-${sender}`;
        
        const p = document.createElement('p');
        p.textContent = text;
        
        bubbleDiv.appendChild(p);
        messageDiv.appendChild(bubbleDiv);
        this.chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom with smooth behavior
        setTimeout(() => {
            this.chatMessages.scrollTo({
                top: this.chatMessages.scrollHeight,
                behavior: 'smooth'
            });
        }, 50);
        
        // Save to history
        this.chatHistory.push({ text, sender, timestamp: Date.now() });
    }
    
    showTyping() {
        this.chatTyping.style.display = 'block';
        setTimeout(() => {
            this.chatMessages.scrollTo({
                top: this.chatMessages.scrollHeight,
                behavior: 'smooth'
            });
        }, 50);
    }
    
    hideTyping() {
        this.chatTyping.style.display = 'none';
    }
    
    processMessage(message) {
        const lowerMessage = message.toLowerCase();
        
        // Greetings
        if (this.matches(lowerMessage, ['hi', 'hello', 'hey', 'greetings'])) {
            return `Hello! I'm here to help you learn about ${this.getPersonalInfo('name') || 'this portfolio'}. What would you like to know?`;
        }
        
        // About / Bio
        if (this.matches(lowerMessage, ['about', 'who are you', 'tell me about', 'bio', 'biography'])) {
            const name = this.getPersonalInfo('name');
            const title = this.getPersonalInfo('title');
            const bio = this.getPersonalInfo('bio');
            let response = '';
            if (name) response += `I'm ${name}. `;
            if (title) response += `I'm a ${title}. `;
            if (bio) response += bio;
            return response || 'I can help you learn about this portfolio. What specific information are you looking for?';
        }
        
        // Skills
        if (this.matches(lowerMessage, ['skill', 'technology', 'tech', 'what can', 'expertise', 'proficient'])) {
            const skills = this.portfolioData?.skills || [];
            if (skills.length === 0) {
                return 'Skills information is not available at the moment.';
            }
            
            // Check for specific skill query
            for (const skill of skills) {
                if (lowerMessage.includes(skill.name.toLowerCase())) {
                    return `${skill.name} - ${skill.level}% proficiency. ${skill.description || 'This is one of my key skills.'}`;
                }
            }
            
            // List top skills
            const topSkills = skills
                .sort((a, b) => b.level - a.level)
                .slice(0, 5)
                .map(s => `${s.name} (${s.level}%)`)
                .join(', ');
            
            return `I have expertise in various technologies. Top skills include: ${topSkills}. I have ${skills.length} skills in total. Would you like to know more about a specific skill?`;
        }
        
        // Projects
        if (this.matches(lowerMessage, ['project', 'work', 'portfolio', 'what have you built', 'what did you create'])) {
            const projects = this.portfolioData?.projects || [];
            if (projects.length === 0) {
                return 'Project information is not available at the moment.';
            }
            
            // Check for specific project query
            for (const project of projects) {
                if (lowerMessage.includes(project.title.toLowerCase())) {
                    return `${project.title}: ${project.description} Technologies used: ${project.technologies?.join(', ') || 'Various technologies'}.`;
                }
            }
            
            // List projects
            const projectList = projects
                .slice(0, 3)
                .map(p => p.title)
                .join(', ');
            
            return `I have ${projects.length} projects in my portfolio. Some notable ones include: ${projectList}. Would you like to know more about a specific project?`;
        }
        
        // Education
        if (this.matches(lowerMessage, ['education', 'degree', 'university', 'school', 'study', 'academic', 'qualification'])) {
            const academic = this.portfolioData?.academic || [];
            if (academic.length === 0) {
                return 'Education information is not available at the moment.';
            }
            
            const eduList = academic
                .map(e => `${e.degree} from ${e.institution} (${e.year})`)
                .join('. ');
            
            return `My educational background: ${eduList}.`;
        }
        
        // Certifications
        if (this.matches(lowerMessage, ['certification', 'certificate', 'certified', 'credential'])) {
            const certs = this.portfolioData?.certifications || [];
            if (certs.length === 0) {
                return 'I don\'t have certifications listed at the moment.';
            }
            
            const certList = certs
                .map(c => `${c.name} from ${c.issuer} (${c.date})`)
                .join('. ');
            
            return `My certifications include: ${certList}.`;
        }
        
        // Contact
        if (this.matches(lowerMessage, ['contact', 'email', 'phone', 'reach', 'get in touch', 'how to contact'])) {
            const email = this.getPersonalInfo('email');
            const phone = this.getPersonalInfo('phone');
            const location = this.getPersonalInfo('location');
            
            let response = 'You can reach me through: ';
            const contacts = [];
            if (email) contacts.push(`Email: ${email}`);
            if (phone) contacts.push(`Phone: ${phone}`);
            if (location) contacts.push(`Location: ${location}`);
            
            if (contacts.length === 0) {
                return 'Contact information is not available. Please use the contact form on the website.';
            }
            
            return response + contacts.join('. ') + '. You can also use the contact form on the website.';
        }
        
        // Social links
        if (this.matches(lowerMessage, ['github', 'linkedin', 'social', 'profile', 'follow'])) {
            const social = this.portfolioData?.personal_info?.social_links || {};
            const links = [];
            if (social.github) links.push(`GitHub: ${social.github}`);
            if (social.linkedin) links.push(`LinkedIn: ${social.linkedin}`);
            if (social.twitter) links.push(`Twitter: ${social.twitter}`);
            
            if (links.length === 0) {
                return 'Social media links are not available.';
            }
            
            return `You can find me on: ${links.join('. ')}.`;
        }
        
        // CV / Resume
        if (this.matches(lowerMessage, ['cv', 'resume', 'download', 'pdf'])) {
            return 'You can download my CV using the "Download CV" button on the homepage.';
        }
        
        // Help
        if (this.matches(lowerMessage, ['help', 'what can you do', 'what do you know'])) {
            return `I can help you learn about:
- Personal information and bio
- Skills and technologies
- Projects and work
- Education and qualifications
- Certifications
- Contact information
- Social media links

Just ask me anything about ${this.getPersonalInfo('name') || 'the portfolio'}!`;
        }
        
        // Default response
        return `I'm not sure I understand that question. I can help you learn about ${this.getPersonalInfo('name') || 'this portfolio'}'s skills, projects, education, certifications, and contact information. What would you like to know?`;
    }
    
    matches(message, keywords) {
        return keywords.some(keyword => message.includes(keyword));
    }
    
    getPersonalInfo(key) {
        return this.portfolioData?.personal_info?.[key] || null;
    }
}

// Initialize chat assistant when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.chatAssistant = new ChatAssistant();
});

