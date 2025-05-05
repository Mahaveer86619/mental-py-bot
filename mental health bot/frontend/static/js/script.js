document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const loginFormContainer = document.getElementById('login-form-container');
    const registerFormContainer = document.getElementById('register-form-container');
    const showRegisterLink = document.getElementById('show-register');
    const showLoginLink = document.getElementById('show-login');

    const authForms = document.getElementById('auth-forms');
    const chatContainer = document.getElementById('chat-container');
    const chatBox = document.getElementById('chat-box');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const logoutButton = document.getElementById('logout-button');
    const userInfo = document.getElementById('user-info');

    const loginError = document.getElementById('login-error');
    const registerError = document.getElementById('register-error');
    const registerSuccess = document.getElementById('register-success');
    const chatError = document.getElementById('chat-error');

    // --- State ---
    let bearerToken = localStorage.getItem('bearerToken');
    let chatInitialized = false; // Track if /chat/start has been called successfully

    // --- Utility Functions ---
    const clearErrors = () => {
        loginError.textContent = '';
        registerError.textContent = '';
        registerSuccess.textContent = '';
        chatError.textContent = '';
    };

    const displayError = (element, message) => {
        clearErrors();
        element.textContent = message;
    };

    const showView = (view) => {
        authForms.style.display = 'none';
        chatContainer.style.display = 'none';
        if (view === 'auth') {
            authForms.style.display = 'flex'; // Use flex for centering
        } else if (view === 'chat') {
            chatContainer.style.display = 'flex'; // Use flex for layout
        }
    };

    const scrollToBottom = () => {
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    const addMessageToChat = (sender, message) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender); // sender is 'user' or 'ai'

        // Basic Markdown-like formatting for newlines (replace \n with <br>)
        // More complex Markdown would require a library
        const formattedMessage = message.replace(/\n/g, '<br>');
        messageElement.innerHTML = formattedMessage; // Use innerHTML carefully

        chatBox.appendChild(messageElement);
        scrollToBottom();
    };

     // --- API Call Function ---
    const apiCall = async (endpoint, method = 'GET', body = null, needsAuth = false) => {
        const headers = {
            'Content-Type': 'application/json',
        };
        if (needsAuth && bearerToken) {
            headers['Authorization'] = `Bearer ${bearerToken}`;
        }

        const options = {
            method,
            headers,
        };

        if (body) {
            // For GET requests with OAuth2PasswordRequestForm, FastAPI expects form data
            if (endpoint === '/auth/token' && method === 'POST') {
                headers['Content-Type'] = 'application/x-www-form-urlencoded';
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
                console.error('API Error Response:', errorData);
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }
            // Handle cases where response might be empty (e.g., 204 No Content)
             if (response.status === 204) {
                return null; // Or handle as needed
            }
            return await response.json();
        } catch (error) {
            console.error('API Call Failed:', error);
            throw error; // Re-throw the error to be caught by the caller
        }
    };


    // --- Authentication Logic ---
    const handleLogin = async (event) => {
        event.preventDefault();
        clearErrors();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        // FastAPI's OAuth2PasswordRequestForm expects form data
        const formData = {
             username: username,
             password: password
        };


        try {
            // Note: Body is form data for /token endpoint
            const data = await apiCall('/auth/token', 'POST', formData);
            if (data.access_token) {
                bearerToken = data.access_token;
                localStorage.setItem('bearerToken', bearerToken);
                await fetchUserInfoAndSetupChat();
            } else {
                displayError(loginError, 'Login failed: No token received.');
            }
        } catch (error) {
            displayError(loginError, `Login failed: ${error.message}`);
        }
    };

    const handleRegister = async (event) => {
        event.preventDefault();
        clearErrors();
        const username = document.getElementById('register-username').value;
        const email = document.getElementById('register-email').value;
        const fullName = document.getElementById('register-fullname').value;
        const password = document.getElementById('register-password').value;

        const userData = { username, email, full_name: fullName || null, password };

        try {
            await apiCall('/auth/register', 'POST', userData);
            registerSuccess.textContent = 'Registration successful! Please login.';
             // Optionally clear form or switch to login view
            registerForm.reset();
             registerFormContainer.style.display = 'none';
             loginFormContainer.style.display = 'block';
        } catch (error) {
            displayError(registerError, `Registration failed: ${error.message}`);
        }
    };

    const handleLogout = () => {
        bearerToken = null;
        localStorage.removeItem('bearerToken');
        chatInitialized = false; // Reset chat state on logout
        chatBox.innerHTML = ''; // Clear chat history visually
        userInfo.textContent = '';
        userInfo.style.display = 'none';
        logoutButton.style.display = 'none';
        showView('auth');
        loginFormContainer.style.display = 'block'; // Show login form by default
        registerFormContainer.style.display = 'none';
        clearErrors();
    };

    const fetchUserInfoAndSetupChat = async () => {
        if (!bearerToken) {
            showView('auth');
            return;
        }
        try {
            const user = await apiCall('/auth/users/me', 'GET', null, true);
            userInfo.textContent = `Logged in as: ${user.username}`;
            userInfo.style.display = 'inline';
            logoutButton.style.display = 'inline-block';
            showView('chat');
            // Clear previous messages and start a new chat session
            chatBox.innerHTML = '';
            await startChatSession(); // Explicitly start chat
        } catch (error) {
            console.error('Failed to fetch user info:', error);
            // Token might be invalid/expired
            handleLogout(); // Log out if fetching user fails
            displayError(loginError, `Session expired or invalid. Please login again. (${error.message})`);
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
             const initialResponse = await apiCall('/chat/start', 'POST', {}, true); // Send empty body, auth needed
             addMessageToChat('ai', initialResponse.message);
             chatInitialized = true; // Mark chat as initialized
             console.log("Chat session started successfully.");
         } catch (error) {
             displayError(chatError, `Error starting chat: ${error.message}. Please try refreshing.`);
             console.error('Failed to start chat session:', error);
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
             displayError(chatError, "Chat session not started. Please wait or refresh.");
             return;
        }

        clearErrors();
        addMessageToChat('user', messageText);
        messageInput.value = ''; // Clear input field
        messageInput.disabled = true; // Disable input while waiting for AI
        sendButton.disabled = true;

        try {
            const response = await apiCall('/chat/message', 'POST', { message: messageText }, true);
            addMessageToChat('ai', response.message);
        } catch (error) {
            displayError(chatError, `Error sending message: ${error.message}`);
            // Optionally add an error message to the chat box itself
             addMessageToChat('ai', "Sorry, I encountered an error. Please try sending your message again.");
        } finally {
            messageInput.disabled = false; // Re-enable input
            sendButton.disabled = false;
            messageInput.focus();
        }
    };

    // --- Event Listeners ---
    loginForm.addEventListener('submit', handleLogin);
    registerForm.addEventListener('submit', handleRegister);
    logoutButton.addEventListener('click', handleLogout);

    sendButton.addEventListener('click', handleSendMessage);
    messageInput.addEventListener('keypress', (e) => {
        // Send message on Enter key, unless Shift+Enter is pressed
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault(); // Prevent default newline behavior
            handleSendMessage();
        }
    });

    showRegisterLink.addEventListener('click', (e) => {
        e.preventDefault();
        clearErrors();
        loginFormContainer.style.display = 'none';
        registerFormContainer.style.display = 'block';
    });

    showLoginLink.addEventListener('click', (e) => {
        e.preventDefault();
        clearErrors();
        registerFormContainer.style.display = 'none';
        loginFormContainer.style.display = 'block';
    });


    // --- Initial Check ---
    // Check if user is already logged in on page load
    if (bearerToken) {
        fetchUserInfoAndSetupChat(); // Fetch user info and switch to chat view
    } else {
        showView('auth'); // Otherwise, show auth forms
    }
});