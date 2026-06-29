# repository/daily_stats_repo.py
"""每日统计数据访问层"""
from config.database import get_db

def increment_doc_upload_count():
    """增加今日文档上传计数"""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO daily_stats (stat_date, doc_upload_count, qa_chat_count, 
                                      report_gen_count, kb_search_count, kb_create_count, active_user_count) 
                VALUES (%s, 1, 0, 0, 0, 0, 0) 
                ON DUPLICATE KEY UPDATE 
                    doc_upload_count = doc_upload_count + 1,
                    updated_at = NOW()
            """, (today,))