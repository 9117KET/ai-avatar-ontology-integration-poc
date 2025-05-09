/**
 * Frontend application logic for the Physics Tutor.
 *
 * This module handles:
 * - User interaction with the chat interface
 * - Communication with the backend API
 * - Rendering tutor responses
 * - Visualizing the student model data
 * - Updating the UI based on learning progress
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
      message.innerHTML = `<p>${this.formatMessage(content)}</p>`;

      messageDiv.appendChild(type === "user" ? message : avatar);
      messageDiv.appendChild(type === "user" ? avatar : message);

      chatContainer.appendChild(messageDiv);
      chatContainer.scrollTop = chatContainer.scrollHeight;
    },

    formatMessage(content) {
      // Convert Markdown-like syntax to HTML
      return content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold
        .replace(/\*(.*?)\*/g, '<em>$1</em>')         // Italic
        .replace(/\n/g, '<br>')                      // Line breaks
        .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>'); // Code blocks
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

  // Initialize chat
});
