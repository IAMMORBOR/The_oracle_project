import sqlite3
from config.settings import RESULTS_DB

def init_db():
    """Create the results table if it does not exist yet"""
    conn = sqlite3.connect(RESULTS_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            bug_id           TEXT,
            context_level    TEXT,
            run_number       INTEGER,
            compiled         INTEGER,
            catches_bug      INTEGER,
            passes_fixed     INTEGER,
            accurate         INTEGER,
            false_positive   INTEGER,
            false_negative   INTEGER,
            generated_oracle TEXT,
            timestamp        TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("Database ready.")

def save_result(data):
    """Save one experiment result to the database"""
    conn = sqlite3.connect(RESULTS_DB)
    conn.execute("""
        INSERT INTO results (
            bug_id, context_level, run_number,
            compiled, catches_bug, passes_fixed,
            accurate, false_positive, false_negative,
            generated_oracle, timestamp
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (
        data["bug_id"],
        data["context_level"],
        data["run_number"],
        int(data["compiled"]),
        int(data["catches_bug"]),
        int(data["passes_fixed"]),
        int(data["accurate"]),
        int(data["false_positive"]),
        int(data["false_negative"]),
        data["generated_oracle"],
        data["timestamp"],
    ))
    conn.commit()
    conn.close()