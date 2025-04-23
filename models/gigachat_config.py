from db import Base
from sqlalchemy import Column, Text, Integer


# Таблица хранит промпт для гигачата
class GigachatConfig(Base):
    __tablename__ = 'gigachat_config'
    id: int = Column(Integer, primary_key=True)

    # промпт
    prompt: str = Column(Text, nullable=False)
    prompt1: str = Column(Text, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'prompt': self.prompt,
        }
