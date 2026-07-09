import React, { useEffect, useRef, useState } from "react";
import { Send, ArrowLeft, RotateCcw, X, MessageCircle } from "lucide-react";

const FONT_STYLES = `
  html, body, #root { width: 100%; min-height: 100%; margin: 0; font-family: 'Times New Roman', Times, serif; }
  * { box-sizing: border-box; }
  .font-display { font-family: 'Times New Roman', Times, serif; }
  .font-body { font-family: 'Times New Roman', Times, serif; }
  .font-mono { font-family: 'Times New Roman', Times, serif; }

  @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
  .cursor-blink { animation: blink 1s step-end infinite; }

  @keyframes dotPulse {
    0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
    40% { transform: scale(1); opacity: 1; }
  }
  .dot-pulse { animation: dotPulse 1.2s infinite ease-in-out; }

  @keyframes riseIn {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .rise-in { animation: riseIn 0.25s ease-out; }

  @keyframes chatSlideIn {
    from { opacity: 0; transform: translateX(60px) scale(0.985); }
    to { opacity: 1; transform: translateX(0) scale(1); }
  }
  .chat-slide-in { animation: chatSlideIn 0.55s ease-out both; }

  @keyframes introFadeOut {
    from { opacity: 1; transform: translateX(0); }
    to { opacity: 0; transform: translateX(-48px); }
  }
  .intro-fade-out { animation: introFadeOut 0.45s ease-in both; }

  @keyframes subtitleIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .subtitle-in { animation: subtitleIn 0.45s ease-out both; }
`;

const TARGET_TITLE = "DECODE LABS";
const APP_ICON_SRC = "/decodelabs-icon.png";

function useTypewriter(text, speed = 90, startDelay = 250) {
  const [display, setDisplay] = useState("");
  const [done, setDone] = useState(false);

  useEffect(() => {
    setDisplay("");
    setDone(false);

    let interval;
    const startTimer = setTimeout(() => {
      let index = 0;

      interval = setInterval(() => {
        index += 1;
        setDisplay(text.slice(0, index));

        if (index >= text.length) {
          clearInterval(interval);
          setDone(true);
        }
      }, speed);
    }, startDelay);

    return () => {
      clearTimeout(startTimer);
      clearInterval(interval);
    };
  }, [text, speed, startDelay]);

  return { display, done };
}

const URL_OR_EMAIL = /((?:https?:\/\/)[^\s]+|[\w.+-]+@[\w-]+\.[\w.-]+)/g;

function linkify(text) {
  if (!text) return text;
  const parts = text.split(URL_OR_EMAIL);
  return parts.map((part, i) => {
    if (!part) return null;
    if (/^https?:\/\//.test(part)) {
      const trailing = part.match(/[).,!?]+$/)?.[0] ?? "";
      const clean = trailing ? part.slice(0, -trailing.length) : part;
      return (
        <React.Fragment key={i}>
          <a
            href={clean}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-400 underline decoration-blue-400/40 underline-offset-2 hover:text-blue-300 hover:decoration-blue-300 break-all"
          >
            {clean}
          </a>
          {trailing}
        </React.Fragment>
      );
    }
    if (/^[\w.+-]+@[\w-]+\.[\w.-]+$/.test(part)) {
      return (
        <a
          key={i}
          href={`mailto:${part}`}
          className="text-blue-400 underline decoration-blue-400/40 underline-offset-2 hover:text-blue-300 hover:decoration-blue-300 break-all"
        >
          {part}
        </a>
      );
    }
    return <React.Fragment key={i}>{part}</React.Fragment>;
  });
}

function HorizontalCursor({ className = "" }) {
  return (
    <span
      className={`inline-block h-1 w-7 rounded-full bg-sky-400 align-middle cursor-blink ${className}`}
      aria-hidden="true"
    />
  );
}

function cleanBotTitle(title) {
  if (!title) return title;
  return title.replace(/🤖/g, "").replace(/\s{2,}/g, " ").trim();
}

function TypingDots() {
  return (
    <div className="flex items-center gap-1.5 px-4 py-3">
      <span className="w-1.5 h-1.5 rounded-full bg-sky-400 dot-pulse" style={{ animationDelay: "0ms" }} />
      <span className="w-1.5 h-1.5 rounded-full bg-sky-400 dot-pulse" style={{ animationDelay: "150ms" }} />
      <span className="w-1.5 h-1.5 rounded-full bg-sky-400 dot-pulse" style={{ animationDelay: "300ms" }} />
    </div>
  );
}

function IntroScreen({ typedTitle, typingDone, leaving }) {
  return (
    <div
      className={`fixed inset-0 z-50 flex items-center justify-center bg-black px-6 ${
        leaving ? "intro-fade-out" : ""
      }`}
    >
      <div className="text-center">
        <div className="flex items-center justify-center gap-2">
          <h1 className="font-display text-4xl sm:text-6xl md:text-7xl font-bold tracking-tight text-slate-100">
            {typedTitle}
          </h1>
          <HorizontalCursor className="mt-5 sm:mt-8" />
        </div>

        {typingDone && (
          <p className="subtitle-in mt-3 font-body text-sm sm:text-base italic tracking-wide text-slate-400">
            Your 24-hour Assistant
          </p>
        )}
      </div>
    </div>
  );
}

