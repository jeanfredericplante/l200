/* ==========================================================================
   🌌 Gemini L200 Agentic Hub app.js
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    // UI Elements
    const progressCircle = document.getElementById("progressCircle");
    const progressText = document.getElementById("progressText");
    const hoursCompleted = document.getElementById("hoursCompleted");
    const hoursTotal = document.getElementById("hoursTotal");
    const apiKeyInput = document.getElementById("apiKeyInput");
    const saveKeyBtn = document.getElementById("saveKeyBtn");
    const apiStatus = document.getElementById("apiStatus");
    const chatMessages = document.getElementById("chatMessages");
    const userInput = document.getElementById("userInput");
    const sendBtn = document.getElementById("sendBtn");
    const strugglesList = document.getElementById("strugglesList");
    const struggleCount = document.getElementById("struggleCount");
    
    // Quiz Arena Elements
    const quizModuleSelect = document.getElementById("quizModuleSelect");
    const startQuizBtn = document.getElementById("startQuizBtn");
    const quizArenaCard = document.getElementById("quizArenaCard");
    const quizQuestionText = document.getElementById("quizQuestionText");
    const quizOptionsList = document.getElementById("quizOptionsList");
    const submitAnswerBtn = document.getElementById("submitAnswerBtn");
    const quizFeedbackPanel = document.getElementById("quizFeedbackPanel");
    const feedbackBadge = document.getElementById("feedbackBadge");
    const feedbackText = document.getElementById("feedbackText");

    // Client-side Question Bank matching backend L200_SYLLABUS exactly
    const QUIZ_BANK = {
        s1_m1: {
            question: "When building an agent using Google Antigravity, which file is used to define the agent's core identity, metadata, and available tool permissions?",
            options: ["A", "B", "C", "D"],
            optionTexts: [
                "A) main.py",
                "B) skill.yaml",
                "C) model_armor.json",
                "D) agent_definition.py"
            ]
        },
        s1_m2: {
            question: "In the Google Agent Development Kit (ADK), how do you register a custom Python function to be called by an ADK Agent?",
            options: ["A", "B", "C", "D"],
            optionTexts: [
                "A) Decorate the function with @app.route('/tool')",
                "B) Add the function name to python-dotenv",
                "C) Wrap the function using the Tool constructor: Tool(name='...', func=my_func, description='...')",
                "D) Write the function directly inside index.html"
            ]
        },
        s1_m3: {
            question: "What is the primary objective of the 'Hill Climbing' search algorithm in the context of ADK agent evaluation and improvement?",
            options: ["A", "B", "C", "D"],
            optionTexts: [
                "A) To map optimal server routing paths on GCP",
                "B) To secure local API credentials using encryption",
                "C) To iteratively tweak prompt parameters and system instructions to maximize grading rubric compliance",
                "D) To balance traffic between active container replicas"
            ]
        },
        s2_m1: {
            question: "Which Google Cloud platform tool is specifically configured to block user jailbreak attempts, filter toxic content, and sanitize agent outputs in a Gemini Enterprise deployment?",
            options: ["A", "B", "C", "D"],
            optionTexts: [
                "A) Cloud Armor",
                "B) Identity-Aware Proxy (IAP)",
                "C) Model Armor",
                "D) Artifact Registry"
            ]
        },
        s2_m2: {
            question: "When connecting an ADK agent to a Workspace enterprise deployment for grounding, what is the best practice to protect confidential company files?",
            options: ["A", "B", "C", "D"],
            optionTexts: [
                "A) Copying files into a public Github repository",
                "B) Configuring fine-grained data source credentials and respecting existing enterprise access control list (ACL) rules",
                "C) Disabling all safety filters to maximize token speed",
                "D) Embedding the secret API key in client-side app.js"
            ]
        },
        s2_m3: {
            question: "What is the recommended approach for governing custom agent capabilities and authorization scopes across an enterprise organization?",
            options: ["A", "B", "C", "D"],
            optionTexts: [
                "A) Providing the exact same admin credentials to every agent instance",
                "B) Setting up fine-grained Role-Based Access Control (RBAC) mapping specific agents to narrow, verified service accounts",
                "C) Running all workloads outside the enterprise network firewall",
                "D) Storing credentials in plain text comments inside agent_definition.py"
            ]
        }
    };

    let activeQuizModule = null;

    // ==========================================
    // ⚙️ API Key / Session Management
    // ==========================================
    const loadSavedSession = () => {
        const savedKey = localStorage.getItem("gemini_api_key");
        if (savedKey) {
            apiKeyInput.value = savedKey;
            setApiStatusOnline(true);
        } else {
            setApiStatusOnline(false);
        }
    };

    const setApiStatusOnline = (isOnline) => {
        if (isOnline) {
            apiStatus.className = "api-status status-online";
            apiStatus.querySelector(".status-label").textContent = "Live Gemini Agent Mode";
        } else {
            apiStatus.className = "api-status status-offline";
            apiStatus.querySelector(".status-label").textContent = "Local Intelligent Mode";
        }
    };

    saveKeyBtn.addEventListener("click", () => {
        const key = apiKeyInput.value.trim();
        if (key) {
            localStorage.setItem("gemini_api_key", key);
            setApiStatusOnline(true);
            addSystemMessage("🔑 **Session Saved:** Live Gemini API integration activated.");
        } else {
            localStorage.removeItem("gemini_api_key");
            setApiStatusOnline(false);
            addSystemMessage("⚠️ **Session Cleared:** Fallback to Local Intelligent Mode.");
        }
    });

    const getApiKey = () => {
        return localStorage.getItem("gemini_api_key") || "";
    };

    // ==========================================
    // 🧩 Navigation Tabs Controls
    // ==========================================
    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));

            btn.classList.add("active");
            const tabName = btn.getAttribute("data-tab");
            document.getElementById(`panel-${tabName}`).classList.add("active");
        });
    });

    // ==========================================
    // 📊 State Synchronization & HUD Updates
    // ==========================================
    const setProgressRing = (percent) => {
        const radius = progressCircle.r.baseVal.value;
        const circumference = radius * 2 * Math.PI;
        
        progressCircle.style.strokeDasharray = `${circumference} ${circumference}`;
        
        // Reverse direction: 100% means 0 offset, 0% means full offset
        const offset = circumference - (percent / 100) * circumference;
        progressCircle.style.strokeDashoffset = offset;
    };

    const fetchAndRenderState = async () => {
        try {
            const response = await fetch("/api/state");
            if (response.ok) {
                const state = await response.json();
                renderState(state);
            }
        } catch (error) {
            console.error("Error loading state:", error);
        }
    };

    const renderState = (state) => {
        // 1. Overall Progress
        const percent = state.overall_progress_percent;
        progressText.textContent = `${percent}%`;
        setProgressRing(percent);

        hoursCompleted.textContent = state.hours_completed;
        hoursTotal.textContent = state.hours_total;

        // 2. Learning Map Checkboxes
        for (const [mId, module] of Object.entries(state.modules)) {
            const chk = document.getElementById(`chk_${mId}`);
            const card = document.getElementById(`card_${mId}`);
            if (chk && card) {
                chk.checked = module.completed;
                if (module.completed) {
                    card.classList.add("completed");
                } else {
                    card.classList.remove("completed");
                }
            }
        }

        // 3. Struggles List
        renderStrugglesList(state.active_struggles);
    };

    const renderStrugglesList = (struggles) => {
        const activeStruggles = struggles.filter(s => s.status === "active");
        struggleCount.textContent = activeStruggles.length;

        if (activeStruggles.length === 0) {
            strugglesList.innerHTML = `
                <div class="empty-state">
                    <h3>🎉 No Gaps Detected!</h3>
                    <p>You haven't displayed any learning gaps. Ask questions in chat or start quizzes to test your understanding.</p>
                </div>
            `;
            return;
        }

        strugglesList.innerHTML = activeStruggles.map(struggle => {
            const dateStr = new Date(struggle.detected_at).toLocaleDateString();
            const severityClass = `severity-${struggle.severity}`;
            return `
                <div class="struggle-item ${severityClass}">
                    <div class="struggle-details">
                        <h4>${struggle.topic}</h4>
                        <span>Severity: ${struggle.severity.toUpperCase()} | Identified: ${dateStr}</span>
                    </div>
                    <button class="btn btn-primary resolve-btn" data-topic="${struggle.topic}">Study Topic</button>
                </div>
            `;
        }).join("");

        // Add Quick-Study Click listeners to Struggles Study Buttons
        document.querySelectorAll(".resolve-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const topic = btn.getAttribute("data-topic");
                userInput.value = `Explain ${topic} in detail please.`;
                document.querySelector('[data-tab="chat"]').click(); // switch to chat tab
                sendMessage();
            });
        });
    };

    // Roadmap Checkbox Change Listeners
    document.querySelectorAll(".module-checkbox").forEach(chk => {
        chk.addEventListener("change", async (e) => {
            const mId = e.target.id.replace("chk_", "");
            const completed = e.target.checked;
            
            try {
                const res = await fetch("/api/state/update_module", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ module_id: mId, completed: completed })
                });
                
                if (res.ok) {
                    const updatedState = await res.json();
                    renderState(updatedState);
                }
            } catch (err) {
                console.error("Error checking roadmap item:", err);
            }
        });
    });

    // ==========================================
    // 💬 Chat Stream Mechanics
    // ==========================================
    const addMessageBubble = (sender, text, isUser = false) => {
        const bubble = document.createElement("div");
        bubble.className = `message ${isUser ? 'user-message' : 'agent-message'}`;
        
        // Format newline breaks nicely as HTML paragraphs
        const formattedText = text.replace(/\n/g, "<br>");

        bubble.innerHTML = `
            <div class="message-sender">${sender}</div>
            <div class="message-text">${formattedText}</div>
        `;
        chatMessages.appendChild(bubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    const addSystemMessage = (text) => {
        const bubble = document.createElement("div");
        bubble.className = "message system-message";
        bubble.innerHTML = `
            <div class="message-sender">💡 System Notice</div>
            <div class="message-text">${text}</div>
        `;
        chatMessages.appendChild(bubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    const sendMessage = async () => {
        const text = userInput.value.trim();
        if (!text) return;

        addMessageBubble("Student (You)", text, true);
        userInput.value = "";

        // Simulate typing animation
        const typingBubble = document.createElement("div");
        typingBubble.className = "message agent-message system-message";
        typingBubble.innerHTML = `<div class="message-text">⏳ *Orchestrating ADK subagents...*</div>`;
        chatMessages.appendChild(typingBubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const res = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text, api_key: getApiKey() })
            });

            chatMessages.removeChild(typingBubble);

            if (res.ok) {
                const data = await res.json();
                addMessageBubble("Multi-Agent Advisor", data.response, false);
                renderState(data.state);
                
                // If struggle topics were newly logged implicitly
                if (data.detected_gaps && data.detected_gaps.length > 0) {
                    addSystemMessage(`📋 **Coaching Agent Insight:** Detected difficulties with: *${data.detected_gaps.join(", ")}*. Adding them to your Gaps Map.`);
                }
            } else {
                addMessageBubble("Error", "Received a server failure. Ensure main.py backend is active.", false);
            }
        } catch (err) {
            chatMessages.removeChild(typingBubble);
            console.error("Chat API error:", err);
            addMessageBubble("Network Error", "Unable to communicate with the FastAPI backend.", false);
        }
    };

    sendBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });

    // ==========================================
    // 📝 Exam Arena Mechanics
    // ==========================================
    startQuizBtn.addEventListener("click", () => {
        const mId = quizModuleSelect.value;
        activeQuizModule = mId;

        const qData = QUIZ_BANK[mId];
        if (!qData) return;

        // Reset and show question
        quizQuestionText.textContent = qData.question;
        quizOptionsList.innerHTML = qData.optionTexts.map((optText, idx) => {
            const optLetter = qData.options[idx];
            return `
                <label class="quiz-option-label">
                    <input type="radio" name="quiz_opt" value="${optLetter}">
                    <span>${optText}</span>
                </label>
            `;
        }).join("");

        quizFeedbackPanel.style.display = "none";
        quizArenaCard.style.display = "flex";
        submitAnswerBtn.style.display = "block";
    });

    submitAnswerBtn.addEventListener("click", async () => {
        const selectedRadio = document.querySelector('input[name="quiz_opt"]:checked');
        if (!selectedRadio) {
            alert("Please select an answer first!");
            return;
        }

        const answer = selectedRadio.value;
        submitAnswerBtn.style.display = "none";

        try {
            const res = await fetch("/api/quiz/submit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ module_id: activeQuizModule, answer: answer })
            });

            if (res.ok) {
                const result = await res.json();
                
                // Show feedback UI
                feedbackBadge.className = `feedback-badge ${result.correct ? 'correct' : 'incorrect'}`;
                feedbackBadge.textContent = result.correct ? "✓ Correct!" : "❌ Incorrect";
                feedbackText.innerHTML = `**Explanation:** ${result.explanation}`;
                quizFeedbackPanel.style.display = "block";

                // Refresh overall dashboard state
                renderState(result.state);
            }
        } catch (err) {
            console.error("Error submitting quiz response:", err);
            submitAnswerBtn.style.display = "block";
        }
    });

    // ==========================================
    // 🚀 Bootstrap Initialization
    // ==========================================
    loadSavedSession();
    fetchAndRenderState();
});
