document.addEventListener("DOMContentLoaded", () => {
  // --- DOM Elements ---
  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");
  const loginFormContainer = document.getElementById("login-form-container");
  const registerFormContainer = document.getElementById(
    "register-form-container"
  );
  const showRegisterLink = document.getElementById("show-register");
  const showLoginLink = document.getElementById("show-login");

  const authForms = document.getElementById("auth-forms");
  const chatContainer = document.getElementById("chat-container");
  const chatBox = document.getElementById("chat-box");
  const messageInput = document.getElementById("message-input");
  const sendButton = document.getElementById("send-button");
  const logoutButton = document.getElementById("logout-button");
  const userInfo = document.getElementById("user-info");

  const loginError = document.getElementById("login-error");
  const registerError = document.getElementById("register-error");
  const registerSuccess = document.getElementById("register-success");
  const chatError = document.getElementById("chat-error");

  const resultsPopup = document.getElementById("results-popup");
  const resultsContent = document.getElementById("results-content");
  const newTestButton = document.getElementById("new-test-button");
  const emergencyContactButton = document.getElementById(
    "emergency-contact-button"
  );

  const dashboardContainer = document.getElementById("dashboard-container");
  const testCards = document.querySelectorAll(".test-card");
  const addContactBtn = document.getElementById("addContactBtn");

  // Add Chart.js script dynamically
  const chartScript = document.createElement("script");
  chartScript.src = "https://cdn.jsdelivr.net/npm/chart.js";
  document.head.appendChild(chartScript);

  // --- State ---
  let bearerToken = localStorage.getItem("bearerToken");
  let chatInitialized = false; // Track if /chat/start has been called successfully

  // --- Utility Functions ---
  const clearErrors = () => {
    loginError.textContent = "";
    registerError.textContent = "";
    registerSuccess.textContent = "";
    chatError.textContent = "";
  };

  const displayError = (element, message) => {
    clearErrors();
    element.textContent = message;
  };

  const showView = (view) => {
    authForms.style.display = "none";
    chatContainer.style.display = "none";
    dashboardContainer.style.display = "none";
    if (view === "auth") {
      authForms.style.display = "flex"; // Use flex for centering
    } else if (view === "chat") {
      chatContainer.style.display = "flex"; // Use flex for layout
    } else if (view === "dashboard") {
      dashboardContainer.style.display = "block";
    }
  };

  const scrollToBottom = () => {
    chatBox.scrollTop = chatBox.scrollHeight;
  };

  const addMessageToChat = (sender, message) => {
    const messageElement = document.createElement("div");
    messageElement.classList.add("message", sender);

    if (message.includes("Assessment Complete")) {
      const parts = message.split("\n");
      let formattedMessage = '<div class="assessment-results">';

      // Main Results Section
      formattedMessage += '<div class="main-results">';
      const scoreLine = parts.find((line) => line.startsWith("Score:"));
      if (scoreLine) {
        formattedMessage += `<div class="result-score">${scoreLine}</div>`;
      }
      const severityLine = parts.find((line) => line.startsWith("Severity:"));
      if (severityLine) {
        const severity = severityLine.split(":")[1].trim().toLowerCase();
        formattedMessage += `<div class="result-severity severity-${severity}">${severityLine}</div>`;
      }
      formattedMessage += "</div>";

      // Nearby Help Section
      if (message.includes("Recommended Doctors:")) {
        formattedMessage += '<div class="nearby-help">';
        formattedMessage += "<h3>Nearby Mental Health Professionals</h3>";
        formattedMessage += '<div class="doctors-list">';
        const doctorsStart =
          parts.findIndex((line) => line.includes("Recommended Doctors:")) + 1;
        const doctorsEnd = parts.findIndex((line) =>
          line.startsWith("Recommendations:")
        );
        const doctors = parts.slice(
          doctorsStart,
          doctorsEnd > 0 ? doctorsEnd : undefined
        );
        doctors.forEach((doctor) => {
          if (doctor.trim().startsWith("-")) {
            formattedMessage += `<div class="doctor-item">${doctor.substring(
              1
            )}</div>`;
          }
        });
        formattedMessage += "</div></div>";
      }

      // Recommendations Section
      if (message.includes("Recommendations:")) {
        formattedMessage += '<div class="recommendations">';
        formattedMessage += "<h3>Recommendations</h3><ul>";
        const recsStart =
          parts.findIndex((line) => line.includes("Recommendations:")) + 1;
        const recsEnd = parts.findIndex((line) => line.includes("Disclaimer:"));
        const recs = parts.slice(recsStart, recsEnd > 0 ? recsEnd : undefined);
        recs.forEach((rec) => {
          if (rec.trim().startsWith("-")) {
            formattedMessage += `<li>${rec.substring(1).trim()}</li>`;
          }
        });
        formattedMessage += "</ul></div>";
      }

      // Disclaimer Section
      const disclaimer = parts.find((line) => line.includes("Disclaimer:"));
      if (disclaimer) {
        formattedMessage += `<div class="disclaimer">${disclaimer}</div>`;
      }

      formattedMessage += "</div>";
      messageElement.innerHTML = formattedMessage;
    } else {
      // Handle regular messages as before
      const formattedMessage = message.replace(/\n/g, "<br>");
      messageElement.innerHTML = formattedMessage;
    }

    chatBox.appendChild(messageElement);
    scrollToBottom();

    // Check if this is the final message (report)
    if (message.includes("Assessment Complete")) {
      resultsContent.innerHTML = messageElement.innerHTML;
      resultsPopup.style.display = "flex";
    }
  };

  // --- API Call Function ---
  const apiCall = async (
    endpoint,
    method = "GET",
    body = null,
    needsAuth = false
  ) => {
    const headers = {
      "Content-Type": "application/json",
    };
    if (needsAuth && bearerToken) {
      headers["Authorization"] = `Bearer ${bearerToken}`;
    }

    const options = {
      method,
      headers,
    };

    if (body) {
      // For GET requests with OAuth2PasswordRequestForm, FastAPI expects form data
      if (endpoint === "/auth/token" && method === "POST") {
        headers["Content-Type"] = "application/x-www-form-urlencoded";
        options.body = new URLSearchParams(body); // Encode as form data
      } else {
        options.body = JSON.stringify(body);
      }
    }

    try {
      const response = await fetch(endpoint, options);
      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch (e) {
          // If response is not JSON
          errorData = { detail: `HTTP error! status: ${response.status}` };
        }
        console.error("API Error Response:", errorData);
        throw new Error(
          errorData.detail || `HTTP error! status: ${response.status}`
        );
      }
      // Handle cases where response might be empty (e.g., 204 No Content)
      if (response.status === 204) {
        return null; // Or handle as needed
      }
      return await response.json();
    } catch (error) {
      console.error("API Call Failed:", error);
      throw error; // Re-throw the error to be caught by the caller
    }
  };

  // --- Authentication Logic ---
  const handleLogin = async (event) => {
    event.preventDefault();
    clearErrors();
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;

    // FastAPI's OAuth2PasswordRequestForm expects form data
    const formData = {
      username: username,
      password: password,
    };

    try {
      // Note: Body is form data for /token endpoint
      const data = await apiCall("/auth/token", "POST", formData);
      if (data.access_token) {
        bearerToken = data.access_token;
        localStorage.setItem("bearerToken", bearerToken);
        await fetchUserInfoAndSetupChat();
      } else {
        displayError(loginError, "Login failed: No token received.");
      }
    } catch (error) {
      displayError(loginError, `Login failed: ${error.message}`);
    }
  };

  const handleRegister = async (event) => {
    event.preventDefault();
    clearErrors();
    const username = document.getElementById("register-username").value;
    const email = document.getElementById("register-email").value;
    const fullName = document.getElementById("register-fullname").value;
    const password = document.getElementById("register-password").value;

    const userData = { username, email, full_name: fullName || null, password };

    try {
      await apiCall("/auth/register", "POST", userData);
      registerSuccess.textContent = "Registration successful! Please login.";
      // Optionally clear form or switch to login view
      registerForm.reset();
      registerFormContainer.style.display = "none";
      loginFormContainer.style.display = "block";
    } catch (error) {
      displayError(registerError, `Registration failed: ${error.message}`);
    }
  };

  const handleLogout = () => {
    bearerToken = null;
    localStorage.removeItem("bearerToken");
    chatInitialized = false; // Reset chat state on logout
    chatBox.innerHTML = ""; // Clear chat history visually
    userInfo.textContent = "";
    userInfo.style.display = "none";
    logoutButton.style.display = "none";
    showView("auth");
    loginFormContainer.style.display = "block"; // Show login form by default
    registerFormContainer.style.display = "none";
    clearErrors();
  };

  const fetchUserInfoAndSetupChat = async () => {
    if (!bearerToken) {
      showView("auth");
      return;
    }
    try {
      const user = await apiCall("/auth/users/me", "GET", null, true);
      userInfo.textContent = `Logged in as: ${user.username}`;
      userInfo.style.display = "inline";
      logoutButton.style.display = "inline-block";
      showView("dashboard"); // Show dashboard instead of chat
      initDashboard(); // Initialize dashboard
    } catch (error) {
      console.error("Failed to fetch user info:", error);
      // Token might be invalid/expired
      handleLogout(); // Log out if fetching user fails
      displayError(
        loginError,
        `Session expired or invalid. Please login again. (${error.message})`
      );
    }
  };

  // --- Chat Logic ---

  const startChatSession = async () => {
    clearErrors();
    chatInitialized = false; // Reset flag
    messageInput.disabled = true; // Disable input while starting
    sendButton.disabled = true;

    try {
      console.log("Attempting to start chat session...");
      const initialResponse = await apiCall("/chat/start", "POST", {}, true); // Send empty body, auth needed
      addMessageToChat("ai", initialResponse.message);
      chatInitialized = true; // Mark chat as initialized
      console.log("Chat session started successfully.");
    } catch (error) {
      displayError(
        chatError,
        `Error starting chat: ${error.message}. Please try refreshing.`
      );
      console.error("Failed to start chat session:", error);
      // Keep input disabled if start fails critically
      return; // Prevent enabling input if start fails
    } finally {
      // Only enable if initialization was successful
      if (chatInitialized) {
        messageInput.disabled = false;
        sendButton.disabled = false;
        messageInput.focus();
      }
    }
  };

  const handleSendMessage = async () => {
    const messageText = messageInput.value.trim();
    if (!messageText) return;
    if (!chatInitialized) {
      displayError(
        chatError,
        "Chat session not started. Please wait or refresh."
      );
      return;
    }

    clearErrors();
    addMessageToChat("user", messageText);
    messageInput.value = ""; // Clear input field
    messageInput.disabled = true; // Disable input while waiting for AI
    sendButton.disabled = true;

    try {
      const response = await apiCall(
        "/chat/message",
        "POST",
        { message: messageText },
        true
      );
      addMessageToChat("ai", response.message);
    } catch (error) {
      displayError(chatError, `Error sending message: ${error.message}`);
      // Optionally add an error message to the chat box itself
      addMessageToChat(
        "ai",
        "Sorry, I encountered an error. Please try sending your message again."
      );
    } finally {
      messageInput.disabled = false; // Re-enable input
      sendButton.disabled = false;
      messageInput.focus();
    }
  };

  // --- Dashboard Logic ---

  const initDashboard = () => {
    // Initialize progress chart
    chartScript.onload = () => {
      const ctx = document.getElementById("progressChart").getContext("2d");
      new Chart(ctx, {
        type: "line",
        data: {
          labels: ["Jan", "Feb", "Mar", "Apr", "May"],
          datasets: [
            {
              label: "Mental Health Score",
              data: [7, 6, 8, 5, 7],
              borderColor: "#2575fc",
              tension: 0.3,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
        },
      });
    };

    // Load emergency contacts
    loadEmergencyContacts();
  };

  const loadEmergencyContacts = async () => {
    const contactsList = document.getElementById("contactsList");
    // Example contacts - replace with API call in production
    const contacts = [
      { name: "Dr. Smith", phone: "+1234567890" },
      { name: "Local Crisis Center", phone: "+9876543210" },
    ];

    contactsList.innerHTML = contacts
      .map(
        (contact) => `
      <div class="contact-item">
        <div>
          <strong>${contact.name}</strong><br>
          ${contact.phone}
        </div>
        <button class="edit-contact-btn">Edit</button>
      </div>
    `
      )
      .join("");
  };

  const startTest = (testId) => {
    showView("chat");
    messageInput.value = testId;
    handleSendMessage();
  };

  // Event Listeners for test cards
  testCards.forEach((card) => {
    card.querySelector(".start-test-btn").addEventListener("click", () => {
      startTest(card.dataset.test);
    });
  });

  addContactBtn.addEventListener("click", () => {
    // Implementation for adding new contact
    // You can show a modal or form here
  });

  // --- Event Listeners ---
  loginForm.addEventListener("submit", handleLogin);
  registerForm.addEventListener("submit", handleRegister);
  logoutButton.addEventListener("click", handleLogout);

  sendButton.addEventListener("click", handleSendMessage);
  messageInput.addEventListener("keypress", (e) => {
    // Send message on Enter key, unless Shift+Enter is pressed
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault(); // Prevent default newline behavior
      handleSendMessage();
    }
  });

  showRegisterLink.addEventListener("click", (e) => {
    e.preventDefault();
    clearErrors();
    loginFormContainer.style.display = "none";
    registerFormContainer.style.display = "block";
  });

  showLoginLink.addEventListener("click", (e) => {
    e.preventDefault();
    clearErrors();
    registerFormContainer.style.display = "none";
    loginFormContainer.style.display = "block";
  });

  newTestButton.addEventListener("click", async () => {
    resultsPopup.style.display = "none";
    chatBox.innerHTML = ""; // Clear chat history
    messageInput.value = ""; // Clear input
    await startChatSession(); // Start new chat session
  });

  emergencyContactButton.addEventListener("click", async () => {
    // Extract user info
    const userName =
      userInfo.textContent.replace("Logged in as: ", "") || "User";
    // Extract condition and severity from results
    const scoreLine =
      resultsContent.querySelector(".result-score")?.textContent || "";
    const severityLine =
      resultsContent.querySelector(".result-severity")?.textContent || "";
    const severity = severityLine.split(":")[1]?.trim() || "";
    // Try to extract condition from scoreLine or fallback
    let condition = "Unknown";
    if (scoreLine.toLowerCase().includes("depression"))
      condition = "Depression";
    else if (scoreLine.toLowerCase().includes("anxiety")) condition = "Anxiety";
    else if (scoreLine.toLowerCase().includes("stress")) condition = "Stress";
    // Extract recommendations
    const recommendationsList = resultsContent.querySelectorAll(
      ".recommendations li"
    );
    const recommendations = Array.from(recommendationsList).map(
      (li) => li.textContent
    );

    // Hardcoded recipient email for demo
    const receiverEmail = "psatyam86619@gmail.com";

    try {
      await apiCall(
        "/chat/emergency_contact",
        "POST",
        {
          user_name: userName,
          receiver_email: receiverEmail,
          condition,
          severity,
          recommendations,
        },
        true
      );
      alert("Emergency contact has been notified via email.");
    } catch (error) {
      alert("Failed to send emergency contact email: " + error.message);
    }
  });

  // --- Initial Check ---
  // Check if user is already logged in on page load
  if (bearerToken) {
    fetchUserInfoAndSetupChat(); // Fetch user info and switch to dashboard view
  } else {
    showView("auth"); // Otherwise, show auth forms
  }
});
