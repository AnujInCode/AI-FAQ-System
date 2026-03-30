(function() {
  const API_URL = ""; // Relative URL for identical origin

  // Create UI elements
  const container = document.createElement('div');
  container.id = 'faq-widget-container';
  container.innerHTML = `
    <style>
      #faq-widget-button { position: fixed; bottom: 20px; right: 20px; width: 60px; height: 60px; background: #4a90e2; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.2); z-index: 9999; }
      #faq-widget-window { position: fixed; bottom: 90px; right: 20px; width: 380px; height: 550px; background: white; border-radius: 12px; box-shadow: 0 8px 30px rgba(0,0,0,0.15); display: none; flex-direction: column; overflow: hidden; z-index: 9998; border: 1px solid #eee; }
      #faq-widget-header { background: #4a90e2; color: white; padding: 15px; font-weight: bold; display: flex; justify-content: space-between; align-items: center; }
      #faq-widget-messages { flex: 1; overflow-y: auto; padding: 15px; font-family: sans-serif; font-size: 14px; background: #fafafa; }
      .faq-msg { margin-bottom: 12px; padding: 12px; border-radius: 8px; max-width: 85%; line-height: 1.5; position: relative; }
      .faq-user { align-self: flex-end; background: #4a90e2; color: white; margin-left: auto; border-bottom-right-radius: 2px; }
      .faq-bot { align-self: flex-start; background: #fff; color: #333; border: 1px solid #eaeaea; border-bottom-left-radius: 2px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
      .faq-meta { font-size: 11px; color: #999; margin-top: 8px; border-top: 1px solid #eee; padding-top: 6px; }
      .faq-timestamp { font-size: 10px; color: #bbb; display: block; margin-top: 4px; text-align: right; }
      #faq-widget-input-area { padding: 15px; background: #fff; border-top: 1px solid #eee; display: flex; align-items: center; }
      #faq-widget-input { flex: 1; border: 1px solid #ddd; border-radius: 20px; padding: 10px 15px; outline: none; transition: border 0.3s; }
      #faq-widget-input:focus { border-color: #4a90e2; }
      #faq-widget-send { background: none; color: #4a90e2; border: none; padding: 8px; margin-left: 8px; cursor: pointer; font-weight: bold; }
      .faq-loading { display: flex; gap: 4px; padding: 12px; align-items: center; }
      .faq-dot { width: 6px; height: 6px; background: #ccc; border-radius: 50%; animation: faq-bounce 1.4s infinite ease-in-out both; }
      .faq-dot:nth-child(1) { animation-delay: -0.32s; }
      .faq-dot:nth-child(2) { animation-delay: -0.16s; }
      @keyframes faq-bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }
    </style>
    <div id="faq-widget-button">💬</div>
    <div id="faq-widget-window">
      <div id="faq-widget-header">
        <span>Mental Health Assistant</span>
        <span id="faq-widget-close" style="cursor:pointer;">✖</span>
      </div>
      <div id="faq-widget-messages" style="display:flex; flex-direction:column;">
        <div class="faq-msg faq-bot">
          Hi! I can help you find answers to common questions about finding a therapist, our process, and mental health support.
        </div>
      </div>
      <div id="faq-widget-input-area">
        <input type="text" id="faq-widget-input" placeholder="Ask a question..." autocomplete="off" />
        <button id="faq-widget-send">Send</button>
      </div>
    </div>
  `;
  document.body.appendChild(container);

  const button = document.getElementById('faq-widget-button');
  const window = document.getElementById('faq-widget-window');
  const closeBtn = document.getElementById('faq-widget-close');
  const messages = document.getElementById('faq-widget-messages');
  const input = document.getElementById('faq-widget-input');
  const send = document.getElementById('faq-widget-send');

  const toggleWindow = () => {
    window.style.display = window.style.display === 'flex' ? 'none' : 'flex';
  };

  button.onclick = toggleWindow;
  closeBtn.onclick = toggleWindow;

  function getTime() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;

    // Append user message
    const userDiv = document.createElement('div');
    userDiv.className = 'faq-msg faq-user';
    userDiv.innerHTML = `<div>${text}</div><span class="faq-timestamp">${getTime()}</span>`;
    messages.appendChild(userDiv);
    input.value = '';
    messages.scrollTop = messages.scrollHeight;

    // Loading indicator (Typing dots)
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'faq-msg faq-bot faq-loading';
    loadingDiv.innerHTML = `<div class="faq-dot"></div><div class="faq-dot"></div><div class="faq-dot"></div>`;
    messages.appendChild(loadingDiv);
    messages.scrollTop = messages.scrollHeight;

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: text })
      });
      
      if (!response.ok) {
        if (response.status === 429) throw new Error("Too many requests. Please wait.");
        throw new Error("API error");
      }
      
      const data = await response.json();
      loadingDiv.remove();
      
      // Build response
      const botDiv = document.createElement('div');
      botDiv.className = 'faq-msg faq-bot';
      
      let html = `<div>${data.answer}</div>`;
      
      // Add Transparency Meta (Sources & Confidence)
      if (data.sources && data.sources.length > 0) {
          const confScore = Math.round(data.confidence * 100);
          html += `<div class="faq-meta">
            <strong>Sources:</strong> ${data.sources.join(' • ')}<br/>
            <em>Confidence: ${confScore}% (Latency: ${data.latency_ms}ms)</em>
          </div>`;
      }
      
      html += `<span class="faq-timestamp">${getTime()}</span>`;
      botDiv.innerHTML = html;
      
      messages.appendChild(botDiv);
      messages.scrollTop = messages.scrollHeight;
    } catch (err) {
      loadingDiv.remove();
      const errorDiv = document.createElement('div');
      errorDiv.className = 'faq-msg faq-bot';
      errorDiv.style.borderLeft = '3px solid red';
      errorDiv.innerHTML = `<div>${err.message || "Sorry, I couldn't process that. Please try again."}</div><span class="faq-timestamp">${getTime()}</span>`;
      messages.appendChild(errorDiv);
      messages.scrollTop = messages.scrollHeight;
    }
  }

  send.onclick = sendMessage;
  input.onkeypress = (e) => { if (e.key === 'Enter') sendMessage(); };
})();
