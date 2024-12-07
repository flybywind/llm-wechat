import { EventEmitter } from "events";

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
    const body = { ...this.params, messages };
    const emitter = new EventEmitter();
    const dataPrefix = "data: ";
    const doneMessage = "[DONE]";
    fetch(this.url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify(body),
    })
      .then((response) => {
        if (!response.ok) throw new Error("Network response was not ok");
        if (!response.body) throw new Error("ReadableStream is not supported in this environment");

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");

        let buffer = "";
        let finish = false;
        const readStream = async () => {
          while (!finish) {
            const { done, value } = await reader.read();
            if (done) {
              emitter.emit("end");
              break;
            }

            buffer = decoder.decode(value, { stream: true });

            // Split data by newline or message boundary
            const parts = buffer.split("\n");
            for (const part of parts) {
              if (part.startsWith(dataPrefix)) {
                const json = part.slice(dataPrefix.length);
                if (json.trim() === doneMessage) {
                  emitter.emit("end");
                  finish = true;
                  break;
                }
                try {
                  const resp = JSON.parse(json);
                  resp.choices.forEach((choice) => {
                    emitter.emit("data", choice.delta.content);
                  });
                } catch (err) {
                  emitter.emit("error", err);
                }
              }
            }
          }
        };

        readStream().catch((err) => emitter.emit("error", err));
      })
      .catch((err) => emitter.emit("error", err));

    return emitter; // Return the EventEmitter
  }
}

export { QianwenApi, Role, Message };
