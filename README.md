# ET Voice Concierge

Production-ready scaffold for a real-time voice concierge that answers Exotel calls, performs LLM-driven reasoning, recommends ET products, and executes follow-up actions (SMS/links) with streaming audio in/out.

## System Flow (End-to-End)
1. Caller dials your Exotel number.
2. Exotel hits your webhook `/voice` with caller metadata.
3. Backend replies with XML to greet and start audio streaming to your WebSocket server.
4. Audio chunks arrive on `/audio-stream` (WebSocket).
5. STT converts audio -> text (Deepgram suggested).
6. Agent orchestrator runs reasoning + tool calls (OpenAI GPT-4o suggested).
7. Actions executed (send SMS/WhatsApp, recommend ET product, log to DB).
8. TTS converts reply -> audio (ElevenLabs/OpenAI TTS suggested).
9. Audio is streamed back to Exotel -> caller hears response.

## Tech Stack
- Telephony: Exotel Voice API
- Backend: FastAPI + WebSockets
- Speech: Deepgram (streaming STT), ElevenLabs/OpenAI TTS
- AI: OpenAI GPT-4o with function calling
- Data: Supabase/PostgreSQL (for profiles, logs, sessions)

## Repo Structure
```
et-voice-concierge/
├── backend/
│   ├── main.py                 # FastAPI app entry
│   ├── exotel_webhook.py       # /voice webhook, returns XML
│   ├── websocket_server.py     # /audio-stream WebSocket handler
│   ├── agents/
│   │   ├── orchestrator.py
│   │   ├── conversation_agent.py
│   │   ├── profiling_agent.py
│   │   ├── recommendation_agent.py
│   │   ├── action_agent.py
│   │   └── memory_agent.py
│   ├── services/
│   │   ├── stt_service.py
│   │   ├── tts_service.py
│   │   ├── llm_service.py
│   ├── tools/
│   │   ├── et_products.json
│   │   ├── send_sms.py
│   │   └── send_whatsapp.py
│   ├── config.py
│   ├── requirements.txt
│   └── .env.example
└── README.md
```

## Quickstart
1. Install Python 3.11+ and `uvicorn` (comes via requirements).
2. Copy env template:
   ```bash
   cp backend/.env.example backend/.env
   ```
3. Install deps:
   ```bash
   cd backend
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Run API + WebSocket server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
5. Expose publicly (for Exotel) via HTTPS tunnel (e.g., `cloudflared` or `ngrok`) and set Exotel Incoming Call URL to `https://your-server.com/voice`.

## Exotel Webhook Contract
- Exotel sends POST to `/voice` with `CallSid`, `From`, and metadata.
- You must respond with XML:
  ```xml
  <Response>
      <Say voice="female">Welcome to ET AI Concierge</Say>
      <Connect>
          <Stream url="wss://your-server.com/audio-stream"/>
      </Connect>
  </Response>
  ```
- Streaming starts immediately; keep responses short to cut latency.

## WebSocket Audio Loop
- Client: Exotel streams raw audio frames.
- Server: for each chunk
   1. STT: `stt_service.transcribe_chunk` -> text
   2. Orchestrator: `run_agent_pipeline` -> tool calls + reply
   3. TTS: `tts_service.synthesize` -> audio bytes
   4. Send audio bytes back on the same socket

## Agents (single responsibility)
- Conversation Agent: maintain dialog tone, follow-ups.
- Profiling Agent: extract profile (experience, goal, risk) and context.
- Recommendation Agent: map intents to ET products (reads `tools/et_products.json`).
- Action Agent: execute tools (send SMS/WhatsApp) and log outcomes.
- Memory Agent: persist session state/profile.
- Orchestrator: glue that calls the above and handles function-calling payloads.

## Environment
See `backend/.env.example` for required keys (Exotel, Deepgram, OpenAI, ElevenLabs, Supabase). Use separate service accounts for staging vs. demo.

## Demo Script (suggested)
- Demo 1: "I want to start investing" → profile beginner → recommend ET Markets → SMS link sent.
- Demo 2: "I already invest in stocks" → detect advanced → suggest ET Prime.
- Demo 3: "I want a home loan" → pivot intent → suggest relevant ET service → send WhatsApp link.

## Production Notes
- Optimize latency: streaming STT/TTS, short turns, async IO.
- Reliability: timeouts on upstream calls, retries for SMS/WhatsApp, circuit breakers.
- Observability: request/response logging (redact PII), metrics on latency per turn.
- Security: validate Exotel signatures, lock down WebSocket origin, secure secrets.
- Persistence: Supabase/Postgres for session/memory, cold-start prewarm for TTS.
