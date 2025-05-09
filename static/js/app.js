/**
 * Frontend application logic for the Physics Tutor.
 *
 * This module handles:
 * - User interaction with the chat interface
 * - Communication with the backend API
 * - Rendering tutor responses with physics-optimized formatting
 * - Theme switching and UI responsiveness
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const chatContainer = document.getElementById("chatContainer");
  const questionInput = document.getElementById("questionInput");
  const sendButton = document.getElementById("sendButton");
  const loadingOverlay = document.getElementById("loadingOverlay");
  const themeToggle = document.getElementById("themeToggle");

  // Generate a session ID for this conversation
  const sessionId = "session_" + Math.random().toString(36).substring(2, 15);

  // Theme Management
  const theme = {
    init() {
      // Check for saved theme preference or system preference
      const savedTheme = localStorage.getItem("theme");
      const systemDark = window.matchMedia(
        "(prefers-color-scheme: dark)"
      ).matches;

      if (savedTheme === "dark" || (!savedTheme && systemDark)) {
        document.documentElement.classList.add("dark");
        this.updateThemeIcon(true);
      } else {
        document.documentElement.classList.remove("dark");
        this.updateThemeIcon(false);
      }

      // Listen for system theme changes
      window
        .matchMedia("(prefers-color-scheme: dark)")
        .addEventListener("change", (e) => {
          if (!localStorage.getItem("theme")) {
            if (e.matches) {
              document.documentElement.classList.add("dark");
              this.updateThemeIcon(true);
            } else {
              document.documentElement.classList.remove("dark");
              this.updateThemeIcon(false);
            }
          }
        });
    },

    toggle() {
      if (document.documentElement.classList.contains("dark")) {
        document.documentElement.classList.remove("dark");
        localStorage.setItem("theme", "light");
        this.updateThemeIcon(false);
      } else {
        document.documentElement.classList.add("dark");
        localStorage.setItem("theme", "dark");
        this.updateThemeIcon(true);
      }
    },

    updateThemeIcon(isDark) {
      const icon = themeToggle.querySelector(".material-icons");
      icon.textContent = isDark ? "light_mode" : "dark_mode";
      icon.className = `material-icons ${
        isDark ? "text-yellow-400" : "text-gray-600"
      }`;
    },
  };

  // API Management
  const api = {
    async fetchTutorResponse(question) {
      const response = await fetch("/api/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Network response was not ok");
      }

      return response.json();
    },
  };

  // Chat Management
  const chat = {
    async sendMessage(message) {
      // Add user message to chat
      this.addMessage(message, "user");

      // Show loading state
      loadingOverlay.classList.remove("hidden");
      loadingOverlay.classList.add("flex");

      try {
        // Get tutor's response
        const response = await api.fetchTutorResponse(message);
        this.addMessage(response.response, "tutor");
      } catch (error) {
        console.error("Error:", error);
        this.addMessage(
          "Sorry, I encountered an error. Please try again.",
          "tutor"
        );
      } finally {
        loadingOverlay.classList.add("hidden");
        loadingOverlay.classList.remove("flex");
      }
    },

    addMessage(content, type) {
      const messageDiv = document.createElement("div");
      messageDiv.className = `${type}-message`;

      const avatar = document.createElement("div");
      avatar.className = "avatar";

      // Use Material Icons instead of images
      const icon = document.createElement("span");
      icon.className = `material-icons avatar-icon ${
        type === "tutor"
          ? "text-blue-600 dark:text-blue-400"
          : "text-gray-600 dark:text-gray-400"
      }`;
      icon.textContent = type === "tutor" ? "smart_toy" : "person";
      avatar.appendChild(icon);

      const message = document.createElement("div");
      message.className = "message";
      
      // Apply our enhanced formatting
      message.innerHTML = this.formatMessage(content);
      
      // Add special treatment for tutor messages with physics content
      if (type === "tutor") {
        this.processMathAndPhysics(message);
      }

      messageDiv.appendChild(type === "user" ? message : avatar);
      messageDiv.appendChild(type === "user" ? avatar : message);

      chatContainer.appendChild(messageDiv);
      
      // Smooth scroll to bottom with animation
      setTimeout(() => {
        chatContainer.scrollTo({
          top: chatContainer.scrollHeight,
          behavior: 'smooth'
        });
      }, 50);
    },
    
    processMathAndPhysics(messageElement) {
      // This function could be expanded in the future to add interactivity 
      // to physics formulas, like showing explanations on hover
      
      // Find all formula elements
      const formulas = messageElement.querySelectorAll('.formula');
      formulas.forEach(formula => {
        // Add any special processing for formulas here
        formula.title = "Physics Formula";
      });
      
      // Process physics terms
      const terms = messageElement.querySelectorAll('.physics-term');
      terms.forEach(term => {
        term.title = "Important Physics Concept";
      });
    },

    formatMessage(content) {
      // Convert Markdown-like syntax to HTML with physics enhancements
      let formatted = content
        // Basic Markdown
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold
        .replace(/\*(.*?)\*/g, '<em>$1</em>')            // Italic
        .replace(/\n\n/g, '</p><p>')                    // Paragraphs
        .replace(/\n/g, '<br>')                         // Line breaks
        
        // Physics-specific formatting
        .replace(/\$([^$]+)\$/g, '<span class="formula">$1</span>')  // Inline formulas
        .replace(/\{\{([^}]+)\}\}/g, '<span class="physics-term">$1</span>') // Physics terms
        
        // Lists
        .replace(/^\s*-(.*)/gm, '<li>$1</li>')           // Unordered lists
        .replace(/<\/li>\s*<li>/g, '</li><li>')         // Fix adjacent list items
        
        // Code blocks with syntax highlighting hint
        .replace(/```([a-z]*)\n([\s\S]*?)```/g, function(match, lang, code) {
          return `<pre><code class="${lang}">${code.trim()}</code></pre>`;
        })
        
        // Inline code
        .replace(/`([^`]+)`/g, '<code>$1</code>');
      
      // Wrap in paragraph if not already wrapped
      if (!formatted.startsWith('<p>')) {
        formatted = '<p>' + formatted;
      }
      if (!formatted.endsWith('</p>')) {
        formatted = formatted + '</p>';
      }
      
      return formatted;
    },
  };

  // Event Listeners
  theme.init();

  themeToggle.addEventListener("click", () => {
    theme.toggle();
  });

  sendButton.addEventListener("click", () => {
    const message = questionInput.value.trim();
    if (message) {
      chat.sendMessage(message);
      questionInput.value = "";
    }
  });

  questionInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendButton.click();
    }
  });
  
  // Set up suggested question buttons
  const suggestionButtons = document.querySelectorAll('.suggestion-btn');
  suggestionButtons.forEach(button => {
    button.addEventListener('click', () => {
      const question = button.textContent.trim();
      questionInput.value = question;
      
      // Briefly highlight the input to show it's been populated
      questionInput.classList.add('bg-blue-50', 'dark:bg-blue-900/20');
      setTimeout(() => {
        questionInput.classList.remove('bg-blue-50', 'dark:bg-blue-900/20');
        sendButton.click(); // Automatically send the suggested question
      }, 200);
    });
  });

  // Initialize chat
});
