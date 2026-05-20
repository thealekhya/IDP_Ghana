"use client";
import Link from "next/link";
import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import AuthUserMenu from "../AuthUserMenu";
import { useUser } from "@clerk/nextjs";

// ─── Types ────────────────────────────────────────────────────────────────────
type StepType = "sql" | "vector" | "document" | "computation";

interface CitationStep {
  id: string;
  type: StepType;
  label: string;
  detail: string;       // the actual query / chunk / code
  source: string;       // table / index / filename
  rows?: number;        // SQL rows returned
  tokens?: number;      // vector search hits
  timing?: string;      // e.g. "142ms"
}

interface Citation {
  id: string;
  title: string;        // short label shown on pill
  steps: CitationStep[];
}

type ChatMessage = {
  role: "user" | "ai";
  text: string;
  citations?: Citation[];
};

type ChatSession = {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: number;
  updatedAt: number;
};

const CHAT_HISTORY_STORAGE_KEY = "sankofa-chat-history";
const ACTIVE_CHAT_STORAGE_KEY = "sankofa-active-chat-id";
const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

// ─── Main Chat Page ───────────────────────────────────────────────────────────

// ─── Icon map ─────────────────────────────────────────────────────────────────
const STEP_ICONS: Record<StepType, { icon: string; color: string; bg: string }> = {
  sql:         { icon: "database",       color: "text-blue-400",   bg: "bg-blue-500/10 border-blue-500/30" },
  vector:      { icon: "hub",            color: "text-purple-400", bg: "bg-purple-500/10 border-purple-500/30" },
  document:    { icon: "description",    color: "text-emerald-400",bg: "bg-emerald-500/10 border-emerald-500/30" },
  computation: { icon: "function",       color: "text-amber-400",  bg: "bg-amber-500/10 border-amber-500/30" },
};

const createUuid = () => {
  if (typeof globalThis.crypto?.randomUUID === "function") {
    return globalThis.crypto.randomUUID();
  }

  return "10000000-1000-4000-8000-100000000000".replace(/[018]/g, char => {
    const value = Number(char);
    const random = typeof globalThis.crypto?.getRandomValues === "function"
      ? globalThis.crypto.getRandomValues(new Uint8Array(1))[0] & 15
      : Math.floor(Math.random() * 16);

    return (value ^ (random >> (value / 4))).toString(16);
  });
};

const createChatSession = (): ChatSession => {
  const now = Date.now();

  return {
    id: createUuid(),
    title: "New Chat",
    messages: [],
    createdAt: now,
    updatedAt: now,
  };
};

const getChatTitle = (text: string) => {
  const cleaned = text.trim().replace(/\s+/g, " ");
  return cleaned.length > 42 ? `${cleaned.slice(0, 42)}...` : cleaned || "New Chat";
};

const isChatSession = (chat: unknown): chat is ChatSession => {
  if (!chat || typeof chat !== "object") return false;
  const candidate = chat as Partial<ChatSession>;
  return (
    typeof candidate.id === "string" &&
    typeof candidate.title === "string" &&
    Array.isArray(candidate.messages)
  );
};

const ensureUuidChatIds = (chats: ChatSession[], activeChatId: string | null) => {
  const usedIds = new Set<string>();
  const migratedIds = new Map<string, string>();

  const history = chats.map(chat => {
    let nextId = chat.id;

    while (!UUID_PATTERN.test(nextId) || usedIds.has(nextId)) {
      nextId = createUuid();
    }

    usedIds.add(nextId);
    if (nextId !== chat.id) {
      migratedIds.set(chat.id, nextId);
    }

    return {
      ...chat,
      id: nextId,
    };
  });

  return {
    history,
    activeChatId: activeChatId ? migratedIds.get(activeChatId) ?? activeChatId : null,
  };
};

