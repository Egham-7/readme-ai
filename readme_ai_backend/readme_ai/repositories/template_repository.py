from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.template import Template


class TemplateRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(
        self,
        content: str,
        user_id: Optional[str] = None,
        preview_image: Optional[str] = None,
    ) -> Template:
        template = Template(
            content=content, user_id=user_id, preview_image=preview_image
        )
        self.db_session.add(template)
        self.db_session.commit()
        self.db_session.refresh(template)
        return template

    def get_by_id(self, template_id: int) -> Optional[Template]:
        return (
            self.db_session.query(Template).filter(Template.id == template_id).first()
        )

    def get_all(self) -> List[Template]:
        return self.db_session.query(Template).all()

    def update(
        self, template_id: int, content: str, preview_image: Optional[str] = None
    ) -> Optional[Template]:
        template = self.get_by_id(template_id)
        if template:
            template.content = content
            if preview_image is not None:
                template.preview_image = preview_image
            self.db_session.commit()
            self.db_session.refresh(template)
        return template

    def delete(self, template_id: int) -> bool:
        template = self.get_by_id(template_id)
        if template:
            self.db_session.delete(template)
            self.db_session.commit()
            return True
        return False
