document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const chatContainer = document.getElementById("chatContainer");
  const questionInput = document.getElementById("questionInput");
  const sendButton = document.getElementById("sendButton");
  const loadingOverlay = document.getElementById("loadingOverlay");
  const exposedConcepts = document.getElementById("exposedConcepts");
  const knowledgeLevels = document.getElementById("knowledgeLevels");

  // Session ID - generate a unique ID for this session
  const sessionId = "session_" + Math.random().toString(36).substring(2, 15);

  // Event Listeners
  sendButton.addEventListener("click", handleSendMessage);
  questionInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      handleSendMessage();
    }
  });

  // Handle sending a message
  async function handleSendMessage() {
    const question = questionInput.value.trim();
    if (!question) return;

    // Add user message to the chat
    addMessageToChat("user", question);

    // Clear input field
    questionInput.value = "";

    // Show loading spinner
    loadingOverlay.classList.remove("d-none");

    try {
      // Call the API
      const response = await fetchTutorResponse(question);

      // Add tutor's response to the chat
      addMessageToChat("tutor", response.response);

      // Update student model display
      updateStudentModelDisplay(response.student_model);
    } catch (error) {
      console.error("Error:", error);
      addMessageToChat(
        "tutor",
        "Sorry, I encountered an error. Please try again."
      );
    } finally {
      // Hide loading spinner
      loadingOverlay.classList.add("d-none");

      // Scroll to bottom of chat
      scrollToBottom();
    }
  }

  // Fetch response from the tutor API
  async function fetchTutorResponse(question) {
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
      throw new Error(errorData.error || "Failed to get response");
    }

    return await response.json();
  }

  // Add a message to the chat container
  function addMessageToChat(role, text) {
    const messageDiv = document.createElement("div");
    messageDiv.className = role === "tutor" ? "tutor-message" : "user-message";

    const avatarDiv = document.createElement("div");
    avatarDiv.className = "avatar";

    const avatarImg = document.createElement("img");
    avatarImg.src =
      role === "tutor"
        ? "https://via.placeholder.com/50"
        : "https://via.placeholder.com/50/24a0ed";
    avatarImg.alt = role === "tutor" ? "Tutor Avatar" : "You";

    avatarDiv.appendChild(avatarImg);

    const messageTextDiv = document.createElement("div");
    messageTextDiv.className = "message";
    messageTextDiv.innerHTML = `<p>${text}</p>`;

    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(messageTextDiv);

    chatContainer.appendChild(messageDiv);

    // Scroll to the bottom
    scrollToBottom();
  }

  // Scroll to the bottom of the chat container
  function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }

  // Update the student model display
  function updateStudentModelDisplay(studentModel) {
    if (!studentModel) return;

    // Update exposed concepts
    exposedConcepts.innerHTML = "";
    if (studentModel.exposed_concepts.length === 0) {
      exposedConcepts.innerHTML =
        '<li class="list-group-item">No concepts explored yet</li>';
    } else {
      studentModel.exposed_concepts.forEach((concept) => {
        const li = document.createElement("li");
        li.className = "list-group-item";
        li.textContent = concept;
        exposedConcepts.appendChild(li);
      });
    }

    // Update knowledge levels
    knowledgeLevels.innerHTML = "";
    const knowledgeEntries = Object.entries(studentModel.knowledge_level);

    if (knowledgeEntries.length === 0) {
      knowledgeLevels.innerHTML = "<p>No knowledge level data yet</p>";
    } else {
      knowledgeEntries.forEach(([concept, level]) => {
        const percentage = Math.round(level * 100);

        const itemDiv = document.createElement("div");
        itemDiv.className = "knowledge-item";

        const labelDiv = document.createElement("div");
        labelDiv.className = "d-flex justify-content-between";
        labelDiv.innerHTML = `
                    <span>${concept}</span>
                    <span>${percentage}%</span>
                `;

        const progressDiv = document.createElement("div");
        progressDiv.className = "progress";
        progressDiv.innerHTML = `
                    <div class="progress-bar ${getProgressBarColor(level)}" 
                         role="progressbar" 
                         style="width: ${percentage}%" 
                         aria-valuenow="${percentage}" 
                         aria-valuemin="0" 
                         aria-valuemax="100"></div>
                `;

        itemDiv.appendChild(labelDiv);
        itemDiv.appendChild(progressDiv);
        knowledgeLevels.appendChild(itemDiv);
      });
    }
  }

  // Get the appropriate Bootstrap color class for a knowledge level
  function getProgressBarColor(level) {
    if (level < 0.3) return "bg-danger";
    if (level < 0.7) return "bg-warning";
    return "bg-success";
  }

  // Initialize - scroll to bottom of chat
  scrollToBottom();
});
