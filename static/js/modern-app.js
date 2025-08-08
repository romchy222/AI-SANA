// Modern BolashakChat JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeTheme();
    initializeAnimations();
    initializeChat();
    initializeLanguageSelector();
});

// Theme Management
function initializeTheme() {
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const currentTheme = localStorage.getItem('theme') || 'light';
    
    // Set initial theme
    document.body.setAttribute('data-theme', currentTheme);
    updateThemeIcon(currentTheme);
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const newTheme = document.body.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
            document.body.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }
}

function updateThemeIcon(theme) {
    const themeIcon = document.getElementById('themeIcon');
    if (themeIcon) {
        themeIcon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
}

// Animations
function initializeAnimations() {
    // Intersection Observer for fade-in animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in-up');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    // Observe all feature cards and agent cards
    const animatedElements = document.querySelectorAll('.feature-card, .agent-card, .hero-content');
    animatedElements.forEach(el => observer.observe(el));
}

// Chat Functionality
function initializeChat() {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    const sendButton = document.getElementById('send-button');
    const voiceButton = document.getElementById('voice-button');
    
    if (chatForm) {
        chatForm.addEventListener('submit', handleChatSubmit);
    }
    
    if (voiceButton) {
        voiceButton.addEventListener('click', handleVoiceInput);
    }
    
    // Auto-resize textarea
    if (chatInput) {
        chatInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    }
}

async function handleChatSubmit(e) {
    e.preventDefault();
    
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    const sendButton = document.getElementById('send-button');
    
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Disable input and show loading
    chatInput.disabled = true;
    sendButton.disabled = true;
    sendButton.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>';
    
    // Add user message to chat
    addMessageToChat('user', message);
    
    // Clear input
    chatInput.value = '';
    chatInput.style.height = 'auto';
    
    try {
        // Send message to backend
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                language: getCurrentLanguage()
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Add bot response to chat
            addMessageToChat('bot', data.response, data.agent_name);
        } else {
            addMessageToChat('bot', 'Извините, произошла ошибка. Попробуйте еще раз.');
        }
        
    } catch (error) {
        console.error('Chat error:', error);
        addMessageToChat('bot', 'Ошибка соединения. Проверьте подключение к интернету.');
    }
    
    // Re-enable input
    chatInput.disabled = false;
    sendButton.disabled = false;
    sendButton.innerHTML = '<i class="fas fa-paper-plane me-1"></i>';
    chatInput.focus();
}

function addMessageToChat(sender, message, agentName = null) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    const messageElement = document.createElement('div');
    messageElement.className = `message ${sender}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'user' ? 'You' : 'AI';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    if (sender === 'bot' && agentName) {
        const agentLabel = document.createElement('div');
        agentLabel.className = 'text-muted small mb-1';
        agentLabel.textContent = agentName;
        content.appendChild(agentLabel);
    }
    
    const messageText = document.createElement('div');
    messageText.innerHTML = marked.parse(message); // Assuming marked.js is loaded
    content.appendChild(messageText);
    
    messageElement.appendChild(avatar);
    messageElement.appendChild(content);
    
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Voice Input
function handleVoiceInput() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert('Голосовой ввод не поддерживается в вашем браузере');
        return;
    }
    
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    const voiceButton = document.getElementById('voice-button');
    const chatInput = document.getElementById('chat-input');
    
    recognition.lang = getCurrentLanguage() === 'kz' ? 'kk-KZ' : 'ru-RU';
    recognition.continuous = false;
    recognition.interimResults = false;
    
    recognition.onstart = function() {
        voiceButton.innerHTML = '<i class="fas fa-microphone-slash text-danger"></i>';
        voiceButton.classList.add('recording');
    };
    
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        chatInput.value = transcript;
        chatInput.focus();
    };
    
    recognition.onend = function() {
        voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
        voiceButton.classList.remove('recording');
    };
    
    recognition.onerror = function(event) {
        console.error('Speech recognition error:', event.error);
        voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
        voiceButton.classList.remove('recording');
    };
    
    recognition.start();
}

// Language Management
function initializeLanguageSelector() {
    const languageLinks = document.querySelectorAll('[href*="lang="]');
    languageLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Close modal if open
            const modal = bootstrap.Modal.getInstance(document.getElementById('languageModal'));
            if (modal) {
                modal.hide();
            }
        });
    });
}

function getCurrentLanguage() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('lang') || 'ru';
}

// Utility Functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function formatDateTime(dateString) {
    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString(getCurrentLanguage(), options);
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Loading states for buttons
function setButtonLoading(button, loading = true) {
    if (!button) return;
    
    if (loading) {
        button.disabled = true;
        const originalText = button.innerHTML;
        button.setAttribute('data-original-text', originalText);
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Загрузка...';
    } else {
        button.disabled = false;
        const originalText = button.getAttribute('data-original-text');
        if (originalText) {
            button.innerHTML = originalText;
        }
    }
}

// Form validation helpers
function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Export functions for global use
window.BolashakChat = {
    showNotification,
    setButtonLoading,
    validateForm,
    getCurrentLanguage,
    formatDateTime
};