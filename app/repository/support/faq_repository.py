from app.domain.support.support_schema import FAQS, ContentType


class FaqRepository:
    def fetch_all(self):
        return FAQS.select()

    def fetch_all_by_content_type_category_and_question(self):
        return (FAQS.select()
                .where(FAQS.content_type.in_([ContentType.Category, ContentType.Question])))

    def fetch_answer_action_by_parent_id(self, parent_id):
        return (FAQS.select()
                .where((FAQS.parent_id == parent_id)
                       & (FAQS.content_type.in_([ContentType.Answer, ContentType.Action]))).get())

    def fetch_all_ordered_by_parent_content_type_and_rank(self):
        return (FAQS.select()
                .order_by(FAQS.parent_id.desc(), FAQS.content_type, FAQS.rank))

