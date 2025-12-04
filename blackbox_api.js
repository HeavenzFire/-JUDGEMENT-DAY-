const API_KEY = "YOUR_API_KEY";
const API_URL = "https://api.blackbox.ai/chat/completions";

const data = {
  model: "blackboxai/anthropic/claude-3-haiku:beta",
  messages: [
    {
      role: "user",
      content: "tesla car moving on a high way",
    },
  ],
};

const response = await fetch(API_URL, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${API_KEY}`,
  },
  body: JSON.stringify(data),
});

const result = await response.json();
console.log(result);