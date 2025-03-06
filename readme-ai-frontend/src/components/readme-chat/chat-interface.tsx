"use client";

import type React from "react";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send, Bot, User, RefreshCw } from "lucide-react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface ChatInterfaceProps {
  markdown: string;
  onUpdateReadme: (newContent: string) => void;
}

export function ChatInterface({
  markdown,
  onUpdateReadme,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content:
        "Hi there! I'm your README assistant. How can I help improve your README file today?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, []); // Updated dependency array

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSendMessage = () => {
    if (!input.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    // Focus the input after sending
    setTimeout(() => {
      inputRef.current?.focus();
    }, 0);

    // Simulate AI response
    setTimeout(() => {
      handleAIResponse(userMessage.content);
      setIsLoading(false);
    }, 1000);
  };

  const handleAIResponse = (userMessage: string) => {
    let aiResponse = "";
    let updatedMarkdown = markdown;

    // Simple logic to simulate AI responses and README updates
    if (userMessage.toLowerCase().includes("add badges")) {
      aiResponse =
        "I've added some badges to your README to show the project status and license.";
      updatedMarkdown = `[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://semver.org) [![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT) [![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/yourusername/yourrepo/actions)\n\n${markdown}`;
    } else if (userMessage.toLowerCase().includes("add table of contents")) {
      aiResponse =
        "I've added a table of contents to help users navigate your README.";
      const tocSection =
        "## Table of Contents\n\n- [Installation](#installation)\n- [Usage](#usage)\n- [Features](#features)\n- [Contributing](#contributing)\n- [License](#license)\n\n";
      const insertPosition = markdown.indexOf("## Description");
      updatedMarkdown =
        markdown.slice(0, insertPosition) +
        tocSection +
        markdown.slice(insertPosition);
    } else if (userMessage.toLowerCase().includes("improve code examples")) {
      aiResponse =
        "I've enhanced your code examples with better comments and more detailed usage patterns.";
      updatedMarkdown = markdown.replace(
        /```javascript[\s\S]*?```/,
        "```javascript\n// Import the module\nimport { myFunction } from 'my-project';\n\n// Configure options\nconst options = {\n  debug: true,\n  timeout: 1000\n};\n\n// Execute with options\nconst result = myFunction(options);\nconsole.log(result);\n```",
      );
    } else if (userMessage.toLowerCase().includes("expand features")) {
      aiResponse =
        "I've expanded the features section with more detailed information.";
      updatedMarkdown = markdown.replace(
        /## Features[\s\S]*?(?=\n## |$)/,
        "## Features\n\n- **Fast Processing**: Optimized algorithms for quick data handling\n- **Responsive UI**: Works on desktop and mobile devices\n- **Customizable Themes**: Choose from light, dark, and system themes\n- **API Integration**: Connect with popular third-party services\n- **Offline Support**: Continue working without an internet connection\n\n",
      );
    } else {
      aiResponse =
        "I understand you want to improve your README. Could you be more specific about what you'd like to change? For example, you could ask me to add badges, create a table of contents, improve code examples, or expand the features section.";
    }

    // Add AI response message
    const assistantMessage: Message = {
      id: Date.now().toString(),
      role: "assistant",
      content: aiResponse,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, assistantMessage]);

    // Update README if changes were made
    if (updatedMarkdown !== markdown) {
      onUpdateReadme(updatedMarkdown);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex w-1/2 flex-col border-r">
      <div className="border-b p-4">
        <h2 className="text-lg font-semibold">Chat with README Assistant</h2>
        <p className="text-sm text-muted-foreground">
          Ask me to help improve your README file
        </p>
      </div>

      <ScrollArea className="flex-1">
        <div className="flex flex-col gap-4 p-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === "assistant" ? "justify-start" : "justify-end"}`}
            >
              <div
                className={`flex max-w-[80%] items-start gap-3 rounded-lg p-3 ${
                  message.role === "assistant"
                    ? "bg-muted"
                    : "bg-primary text-primary-foreground"
                }`}
              >
                <div className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-background/20">
                  {message.role === "assistant" ? (
                    <Bot className="h-4 w-4" />
                  ) : (
                    <User className="h-4 w-4" />
                  )}
                </div>
                <div>
                  <div className="text-sm">{message.content}</div>
                  <div className="mt-1 text-xs text-muted-foreground/70">
                    {message.timestamp.toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </div>
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="flex max-w-[80%] items-start gap-3 rounded-lg bg-muted p-3">
                <div className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-background/20">
                  <RefreshCw className="h-4 w-4 animate-spin" />
                </div>
                <div className="text-sm">Thinking...</div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      <div className="border-t p-4">
        <div className="flex items-center gap-2">
          <Input
            ref={inputRef}
            placeholder="Ask me to improve your README..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-1"
          />
          <Button
            size="icon"
            onClick={handleSendMessage}
            disabled={!input.trim() || isLoading}
          >
            <Send className="h-4 w-4" />
            <span className="sr-only">Send</span>
          </Button>
        </div>
        <div className="mt-2 text-xs text-muted-foreground">
          Try: "Add badges", "Add table of contents", "Improve code examples",
          "Expand features"
        </div>
      </div>
    </div>
  );
}
