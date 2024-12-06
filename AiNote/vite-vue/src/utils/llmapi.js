const Role = Object.freeze({
  System: "system",
  User: "user",
  AI: "assistant",
});
class Message {
  constructor(role, content) {
    if (!Object.values(Role).includes(role)) {
      throw new Error("Invalid role");
    }
    this.role = role;
    this.content = content;
  }
}

class QianwenApi {
  constructor(
    apiKey,
    model,
    params = {
      top_p: 0.8,
      stream: false,
      presence_penalty: 2.0,
      enable_search: false,
    }
  ) {
    this.url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions";
    this.apiKey = apiKey;
    this.systemMessage = null;
    this.params = { top_p: 0.8, stream: false, presence_penalty: 2.0, enable_search: false, ...params, model: model };
  }

  setSystem(prompt) {
    this.systemMessage = new Message(Role.System, prompt);
  }

  async chat(role, content) {
    const message = new Message(role, content);
    const messages = [];
    if (this.systemMessage) {
      messages.push(this.systemMessage);
    }
    messages.push(message);
    return this.getResponse(messages);
  }

  async getResponse(messages) {
    const body = { ...this.params, messages: messages };
    const response = await fetch(this.url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify(body),
    });
    return response.json();
  }
}

export { QianwenApi, Role, Message };
