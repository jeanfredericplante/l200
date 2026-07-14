import os
import re
import json
import logging

# ==========================================
# 🔐 PII Redaction Mechanism
# ==========================================
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_REGEX = re.compile(r"\b(?:\+?1[-. ]?)?\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})\b")
SSN_REGEX = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
CREDIT_CARD_REGEX = re.compile(r"\b(?:\d[ -]*?){13,16}\b")

def redact_pii(text: str) -> str:
    """Redacts email addresses, phone numbers, SSNs, and credit cards from text to preserve user privacy."""
    if not isinstance(text, str):
        return text
    text = EMAIL_REGEX.sub("[REDACTED_EMAIL]", text)
    text = PHONE_REGEX.sub("[REDACTED_PHONE]", text)
    text = SSN_REGEX.sub("[REDACTED_SSN]", text)
    text = CREDIT_CARD_REGEX.sub("[REDACTED_CREDIT_CARD]", text)
    return text

# ==========================================
# 📊 Structured JSON Logging System
# ==========================================
class StructuredJSONFormatter(logging.Formatter):
    """Custom formatter to output structured JSON logs with PII redaction and active OpenTelemetry tracing context."""
    def format(self, record):
        # Base JSON log structure
        log_record = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%SZ"),
            "severity": record.levelname,
            "logger": record.name,
            "message": redact_pii(record.getMessage()),
        }
        
        # Exception formatting with safety redact
        if record.exc_info:
            log_record["exception"] = redact_pii(self.formatException(record.exc_info))
            
        # Intent-vs-Outcome logging fields
        if hasattr(record, "intent"):
            log_record["intent"] = redact_pii(record.intent)
        if hasattr(record, "outcome"):
            log_record["outcome"] = redact_pii(record.outcome)
        if hasattr(record, "user_id"):
            log_record["user_id"] = redact_pii(record.user_id)
            
        # Inject active trace context from OpenTelemetry
        try:
            from opentelemetry import trace
            current_span = trace.get_current_span()
            if current_span and current_span.get_span_context().is_valid:
                trace_id = current_span.get_span_context().trace_id
                log_record["trace_id"] = f"{trace_id:x}"
        except Exception:
            pass
            
        return json.dumps(log_record)

# Configure the active Logger to emit Structured JSON Logs
logger = logging.getLogger("agent_definition")
handler = logging.StreamHandler()
handler.setFormatter(StructuredJSONFormatter())
logger.handlers.clear()
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False

# ==========================================
# 🌌 OpenTelemetry Setup & Tracer Configuration
# ==========================================
# Enable OpenTelemetry semantic conventions for Generative AI
os.environ["OTEL_SEMCONV_STABILITY_OPT_IN"] = "gen_ai_latest_experimental"
# Ensure the full message content (prompts & responses) is captured in the trace events
os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "EVENT_ONLY"

tracer = None
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

    # Attempt to initialize tracer provider if not already set up
    provider = trace.get_tracer_provider()
    if not hasattr(provider, "add_span_processor"):
        provider = TracerProvider()
        try:
            processor = BatchSpanProcessor(OTLPSpanExporter())
            provider.add_span_processor(processor)
        except Exception as e:
            logger.warning(f"Failed to add OTLPSpanExporter: {str(e)}")
        trace.set_tracer_provider(provider)
    
    tracer = trace.get_tracer("l200_study_companion")
except Exception as e:
    logger.warning(f"OpenTelemetry initialization skipped: {str(e)}")
