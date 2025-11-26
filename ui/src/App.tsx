import { useState } from "react";

// ---- Types ----
interface UsedChunk {
  ticket_id: string;
  product_tag: string;
  chunk_index: number;
  text: string;
}

interface ApiResponse {
  answer: string;
  source_ticket_ids: string[];
  used_chunks: UsedChunk[];
  metadata?: any;
}

export default function App() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

  const sendQuery = async () => {
    setLoading(true);
    setError("");
    setResponse(null);

    try {
      const res = await fetch(`${API_URL}/v1/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer mock-token",
        },
        body: JSON.stringify({
          question,
          max_context_chunks: 5,
        }),
      });

      if (!res.ok) throw new Error(`Request failed: ${res.status}`);

      const data: ApiResponse = await res.json();
      setResponse(data);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Unknown error occurred";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#f3f4f6",
        padding: "40px 20px",
        fontFamily: "Inter, Arial",
        display: "flex",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "750px",
          background: "white",
          padding: "30px",
          borderRadius: "16px",
          boxShadow: "0 8px 30px rgba(0,0,0,0.08)",
        }}
      >
        <h1
          style={{
            fontSize: "28px",
            marginBottom: "20px",
            fontWeight: 700,
            color: "#111827",
          }}
        >
          🔍 Ask Your Knowledge Base
        </h1>

        {/* Input */}
        <textarea
          rows={3}
          placeholder="Type your question here..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          style={{
            width: "100%",
            padding: "14px",
            borderRadius: "12px",
            border: "1px solid #d1d5db",
            fontSize: "15px",
            resize: "none",
            outline: "none",
            transition: "0.2s border-color",
          }}
          onFocus={(e) =>
            ((e.target as HTMLTextAreaElement).style.borderColor = "#2563eb")
          }
          onBlur={(e) =>
            ((e.target as HTMLTextAreaElement).style.borderColor = "#d1d5db")
          }
        />

        <button
          onClick={sendQuery}
          style={{
            marginTop: "15px",
            padding: "12px 18px",
            background: "#2563eb",
            color: "white",
            border: "none",
            borderRadius: "10px",
            fontSize: "16px",
            cursor: "pointer",
            fontWeight: 600,
            transition: "0.2s background",
          }}
          onMouseEnter={(e) =>
            ((e.target as HTMLButtonElement).style.background = "#1d4ed8")
          }
          onMouseLeave={(e) =>
            ((e.target as HTMLButtonElement).style.background = "#2563eb")
          }
        >
          {loading ? "Thinking..." : "Ask"}
        </button>

        {/* Loading */}
        {loading && (
          <div style={{ marginTop: "20px", fontSize: "16px", color: "#6b7280" }}>
            ⏳ Processing your question...
          </div>
        )}

        {/* Error */}
        {error && (
          <div
            style={{
              background: "#fee2e2",
              color: "#b91c1c",
              padding: "12px",
              marginTop: "20px",
              borderRadius: "10px",
            }}
          >
            ⚠️ {error}
          </div>
        )}

        {/* Response */}
        {response && (
          <div style={{ marginTop: "30px" }}>
            <div
              style={{
                background: "#f0f9ff",
                borderLeft: "6px solid #38bdf8",
                padding: "18px",
                borderRadius: "10px",
                marginBottom: "20px",
              }}
            >
              <h2 style={{ margin: 0, fontSize: "20px", fontWeight: 600 }}>
                ✅ Answer
              </h2>
              <p style={{ marginTop: "10px", fontSize: "15px", lineHeight: 1.6 }}>
                {response.answer}
              </p>
            </div>

            <div
              style={{
                background: "#f9fafb",
                padding: "18px",
                borderRadius: "10px",
                marginBottom: "20px",
                border: "1px solid #e5e7eb",
              }}
            >
              <h3 style={{ margin: 0, fontSize: "17px", fontWeight: 600 }}>
                📁 Source Ticket IDs
              </h3>
              <ul style={{ marginTop: "10px", paddingLeft: "20px" }}>
                {response.source_ticket_ids.map((id) => (
                  <li key={id} style={{ fontSize: "15px" }}>
                    {id}
                  </li>
                ))}
              </ul>
            </div>

            <div
              style={{
                background: "#f9f9ff",
                padding: "18px",
                borderRadius: "10px",
                border: "1px solid #e0e7ff",
              }}
            >
              <h3 style={{ margin: 0, fontSize: "17px", fontWeight: 600 }}>
                🧩 Context Used
              </h3>

              {response.used_chunks.map((chunk, index) => (
                <div
                  key={index}
                  style={{
                    marginTop: "12px",
                    padding: "12px",
                    background: "white",
                    borderRadius: "8px",
                    border: "1px solid #e5e7eb",
                  }}
                >
                  <div style={{ fontSize: "14px", color: "#6b7280" }}>
                    <strong>{chunk.ticket_id}</strong> — {chunk.product_tag}
                  </div>
                  <p style={{ marginTop: "6px", fontSize: "15px" }}>
                    {chunk.text}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
