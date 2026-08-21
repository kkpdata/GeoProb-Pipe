from typing import Optional
import sqlite3


class State:

    def __init__(self, geoprob_pipe_file_path: str):
        self.geoprob_pipe_file_path: str = geoprob_pipe_file_path

    def retrieve_question_answer(self, question: str) -> Optional[str]:
        """ The terminal user interface has a workflow of questions that the users answers. This
        method retrieves the answer to a question (if already stored). """
        conn = sqlite3.connect(self.geoprob_pipe_file_path)
        cursor = conn.cursor()
        try:
            cursor.execute(f"""
                SELECT answer
                FROM workflow_questions
                WHERE question_label = '{question}'
                LIMIT 1;
            """)
        except sqlite3.OperationalError:  # table does not exist
            return None
        result = cursor.fetchone()
        if not result:
            return None
        return result[0]

    def store_question_answer(self, question_label: str, answer: str):
        conn = sqlite3.connect(self.geoprob_pipe_file_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_questions (
                question_label TEXT PRIMARY KEY,
                answer TEXT
            )
        """)

        cursor.execute(f"""
            INSERT INTO workflow_questions (
                question_label,
                answer
            )
            VALUES (?, ?)
            ON CONFLICT(question_label)
            DO UPDATE SET answer = excluded.answer
        """, (question_label, answer))

        conn.commit()
        conn.close()
