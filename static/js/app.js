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
  const exposedConcepts = document.getElementById("exposedConcepts");
  const knowledgeLevels = document.getElementById("knowledgeLevels");
  const progressBar = document.getElementById("progressBar");
  const overallProgress = document.getElementById("overallProgress");

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

    async getStudentModel() {
      const response = await fetch(`/api/student_model/${sessionId}`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to fetch student model");
      }

      return response.json();
    },

    async getLearningPath(targetConcept) {
      const response = await fetch(
        `/api/learning_path/${sessionId}/${encodeURIComponent(targetConcept)}`
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to fetch learning path");
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

        // Update student model visualization
        if (response.student_model) {
          this.updateStudentModel(response.student_model);
        }
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

    updateStudentModel(studentModel) {
      // Update exposed concepts
      if (studentModel.exposed_concepts) {
        this.updateConcepts(studentModel.exposed_concepts);
      }

      // Update knowledge levels
      if (studentModel.knowledge_level) {
        this.updateKnowledgeLevels(studentModel.knowledge_level);
      }

      // Calculate and update overall progress
      if (studentModel.understood_concepts && studentModel.exposed_concepts) {
        const progress =
          studentModel.understood_concepts.length /
          Math.max(studentModel.exposed_concepts.length, 1);
        this.updateProgress(progress);
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
      // Convert markdown-style code blocks to HTML
      return content
        .replace(/`([^`]+)`/g, "<code>$1</code>")
        .replace(/\n/g, "<br>")
        .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
        .replace(/\*([^*]+)\*/g, "<em>$1</em>");
    },

    updateProgress(progress) {
      const percentage = Math.round(progress * 100);
      progressBar.style.width = `${percentage}%`;
      overallProgress.textContent = `${percentage}%`;
    },

    updateConcepts(concepts) {
      exposedConcepts.innerHTML = concepts
        .map(
          (concept) => `
        <div class="concept-tag">
          <span class="material-icons text-sm mr-1">check_circle</span>
          ${concept}
        </div>
      `
        )
        .join("");
    },

    updateKnowledgeLevels(levels) {
      knowledgeLevels.innerHTML = Object.entries(levels)
        .map(
          ([topic, level]) => `
        <div class="knowledge-item">
          <div class="flex justify-between items-center mb-2">
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">${topic}</span>
            <span class="text-sm text-blue-600 dark:text-blue-400">${Math.round(
              level * 100
            )}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-bar-fill" style="width: ${level * 100}%"></div>
          </div>
        </div>
      `
        )
        .join("");
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

  // Initialize with example knowledge levels
  chat.updateKnowledgeLevels({
    Mechanics: 0.7,
    Thermodynamics: 0.4,
    Electromagnetism: 0.2,
    "Quantum Physics": 0.1,
  });
});
