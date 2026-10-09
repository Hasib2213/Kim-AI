from app.database.mongodb import get_database
from app.utils.common import utcnow


async def log_ai_run(*, provider: str, model: str, operation: str, response=None, success: bool = True, error: str | None = None):
    """Best-effort usage logging; never breaks the main AI request."""
    try:
        usage = getattr(response, 'usage', None)
        doc = {
            'provider': provider,
            'model': model,
            'operation': operation,
            'success': success,
            'error': error,
            'created_at': utcnow(),
        }
        if usage is not None:
            for key in ('input_tokens', 'output_tokens', 'total_tokens'):
                value = getattr(usage, key, None)
                if value is not None:
                    doc[key] = value
        await get_database().ai_runs.insert_one(doc)
    except Exception:
        return
