from abc import ABC, abstractmethod


class AIProvider(ABC):
    @abstractmethod
    async def generate_text(self, *, system: str, messages: list[dict], model: str | None = None) -> str:
        raise NotImplementedError

    @abstractmethod
    async def generate_json(self, *, system: str, prompt: str, model: str | None = None) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def analyze_image(self, *, image_data_url: str, prompt: str, model: str | None = None) -> dict:
        raise NotImplementedError
