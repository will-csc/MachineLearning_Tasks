import os
import random


# Respostas empáticas para modo fallback (sem chave/API indisponível)
FALLBACK_RESPONSES = [
    "Sinto muito que você esteja passando por isso. Se quiser, posso ouvir — conte um pouco mais.",
    "Se estiver em perigo agora, por favor, procure ajuda imediata (polícia/serviços de emergência). Posso listar canais de apoio.",
    "Obrigado por compartilhar. Gostaria de informações sobre serviços de apoio locais ou dicas de segurança?"
]


def get_fallback_response() -> str:
    return random.choice(FALLBACK_RESPONSES)


def build_prompt(user_message: str, context: str | None = None) -> str:
    base = (
        "Você é um assistente empático e acolhedor para uma plataforma de denúncias e apoio chamada ApoioJá.\n"
        "Responda com empatia, segurança e sugira recursos apropriados. Não forneça diagnóstico profissional.\n\n"
    )
    if context:
        base += f"Contexto da conversa:\n{context}\n\n"
    base += f"Usuário: {user_message}\nResposta:"
    return base


def _load_env_key() -> str | None:
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key
    try:
        # tenta carregar do .env se existir
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv("GEMINI_API_KEY")
    except Exception:
        return None


def get_gemini_response(user_message: str, context: str | None = None) -> str | None:
    """Tenta obter resposta da API Gemini; retorna None se indisponível/erro."""
    api_key = _load_env_key()
    if not api_key:
        return None

    try:
        import google.generativeai as genai
    except Exception:
        # pacote não instalado
        return None

    try:
        genai.configure(api_key=api_key)
        prompt = build_prompt(user_message, context=context)

        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        model = genai.GenerativeModel(model_name)
        resp = model.generate_content(prompt)

        # Tenta extrair texto
        text = getattr(resp, "text", None)
        if not text and hasattr(resp, "candidates"):
            try:
                text = resp.candidates[0].content.parts[0].text
            except Exception:
                text = None

        if text:
            max_chars = int(os.getenv("CHATBOT_MAX_CHARS", "600"))
            return text[:max_chars]

        return None
    except Exception:
        # qualquer erro da API/provedor → fallback pelo chamador
        return None