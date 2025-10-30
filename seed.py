from db import init_db, engine
from sqlmodel import Session
from models import SessionThread, ChatMessage

init_db()
with Session(engine) as s:
    t = SessionThread(role_raw="Senior Product Manager", industry_raw="Fitness Tech",
                      pains_raw="Too many context pings; manual release notes; planning churn",
                      role_normalized="Product Manager", onet_code=None)
    s.add(t); s.commit(); s.refresh(t)
    s.add(ChatMessage(thread_id=t.id, sender="system", content="Anti-To-Do assistant initialized."))
    s.add(ChatMessage(thread_id=t.id, sender="user",
        content=f"Role={t.role_raw}; Industry={t.industry_raw}; Pains={t.pains_raw}"))
    s.commit()
print("Seeded.")