export default function DecodeLabsChat() {
  const [apiBase] = useState("http://localhost:8000");
  const [, setConnected] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]); // {id, role, title, intro, message, options, isError, canGoBack}
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [showIntro, setShowIntro] = useState(true);
  const [introLeaving, setIntroLeaving] = useState(false);
  const [appClosed, setAppClosed] = useState(false);
  const scrollRef = useRef(null);
  const { display: typedTitle, done: typingDone } = useTypewriter(TARGET_TITLE);

  const scrollToBottom = () => {
    requestAnimationFrame(() => {
      scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
    });
  };

  const loadMenu = async (base) => {
    setLoading(true);
    try {
      const res = await fetch(`${base}/menu`);
      if (!res.ok) throw new Error("bad status");
      const data = await res.json();
      setConnected(true);
      setSessionId(data.session_id);
      setMessages([
        {
          id: crypto.randomUUID(),
          role: "bot",
          title: data.title,
          intro: data.intro,
          message: data.message,
          options: data.options,
          canGoBack: data.can_go_back,
          isError: false,
        },
      ]);
    } catch (err) {
      setConnected(false);
      setMessages([
        {
          id: crypto.randomUUID(),
          role: "bot",
          title: "Connection issue",
          intro: "",
          message: `Couldn't reach the backend at ${base}. Make sure your FastAPI server is running (uvicorn main:app --reload) and reachable from this page, then hit retry.`,
          options: [],
          canGoBack: false,
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
      scrollToBottom();
    }
  };

  useEffect(() => {
    loadMenu(apiBase);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!typingDone) return;

    const holdTimer = setTimeout(() => setIntroLeaving(true), 900);
    const removeTimer = setTimeout(() => setShowIntro(false), 1400);

    return () => {
      clearTimeout(holdTimer);
      clearTimeout(removeTimer);
    };
  }, [typingDone]);

  useEffect(scrollToBottom, [messages, loading]);

  const sendMessage = async (rawValue, displayLabel) => {
    const value = rawValue.trim();
    if (!value || loading) return;

    setMessages((prev) => [
      ...prev.map((m) =>
        m.role === "bot" ? { ...m, options: [], canGoBack: false } : m
      ),
      { id: crypto.randomUUID(), role: "user", message: displayLabel ?? value },
    ]);
    setInputValue("");
    setLoading(true);

    try {
      const res = await fetch(`${apiBase}/chatbot`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: value, session_id: sessionId }),
      });
      if (!res.ok) throw new Error("bad status");
      const data = await res.json();
      setConnected(true);
      setSessionId(data.session_id);
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "bot",
          title: data.title,
          intro: data.intro,
          message: data.message,
          options: data.options,
          canGoBack: data.can_go_back,
          isError: data.is_error,
        },
      ]);
    } catch (err) {
      setConnected(false);
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "bot",
          title: "Connection issue",
          intro: "",
          message: `Lost the connection to ${apiBase}. Check that the backend is running, then try again.`,
          options: [],
          canGoBack: false,
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleOptionClick = (opt) => sendMessage(opt.key, opt.label);
  const handleBack = () => sendMessage("back", "← Back");
  const handleRestart = () => sendMessage("menu", "↺ Restart");
  const handleSubmitInput = (e) => {
    e.preventDefault();
    sendMessage(inputValue, inputValue);
  };

  const handleCloseWindow = () => {
    window.close();
    setTimeout(() => setAppClosed(true), 100);
  };

  if (appClosed) {
    return (
      <div className="w-screen h-screen h-[100dvh] flex items-center justify-center bg-black font-body text-slate-400">
        <style>{FONT_STYLES}</style>
        <div className="flex flex-col items-center gap-5 text-center rise-in">
          <img src={APP_ICON_SRC} alt="Decode Labs icon" className="h-12 w-12 object-contain" />
          <p className="italic">Decode Labs Assistant Closed</p>
          <button
            onClick={() => setAppClosed(false)}
            className="flex h-14 w-14 items-center justify-center rounded-full border border-slate-700 bg-slate-900 text-sky-400 shadow-xl shadow-black/30 transition-colors hover:border-sky-400/70 hover:bg-black hover:text-sky-300"
            aria-label="Reopen Decode Labs Assistant"
            title="Reopen chat"
          >
            <MessageCircle size={26} />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-screen h-screen h-[100dvh] overflow-hidden bg-black font-body text-slate-100">
      <style>{FONT_STYLES}</style>

      {showIntro && (
        <IntroScreen typedTitle={typedTitle} typingDone={typingDone} leaving={introLeaving} />
      )}

      <div className={`${showIntro ? "" : "chat-slide-in"} w-full h-full min-h-0 flex flex-col overflow-hidden bg-slate-950`}>
        {/* Header */}
        <div className="flex items-center justify-between px-5 sm:px-8 py-4 border-b border-slate-800 bg-black/70 backdrop-blur">
          <div className="flex items-center gap-3">
            <img
              src={APP_ICON_SRC}
              alt="Decode Labs icon"
              className="h-9 w-9 shrink-0 object-contain"
            />
            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-display font-bold text-lg sm:text-xl tracking-tight text-slate-100">
                  DECODE LABS
                </h1>
                <HorizontalCursor className="w-5" />
              </div>
              <p className="mt-0.5 text-[11px] sm:text-xs italic text-slate-500">
                Your 24-hour Assistant
              </p>
            </div>
          </div>
          <button
            onClick={handleCloseWindow}
            className="p-2 rounded-lg text-slate-400 hover:text-red-400 hover:bg-slate-800 transition-colors"
            aria-label="Close window"
            title="Close window"
          >
            <X size={20} />
          </button>
        </div>

        {/* Messages */}
        <div ref={scrollRef} className="flex-1 min-h-0 overflow-y-auto px-4 sm:px-8 lg:px-24 py-6 space-y-3">
          {messages.map((m) =>
            m.role === "user" ? (
              <div key={m.id} className="flex justify-end rise-in">
                <div className="max-w-[80%] sm:max-w-[65%] bg-blue-500 text-slate-950 rounded-2xl rounded-tr-sm px-4 py-2 text-sm font-medium">
                  {m.message}
                </div>
              </div>
            ) : (
              <div key={m.id} className="flex justify-start rise-in">
                <div
                  className={`max-w-[88%] sm:max-w-[70%] lg:max-w-[58%] rounded-2xl rounded-tl-sm border px-4 py-3 ${
                    m.isError
                      ? "bg-red-950/40 border-red-900 text-red-200"
                      : "bg-slate-800/70 border-slate-700 text-slate-100"
                  }`}
                >
                  {cleanBotTitle(m.title) && (
                    <div className="font-display font-bold text-[13px] text-sky-400 mb-1">
                      {cleanBotTitle(m.title)}
                    </div>
                  )}
                  {m.intro && <div className="text-sm text-slate-300 mb-1">{m.intro}</div>}
                  {m.message && (
                    <div className="text-sm leading-relaxed">{linkify(m.message)}</div>
                  )}

                  {m.options && m.options.length > 0 && (
                    <div className="mt-3 flex flex-col gap-2">
                      {m.options.map((opt) => (
                        <button
                          key={opt.key}
                          onClick={() => handleOptionClick(opt)}
                          disabled={loading}
                          className="group flex w-full items-center gap-3 text-left text-sm bg-slate-900 hover:bg-black border border-slate-700 hover:border-blue-400/60 rounded-lg px-3 py-2.5 transition-colors disabled:opacity-50"
                        >
                          <span className="flex h-6 min-w-6 items-center justify-center rounded-full border border-slate-700 font-mono text-xs text-blue-400 group-hover:text-blue-300">
                            {opt.key}
                          </span>
                          <span className="text-slate-200">{opt.label}</span>
                        </button>
                      ))}
                    </div>
                  )}

                  {m.canGoBack && (
                    <button
                      onClick={handleBack}
                      disabled={loading}
                      className="mt-3 flex items-center gap-1 font-mono text-[11px] text-slate-500 hover:text-blue-400 transition-colors disabled:opacity-50"
                    >
                      <ArrowLeft size={12} /> back
                    </button>
                  )}
                </div>
              </div>
            )
          )}
          {loading && (
            <div className="flex justify-start rise-in">
              <div className="bg-slate-800/70 border border-slate-700 rounded-2xl rounded-tl-sm">
                <TypingDots />
              </div>
            </div>
          )}
        </div>

        {/* Footer / input */}
        <div className="border-t border-slate-800 bg-black/70 backdrop-blur px-3 sm:px-8 lg:px-24 py-3">
          <form onSubmit={handleSubmitInput} className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleRestart}
              disabled={loading}
              className="p-2 rounded-lg text-slate-400 hover:text-blue-400 hover:bg-slate-800 transition-colors disabled:opacity-50"
              aria-label="Restart"
              title="Back to main menu"
            >
              <RotateCcw size={16} />
            </button>
            <input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Type a number, 'back', or 'menu'…"
              className="flex-1 font-mono text-sm bg-slate-900 border border-slate-700 rounded-full px-4 py-2 text-slate-200 placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-sky-400/50"
            />
            <button
              type="submit"
              disabled={loading || !inputValue.trim()}
              className="p-2 rounded-full bg-sky-500 text-slate-950 hover:bg-sky-400 transition-colors disabled:opacity-40"
              aria-label="Send"
            >
              <Send size={16} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