// ─── Context Inspector Panel ──────────────────────────────────────────────────
function ContextInspector({
  citation,
  onClose,
}: {
  citation: Citation | null;
  onClose: () => void;
}) {
  const [openStep, setOpenStep] = useState<string | null>(null);

  return (
    <aside
      className={`fixed top-0 right-0 h-full z-50 flex flex-col bg-[#0f1117] border-l border-white/10 shadow-2xl transition-all duration-300 ease-in-out ${
        citation ? "w-[480px] translate-x-0 opacity-100" : "w-[480px] translate-x-full opacity-0 pointer-events-none"
      }`}
      style={{ fontFamily: "'JetBrains Mono', 'Fira Mono', monospace" }}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-white/10 bg-[#0f1117]">
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-md bg-primary/20 flex items-center justify-center">
            <span className="material-symbols-outlined text-primary text-[16px]">query_stats</span>
          </div>
          <div>
            <div className="text-[11px] uppercase tracking-[0.15em] text-white/40 font-bold">Context Inspector</div>
            <div className="text-sm text-white/80 font-sans font-semibold truncate max-w-[300px]">
              {citation?.title ?? ""}
            </div>
          </div>
        </div>
        <button
          onClick={onClose}
          className="w-7 h-7 rounded-md hover:bg-white/10 flex items-center justify-center text-white/50 hover:text-white transition-all"
        >
          <span className="material-symbols-outlined text-[18px]">close</span>
        </button>
      </div>

      {/* Step count summary */}
      {citation && (
        <div className="px-5 py-3 border-b border-white/5 bg-white/[0.02] flex items-center gap-4">
          <span className="text-[11px] text-white/40 uppercase tracking-wider font-bold font-sans">
            {citation.steps.length} steps · AI reasoning trace
          </span>
          <div className="flex gap-2 ml-auto">
            {Array.from(new Set(citation.steps.map(s => s.type))).map(type => {
              const meta = STEP_ICONS[type];
              return (
                <span key={type} className={`text-[10px] px-2 py-0.5 rounded-full border font-bold uppercase tracking-wider font-sans ${meta.bg} ${meta.color}`}>
                  {type}
                </span>
              );
            })}
          </div>
        </div>
      )}

      {/* Steps list */}
      <div className="flex-1 overflow-y-auto px-4 py-4 flex flex-col gap-3">
        {citation?.steps.map((step, idx) => {
          const meta = STEP_ICONS[step.type];
          const isOpen = openStep === step.id;
          return (
            <div
              key={step.id}
              className={`rounded-xl border transition-all duration-200 overflow-hidden ${meta.bg}`}
            >
              {/* Step header — always visible */}
              <button
                className="w-full flex items-start gap-3 px-4 py-3 text-left hover:bg-white/[0.04] transition-colors"
                onClick={() => setOpenStep(isOpen ? null : step.id)}
              >
                {/* Step number */}
                <div className="mt-0.5 w-5 h-5 rounded-full bg-white/10 flex items-center justify-center shrink-0">
                  <span className="text-[10px] text-white/60 font-bold">{idx + 1}</span>
                </div>
                {/* Icon + label */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className={`material-symbols-outlined text-[15px] ${meta.color}`}>{meta.icon}</span>
                    <span className={`text-[10px] uppercase tracking-wider font-bold ${meta.color}`}>{step.type}</span>
                    {step.timing && (
                      <span className="ml-auto text-[10px] text-white/30 font-sans">{step.timing}</span>
                    )}
                  </div>
                  <div className="text-[13px] text-white/80 font-sans font-medium leading-snug truncate">{step.label}</div>
                  <div className="text-[11px] text-white/35 font-sans mt-0.5 flex items-center gap-3">
                    <span className="truncate">{step.source}</span>
                    {step.rows !== undefined && <span className="shrink-0 text-emerald-400/70">{step.rows} rows</span>}
                    {step.tokens !== undefined && <span className="shrink-0 text-purple-400/70">{step.tokens} hits</span>}
                  </div>
                </div>
                {/* Expand chevron */}
                <span className={`material-symbols-outlined text-[18px] text-white/30 transition-transform duration-200 shrink-0 mt-1 ${isOpen ? "rotate-180" : ""}`}>
                  expand_more
                </span>
              </button>

              {/* Expanded code block */}
              {isOpen && (
                <div className="border-t border-white/10 bg-black/30">
                  <div className="flex items-center justify-between px-4 py-2 border-b border-white/5">
                    <span className="text-[10px] text-white/30 uppercase tracking-wider">Raw · {step.type}</span>
                    <button
                      onClick={() => navigator.clipboard.writeText(step.detail)}
                      className="flex items-center gap-1 text-[10px] text-white/30 hover:text-white/60 transition-colors"
                    >
                      <span className="material-symbols-outlined text-[13px]">content_copy</span>
                      Copy
                    </button>
                  </div>
                  <pre className="px-4 py-3 text-[11.5px] leading-relaxed text-green-300/80 overflow-x-auto whitespace-pre-wrap break-words">
                    <code>{step.detail}</code>
                  </pre>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div className="px-5 py-3 border-t border-white/10 bg-black/20 flex items-center justify-between">
        <span className="text-[10px] text-white/25 uppercase tracking-wider font-sans">Sankofa AI · Trace v1</span>
        <button
          onClick={onClose}
          className="text-[11px] text-white/40 hover:text-white/70 font-sans transition-colors flex items-center gap-1"
        >
          <span className="material-symbols-outlined text-[14px]">close</span>
          Close panel
        </button>
      </div>
    </aside>
  );
}

export default function ChatPage() {
  const [inputText, setInputText] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [activeCitation, setActiveCitation] = useState<Citation | null>(null);
  const [loading, setLoading] = useState(false);
  const [showQuotaModal, setShowQuotaModal] = useState(false);
  const [chatHistory, setChatHistory] = useState<ChatSession[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const [loadedChatHistoryStorageKey, setLoadedChatHistoryStorageKey] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const { isLoaded, user } = useUser();
  const userStorageId = isLoaded ? user?.id ?? "guest" : null;
  const chatHistoryStorageKey = userStorageId ? `${CHAT_HISTORY_STORAGE_KEY}:${userStorageId}` : null;
  const activeChatStorageKey = userStorageId ? `${ACTIVE_CHAT_STORAGE_KEY}:${userStorageId}` : null;
  const displayName = user?.fullName || user?.username || user?.primaryEmailAddress?.emailAddress || "Guest";

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      if (!chatHistoryStorageKey || !activeChatStorageKey) return;

      let savedHistory: ChatSession[] = [];

      try {
        const rawHistory = window.localStorage.getItem(chatHistoryStorageKey);
        const parsedHistory = rawHistory ? JSON.parse(rawHistory) : null;
        if (Array.isArray(parsedHistory)) {
          savedHistory = parsedHistory.filter(isChatSession).map(chat => ({
            ...chat,
            createdAt: chat.createdAt || Date.now(),
            updatedAt: chat.updatedAt || Date.now(),
          }));
        }
      } catch {
        savedHistory = [];
      }

      const savedActiveChatId = window.localStorage.getItem(activeChatStorageKey);
      const { history: nextHistory, activeChatId: migratedActiveChatId } = ensureUuidChatIds(
        savedHistory.length > 0 ? savedHistory : [createChatSession()],
        savedActiveChatId
      );
      const nextActiveChat = nextHistory.find(chat => chat.id === migratedActiveChatId) ?? nextHistory[0];

      setChatHistory(nextHistory);
      setActiveChatId(nextActiveChat.id);
      setMessages(nextActiveChat.messages);
      setLoadedChatHistoryStorageKey(chatHistoryStorageKey);
      setHistoryLoaded(true);

      window.localStorage.setItem(chatHistoryStorageKey, JSON.stringify(nextHistory));
      window.localStorage.setItem(activeChatStorageKey, nextActiveChat.id);
    }, 0);

    return () => window.clearTimeout(timeoutId);
  }, [chatHistoryStorageKey, activeChatStorageKey]);

  useEffect(() => {
    if (!historyLoaded || loadedChatHistoryStorageKey !== chatHistoryStorageKey || !chatHistoryStorageKey) return;
    window.localStorage.setItem(chatHistoryStorageKey, JSON.stringify(chatHistory));
  }, [chatHistory, chatHistoryStorageKey, historyLoaded, loadedChatHistoryStorageKey]);

  useEffect(() => {
    if (!historyLoaded || loadedChatHistoryStorageKey !== chatHistoryStorageKey || !activeChatStorageKey || !activeChatId) return;
    window.localStorage.setItem(activeChatStorageKey, activeChatId);
  }, [activeChatId, activeChatStorageKey, chatHistoryStorageKey, historyLoaded, loadedChatHistoryStorageKey]);

  const openInspector = (c: Citation) => {
    setActiveCitation(prev => (prev?.id === c.id ? null : c)); // toggle
  };

  const updateChatMessages = (chatId: string, nextMessages: ChatMessage[]) => {
    setChatHistory(prev => {
      const now = Date.now();
      return prev.map(chat => {
        if (chat.id !== chatId) return chat;
        const shouldRename = chat.title === "New Chat" && nextMessages.length > 0;

        return {
          ...chat,
          title: shouldRename ? getChatTitle(nextMessages[0].text) : chat.title,
          messages: nextMessages,
          updatedAt: now,
        };
      });
    });
  };

  const startNewChat = () => {
    abortControllerRef.current?.abort();
    const newChat = createChatSession();
    setChatHistory(prev => [newChat, ...prev]);
    setActiveChatId(newChat.id);
    setMessages([]);
    setInputText("");
    setActiveCitation(null);
    setLoading(false);
  };

  const openChat = (chat: ChatSession) => {
    abortControllerRef.current?.abort();
    setActiveChatId(chat.id);
    setMessages(chat.messages);
    setInputText("");
    setActiveCitation(null);
    setLoading(false);
  };

  const handleSend = async () => {
    if (!inputText.trim()) return;

    let currentChatId = activeChatId;
    if (!currentChatId || !chatHistory.some(chat => chat.id === currentChatId)) {
      const newChat = createChatSession();
      currentChatId = newChat.id;
      setChatHistory(prev => [newChat, ...prev]);
      setActiveChatId(newChat.id);
    }

    const userMessage = { role: "user" as const, text: inputText };
    const nextMessages = [...messages, userMessage];
    setMessages(nextMessages);
    updateChatMessages(currentChatId, nextMessages);
    setInputText("");
    setActiveCitation(null);
    setLoading(true);
    
    abortControllerRef.current = new AbortController();

    try {
      // Connect to the local FastAPI server
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userMessage.text }),
        signal: abortControllerRef.current.signal
      });
      
      if (res.status === 429) {
        setShowQuotaModal(true);
        // Remove the user message if it failed, or just leave it. We'll leave it but not add an AI response.
        return;
      }
      
      if (!res.ok) throw new Error("API Error");
      
      const data = await res.json();
      
      const aiMessage: ChatMessage = {
        role: "ai", 
        text: data.answer, 
        citations: data.citations
      };

      setMessages(prev => {
        const updatedMessages = [...prev, aiMessage];
        updateChatMessages(currentChatId, updatedMessages);
        return updatedMessages;
      });
    } catch (err: unknown) {
      if (err instanceof DOMException && err.name === 'AbortError') {
        // User aborted the request
        return;
      }
      console.error(err);
      const errorMessage: ChatMessage = {
        role: "ai", 
        text: "I'm currently unable to process your request due to a temporary network issue. Please try again in a few moments."
      };

      setMessages(prev => {
        const updatedMessages = [...prev, errorMessage];
        updateChatMessages(currentChatId, updatedMessages);
        return updatedMessages;
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-background text-on-background h-screen flex flex-col overflow-hidden font-body-md text-body-md antialiased">
      {/* Mobile TopNav */}
      <header className="fixed top-0 left-0 w-full z-40 flex justify-between items-center px-4 h-16 bg-surface/80 backdrop-blur-md border-b border-outline-variant/30 lg:hidden mt-10">
        <div className="font-headline-md font-bold text-primary tracking-tight">Sankofa AI</div>
        <div className="flex items-center gap-4 text-primary">
          <AuthUserMenu />
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden lg:pt-0 pt-16">
        {/* SideNavBar */}
        <nav className="hidden lg:flex flex-col h-full bg-surface-container-low border-r border-outline-variant/20 w-64 z-40 shrink-0">
          <div className="p-6 flex flex-col items-center border-b border-outline-variant/20">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              alt="Sankofa Health Logo"
              className="w-16 h-16 rounded-full mb-4 object-cover"
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuAum3m4zs7-RJwCvcE-JhB52nMps1jxy5l6iws17tBu7dqk-2DBg_g9DMWGtUplT-8rBP24vOEiCssdLx_z5p0vVGVrE7blpPfqn4ZxMS7RlN9ZdZmoNL4myqjDp5a8AysE-PzNu5cgBVJ22l02Hk40awEKg157eHAff7lDCcjfJWwdOZpYID1ENseIzcAsQi-xx78TpgAP8L164Q0o07wrvIaz-TObPX6mDkip4L8bb-18SEMZky5Q6QQnB2YVfnz7dWXKZb2HtAEn"
            />
            <h1 className="font-headline-md font-bold text-primary text-center">Sankofa AI</h1>
            <p className="font-label-sm text-on-surface-variant mt-1 text-center uppercase">Ghana Medical Intelligence</p>
          </div>
          <div className="flex-1 overflow-y-auto py-4 px-3 flex flex-col gap-2">
            <button
              type="button"
              onClick={startNewChat}
              className="flex items-center gap-3 px-3 py-2 bg-secondary-container text-on-secondary-container rounded-lg font-bold text-left"
            >
              <span className="material-symbols-outlined">add_comment</span>
              <span className="font-label-sm uppercase">New Chat</span>
            </button>
            <Link className="flex items-center gap-3 px-3 py-2 text-on-surface-variant hover:bg-surface-container-high transition-all rounded-lg" href="/map">
              <span className="material-symbols-outlined">map</span>
              <span className="font-label-sm uppercase">Healthcare Map</span>
            </Link>
            <Link className="flex items-center gap-3 px-3 py-2 text-on-surface-variant hover:bg-surface-container-high transition-all rounded-lg" href="/home">
              <span className="material-symbols-outlined">analytics</span>
              <span className="font-label-sm uppercase">Data Insights</span>
            </Link>
            <Link className="flex items-center gap-3 px-3 py-2 text-on-surface-variant hover:bg-surface-container-high transition-all rounded-lg" href="/anomalies">
              <span className="material-symbols-outlined">data_alert</span>
              <span className="font-label-sm uppercase">Data Integrity</span>
            </Link>

            {/* Chat History Section */}
            <div className="mt-4 pt-4 border-t border-outline-variant/20 px-1 flex flex-col gap-1">
              <div className="font-label-sm text-[10px] uppercase tracking-widest text-on-surface-variant/60 mb-1 pl-2">Recent Chats</div>
              {chatHistory.map(chat => (
                <button
                  type="button"
                  key={chat.id} 
                  onClick={() => openChat(chat)}
                  className={`flex items-center gap-2 px-2 py-1.5 rounded-lg text-sm hover:bg-surface-container-high hover:text-primary cursor-pointer transition-colors group text-left ${
                    activeChatId === chat.id
                      ? "bg-surface-container-high text-primary"
                      : "text-on-surface-variant"
                  }`}
                >
                  <span className="material-symbols-outlined text-[16px] opacity-50 group-hover:opacity-100">
                    {chat.messages.length === 0 ? "add_comment" : "chat_bubble"}
                  </span>
                  <span className="truncate">{chat.title}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Clerk Auth Section at bottom of sidebar */}
          <div className="p-4 border-t border-outline-variant/20 flex flex-col gap-2 mt-auto">
            <div className="flex items-center justify-between w-full px-3 py-2 rounded-lg text-sm text-on-surface bg-surface-container-high/40 border border-outline-variant/20">
              <div className="flex items-center gap-3 truncate">
                <AuthUserMenu />
                <span className="truncate font-medium text-on-surface-variant">{displayName}</span>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Chat Canvas */}
        <main
          className={`flex-1 flex flex-col bg-surface-container-lowest relative transition-all duration-300 ${activeCitation ? "mr-[480px]" : ""}`}
        >
          <div className="hidden lg:flex absolute top-4 right-4 z-30 items-center gap-3">
            <AuthUserMenu />
          </div>

          {/* Chat History */}
          <div className="flex-1 overflow-y-auto p-4 md:p-8 flex flex-col gap-6" id="chat-container">

            {messages.length === 0 ? (
              <div className="flex-1 flex flex-col items-center justify-center max-w-2xl mx-auto w-full text-center space-y-6 opacity-50 py-12">
                <span className="material-symbols-outlined text-[64px] text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>
                  health_and_safety
                </span>
                <h2 className="font-display-lg-mobile text-display-lg-mobile text-on-surface">
                  How can I assist with Ghana healthcare data today?
                </h2>
                <p className="font-body-lg text-on-surface-variant max-w-lg">
                  Query facility availability, medical desert mapping, or historical patient outcome data.
                </p>
              </div>
            ) : (
              messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} w-full max-w-4xl mx-auto gap-4`}>
                  {msg.role === "ai" && (
                    <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0 mt-1">
                      <span className="material-symbols-outlined text-on-primary text-[18px]" style={{ fontVariationSettings: "'FILL' 1" }}>
                        smart_toy
                      </span>
                    </div>
                  )}
                  
                  <div className={`${msg.role === "user" ? "bg-surface-container-high text-on-surface rounded-2xl rounded-tr-sm px-5 py-3 max-w-[85%]" : "bg-surface-container-low border border-outline-variant/30 rounded-2xl rounded-tl-sm px-5 py-4 w-full shadow-[0_4px_40px_rgba(0,0,0,0.1)]"}`}>
                    <div className="chat-markdown max-w-none">
                      {msg.role === "ai" ? (
                        <ReactMarkdown>{msg.text}</ReactMarkdown>
                      ) : (
                        <span className="whitespace-pre-wrap">{msg.text}</span>
                      )}
                    </div>

                    {/* Citations row (AI only) */}
                    {msg.role === "ai" && msg.citations && msg.citations.length > 0 && (
                      <div className="mt-4 pt-3 border-t border-outline-variant/30">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="font-label-sm text-outline text-[10px] uppercase tracking-wider">Sources & Citations</span>
                          <span className="text-[10px] text-outline/60 italic">— click to inspect AI reasoning</span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {msg.citations.map(c => {
                            const isActive = activeCitation?.id === c.id;
                            return (
                              <button
                                key={c.id}
                                onClick={() => openInspector(c)}
                                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-[11px] font-medium transition-all duration-200 ${
                                  isActive
                                    ? "bg-primary/15 border-primary/50 text-primary shadow-[0_0_12px_rgba(var(--primary-rgb),0.25)]"
                                    : "bg-surface-container hover:bg-surface-container-high border-outline-variant/50 text-on-surface-variant hover:text-primary hover:border-primary/30"
                                }`}
                              >
                                <span className="material-symbols-outlined text-[13px]">
                                  {c.steps[0]?.type === "sql" ? "database" : c.steps[0]?.type === "vector" ? "hub" : "description"}
                                </span>
                                {c.title}
                                <span className={`ml-1 text-[10px] rounded-full px-1.5 py-0.5 font-bold ${isActive ? "bg-primary/20 text-primary" : "bg-surface-container-high text-outline"}`}>
                                  {c.steps.length} steps
                                </span>
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}

            {loading && (
              <div className="flex justify-start w-full max-w-4xl mx-auto gap-4">
                <div className="w-8 h-8 rounded-full bg-primary/50 flex items-center justify-center shrink-0 mt-1 animate-pulse">
                  <span className="material-symbols-outlined text-on-primary text-[18px]" style={{ fontVariationSettings: "'FILL' 1" }}>
                    smart_toy
                  </span>
                </div>
                <div className="bg-surface-container-low border border-outline-variant/30 rounded-2xl rounded-tl-sm px-5 py-4 w-32 animate-pulse flex items-center justify-center">
                  <span className="text-on-surface-variant/50 text-sm font-bold tracking-widest">...</span>
                </div>
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="p-4 md:p-6 bg-surface-container-lowest/90 backdrop-blur-md border-t border-outline-variant/20 sticky bottom-0 w-full">
            <div className="max-w-3xl mx-auto relative flex items-end gap-2 bg-surface-container rounded-xl border border-outline-variant/50 p-2 focus-within:border-primary focus-within:ring-1 focus-within:ring-primary transition-all">
              <textarea
                className="w-full bg-transparent border-none focus:ring-0 resize-none font-body-md text-on-surface py-2 max-h-32 min-h-[44px] pl-2"
                onChange={e => setInputText(e.target.value)}
                onKeyDown={e => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                value={inputText}
                placeholder="Ask about Ghana Healthcare..."
                rows={1}
                disabled={loading}
              />
              {loading ? (
                <button
                  aria-label="Stop generation"
                  onClick={() => abortControllerRef.current?.abort()}
                  className="p-2 text-red-500 hover:bg-red-500/10 rounded-lg transition-colors shrink-0 flex items-center justify-center w-10 h-10"
                >
                  <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>stop_circle</span>
                </button>
              ) : (
                <button
                  aria-label="Send message"
                  onClick={handleSend}
                  className="p-2 bg-primary text-on-primary hover:bg-primary/90 rounded-lg transition-colors shrink-0 flex items-center justify-center w-10 h-10 disabled:opacity-50"
                  disabled={!inputText.trim()}
                >
                  <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>send</span>
                </button>
              )}
            </div>
            <div className="text-center mt-2">
              <span className="font-label-sm text-outline text-[10px]">
                Sankofa AI can make mistakes. Verify critical medical data.
              </span>
            </div>
          </div>
        </main>
      </div>

      {/* Context Inspector — slides in from the right */}
      <ContextInspector citation={activeCitation} onClose={() => setActiveCitation(null)} />

      {/* Backdrop dimmer when panel open */}
      {activeCitation && (
        <div
          className="fixed inset-0 z-40 bg-black/20 backdrop-blur-[1px] pointer-events-none"
          style={{ right: "480px" }}
        />
      )}

      {/* Quota Exceeded Modal */}
      {showQuotaModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="bg-surface-container rounded-2xl max-w-sm w-full p-6 border border-outline-variant/30 shadow-2xl flex flex-col items-center">
            <div className="w-12 h-12 rounded-full bg-error-container/20 flex items-center justify-center mb-4">
              <span className="material-symbols-outlined text-error text-[24px]">credit_card_off</span>
            </div>
            <h3 className="text-xl font-headline-md font-bold text-center mb-2 text-on-surface">Quota Exceeded</h3>
            <p className="text-on-surface-variant text-center font-body-md mb-6 leading-relaxed">
              You have reached your API limit. Please recharge your account to continue generating AI insights.
            </p>
            <div className="flex gap-3 w-full">
              <button 
                onClick={() => setShowQuotaModal(false)}
                className="flex-1 py-2.5 rounded-lg border border-outline-variant/50 text-on-surface-variant font-bold hover:bg-surface-container-high transition-colors text-sm"
              >
                Dismiss
              </button>
              <Link href="/payment" className="flex-1">
                <button className="w-full py-2.5 rounded-lg bg-primary text-on-primary font-bold hover:bg-primary/90 transition-colors text-sm">
                  Recharge
                </button>
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
