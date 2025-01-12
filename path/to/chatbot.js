async function getChatbotResponse(userInput) {
    const response = await fetchChatbotAPI(userInput);
    return response;
}

async function fetchChatbotAPI(input) {
    const response = await fetch('https://api.example.com/chatbot', {
        method: 'POST',
        body: JSON.stringify({ input }),
        headers: { 'Content-Type': 'application/json' }
    });
    const data = await response.json();
    return data.reply;
} 