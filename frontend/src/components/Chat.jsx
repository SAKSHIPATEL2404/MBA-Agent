
import React, { useState, useEffect, useRef } from "react";
import "../styles.css";
import { jsPDF } from "jspdf";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false); 
  const [persona, setPersona] = useState("default");

  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [theme, setTheme] = useState(() => localStorage.getItem("theme") || "dark");

  const [currentChatId, setCurrentChatId] = useState(null);
  const [chatList, setChatList] = useState(() => {
    try { return JSON.parse(localStorage.getItem("chats") || "[]"); } catch { return []; }
  });
  const [chatTitle, setChatTitle] = useState("New chat");
  const [editingTitle, setEditingTitle] = useState(false);

  const quickSuggestions = [
    "Summarize my resume for MBA essays",
    "Give 3 tips to improve my LinkedIn profile",
    "Help me draft an answer for 'tell me about yourself'",
  ];

  const userId = "sakshi";
  const wsRef = useRef(null);
  const chatBoxRef = useRef(null);
  const streamingRef = useRef(false);

  
  useEffect(() => {
    if (chatBoxRef.current) chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
  }, [messages, loading]);

  
  useEffect(() => {
    document.documentElement.className = theme === "light" ? "light" : "dark";
    localStorage.setItem("theme", theme);
  }, [theme]);

  useEffect(() => {
    connectWS();
    
    if (!chatList || chatList.length === 0) {
      const id = "local-" + Date.now();
      setCurrentChatId(id);
      setChatList([{ chat_id: id, title: "New chat", updated: Date.now() }]);
    } else {
      setCurrentChatId(chatList[0]?.chat_id || ("local-" + Date.now()));
    }
   
  }, []);

  useEffect(() => {
    localStorage.setItem("chats", JSON.stringify(chatList));
  }, [chatList]);

  const connectWS = () => {
    try {
      wsRef.current = new WebSocket("ws://127.0.0.1:8000/ws/chat");
    } catch (e) {
      console.warn("WS connect failed", e);
      return;
    }

    wsRef.current.onopen = () => console.log("WS connected");
    wsRef.current.onmessage = (ev) => {
      const data = JSON.parse(ev.data);
      if (data.type === "typing") {
        setLoading(true);
        streamingRef.current = true;
      } else if (data.type === "chunk") {
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last && last.role === "assistant" && last.streaming) {
            const newLast = { ...last, content: last.content + data.text };
            return [...prev.slice(0, -1), newLast];
          } else {
            return [...prev, { role: "assistant", content: data.text, streaming: true }];
          }
        });
      } else if (data.type === "done") {
        setLoading(false);
        streamingRef.current = false;
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last && last.role === "assistant" && last.streaming) {
            const newLast = { ...last };
            delete newLast.streaming;
            return [...prev.slice(0, -1), newLast];
          }
          return prev;
        });
        saveChatLocally(); 
      } else if (data.type === "msg") {
        setMessages((prev) => [...prev, { role: "assistant", content: data.text }]);
        setLoading(false);
        streamingRef.current = false;
        saveChatLocally();
      } else if (data.type === "error") {
        setMessages((prev) => [...prev, { role: "assistant", content: `⚠ ${data.msg}` }]);
        setLoading(false);
        streamingRef.current = false;
      }
    };

    wsRef.current.onclose = () => {
      console.log("WS closed — reconnect in 1s");
      setTimeout(connectWS, 1000);
    };
  };

  function saveChatLocally() {
   
    const newList = [...chatList];
    const idx = newList.findIndex((c) => c.chat_id === currentChatId);
    const entry = {
      chat_id: currentChatId || "local-" + Date.now(),
      title: chatTitle || "Untitled",
      messages,
      updated: Date.now(),
    };
    if (idx >= 0) newList[idx] = { ...newList[idx], ...entry };
    else newList.unshift(entry);
    setChatList(newList);
  }

  async function createNewChat() {

    try {
      const res = await fetch("http://127.0.0.1:8000/chats/new", { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        setCurrentChatId(data.chat_id);
      } else {
        throw new Error("no backend new chat");
      }
    } catch {
      const id = "local-" + Date.now();
      setCurrentChatId(id);
    }
    setMessages([]);
    setChatTitle("New chat");
  }

  async function openChat(chat_id) {
    setCurrentChatId(chat_id);
   
    const local = chatList.find((c) => c.chat_id === chat_id);
    if (local && local.messages) {
      setMessages(local.messages);
      setChatTitle(local.title || "Chat");
      return;
    }
    try {
      const res = await fetch(`http://127.0.0.1:8000/chats/${chat_id}`);
      if (res.ok) {
        const data = await res.json();
        setMessages(data.messages || []);
        setChatTitle(data.title || "Chat");
      } else {
        setMessages([]);
        setChatTitle("Chat");
      }
    } catch {
      setMessages([]);
      setChatTitle("Chat");
    }
  }

  const sendMessage = async () => {
    if (!input.trim()) return;
    if (!currentChatId) await createNewChat();

    const msgText = input.trim();
    setInput("");
    setMessages((p) => [...p, { role: "user", content: msgText }]);
    setLoading(true);

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: "msg",
          user_id: userId,
          message: msgText,
          persona,
          chat_id: currentChatId,
        })
      );
     
      return;
    }

    try {
      const fd = new FormData();
      fd.append("user_id", userId);
      fd.append("message", msgText);
      fd.append("persona", persona);
      const res = await fetch("http://127.0.0.1:8000/chat", { method: "POST", body: fd });
      const data = await res.json();
      setMessages((p) => [...p, { role: "assistant", content: data.reply }]);
      setLoading(false);
      saveChatLocally();
    } catch (e) {
      setMessages((p) => [...p, { role: "assistant", content: "⚠ Server error." }]);
      setLoading(false);
    }
  };

  
  const onFileChange = async (file) => {
    if (!file) return;
    setLoading(true);
    const fd = new FormData();
    fd.append("file", file);
    try {
      const res = await fetch("http://127.0.0.1:8000/analyze-image", { method: "POST", body: fd });
      const data = await res.json();
      setMessages((p) => [...p, { role: "assistant", content: data.analysis }]);
      saveChatLocally();
    } catch {
      setMessages((p) => [...p, { role: "assistant", content: "⚠ Image analysis failed." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = (ev) => {
    ev.preventDefault();
    const f = ev.dataTransfer.files?.[0];
    if (f) onFileChange(f);
  };
  const handleDragOver = (ev) => ev.preventDefault();

  
  const startMic = () => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
      alert("Speech recognition not supported.");
      return;
    }
    const rec = new SR();
    rec.lang = "en-US";
    rec.interimResults = false;
    rec.onresult = (e) => {
      const t = e.results[0][0].transcript;
      setInput((prev) => (prev ? prev + " " + t : t));
    };
    rec.start();
  };

  
  const applyQuick = (text) => {
    setInput(text);
  };

  
  const exportToPDF = () => {
    const doc = new jsPDF({ format: "a4", unit: "pt" });
    const margin = 40;
    let y = 60;
    doc.setFontSize(18);
    doc.text(chatTitle || "Chat export", margin, y);
    y += 18;

    doc.setFontSize(12);
    messages.forEach((m) => {
      y += 10;
      const prefix = m.role === "user" ? "You: " : "MBA-Agent: ";
      const lines = doc.splitTextToSize(prefix + m.content, 520);
      doc.text(lines, margin, y);
      y += lines.length * 14;
      if (y > 740) {
        doc.addPage();
        y = 60;
      }
    });

    doc.save((chatTitle || "chat") + ".pdf");
  };

  
  const renameChat = (newTitle) => {
    setChatTitle(newTitle);
    
    const idx = chatList.findIndex((c) => c.chat_id === currentChatId);
    const copy = [...chatList];
    if (idx >= 0) {
      copy[idx] = { ...copy[idx], title: newTitle, updated: Date.now() };
    } else {
      copy.unshift({ chat_id: currentChatId, title: newTitle, updated: Date.now(), messages });
    }
    setChatList(copy);
  };

  
  const deleteMessage = (index) => {
    setMessages((prev) => {
      const copy = prev.filter((_, i) => i !== index);
      return copy;
    });
  };


  return (
    <div className="unique-chat-wrapper" onDrop={handleDrop} onDragOver={handleDragOver}>
      {/* SIDEBAR */}
      <div className={`sidebar ${sidebarOpen ? "" : "closed"}`}>
        <div style={{ display: "flex", gap: 8, alignItems: "center", justifyContent: "space-between" }}>
          <h2>Conversations</h2>
          <button className="menu-btn" onClick={() => setSidebarOpen(false)}>‹</button>
        </div>

        <button className="new-chat" onClick={createNewChat}>+ New Chat</button>

        <div className="chat-list" style={{ marginTop: 8 }}>
          {chatList.length === 0 && <p style={{ opacity: 0.6 }}>No chats yet — start a conversation</p>}
          {chatList.map((chat) => (
            <button key={chat.chat_id} className="chat-item" onClick={() => openChat(chat.chat_id)}>
              <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-start" }}>
                <strong>{chat.title || "New chat"}</strong>
                <small style={{ opacity: 0.6 }}>{new Date(chat.updated || Date.now()).toLocaleString()}</small>
              </div>
            </button>
          ))}
        </div>

        <div style={{ marginTop: 8 }}>
          <div style={{ display: "flex", gap: 8 }}>
            <button className="icon-btn" onClick={() => { setTheme((t) => (t === "dark" ? "light" : "dark")); }}>
              {theme === "dark" ? "🌞" : "🌙"}
            </button>
            <button className="icon-btn" onClick={() => exportToPDF()} title="Export current chat as PDF">PDF</button>
          </div>
        </div>
      </div>

      {/* MAIN CHAT AREA */}
      <div className="chat-container">
        <div className="chat-top">
          <button className="icon-btn" onClick={() => setSidebarOpen((s) => !s)}>☰</button>

          <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
            {!editingTitle ? (
              <h3 style={{ margin: 0 }}>{chatTitle}</h3>
            ) : (
              <input
                value={chatTitle}
                onChange={(e) => setChatTitle(e.target.value)}
                onBlur={() => { setEditingTitle(false); renameChat(chatTitle); }}
                onKeyDown={(e) => { if (e.key === "Enter") { setEditingTitle(false); renameChat(chatTitle); } }}
                autoFocus
              />
            )}

            <button className="icon-btn" onClick={() => setEditingTitle(true)} title="Rename chat">✎</button>
          </div>

          <select value={persona} onChange={(e) => setPersona(e.target.value)} className="persona-select">
            <option value="default">Default</option>
            <option value="mba_coach">MBA Coach</option>
            <option value="investor">Investor</option>
            <option value="startup">Startup Growth</option>
          </select>
        </div>

        <div className="chat-box" ref={chatBoxRef}>
          {messages.map((msg, i) => (
            <div key={i} className={`msg ${msg.role}`}>
              <div style={{ whiteSpace: "pre-wrap" }}>{msg.content}</div>
              <button className="delete-btn" onClick={() => deleteMessage(i)}>✕</button>
            </div>
          ))}

          {loading && (
            <div className="typing">
              <div className="typing-dots"><div></div><div></div><div></div></div>
            </div>
          )}
        </div>

      
        <div style={{ padding: "8px 16px", display: "flex", gap: 8 }}>
          {quickSuggestions.map((q) => (
            <button key={q} className="icon-btn" style={{ padding: "8px 12px" }} onClick={() => applyQuick(q)}>
              {q}
            </button>
          ))}
        </div>

        {/* INPUT BAR */}
        <div className="input-bar">
          {/* file input */}
          <label className="icon-btn" title="Upload image">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" xmlns="http://www.w3.org/2000/svg">
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <circle cx="8.5" cy="8.5" r="2.5" />
              <path d="M21 15l-5-5L5 21" />
            </svg>
            <input type="file" accept="image/*" onChange={(e) => onFileChange(e.target.files?.[0])} style={{ display: "none" }} />
          </label>

          {/* mic */}
          <button className={`icon-btn ${loading ? "listening" : ""}`} title="Voice" onClick={startMic}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 1a3 3 0 0 1 3 3v6a3 3 0 0 1-6 0V4a3 3 0 0 1 3-3z"/>
              <path d="M19 10a7 7 0 0 1-14 0"/>
              <line x1="12" y1="17" x2="12" y2="23" />
              <line x1="8" y1="23" x2="16" y2="23" />
            </svg>
          </button>

          {/* textarea */}
          <textarea
            className="chat-input"
            placeholder="Ask MBA-Agent (Shift+Enter for newline)..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
          />

          <button className="send-btn" onClick={sendMessage} disabled={loading}>
            {loading ? "..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}



