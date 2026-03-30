import sqlite3
import os
from datetime import datetime
from utils.logger import logger_instance as logger

class DatabaseManager:
    def __init__(self, db_path="./data/qubixa.db"):
        self.db_path = db_path
        self._ensure_db_dir()
        self._initialize_db()

    def _ensure_db_dir(self):
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _initialize_db(self):
        conn = self._get_connection()
        cursor = conn.cursor()

        # Agents Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                role TEXT,
                system_prompt TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Agent Logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER,
                log_type TEXT,
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(agent_id) REFERENCES agents(id)
            )
        ''')

        # Agent History
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER,
                input TEXT,
                output TEXT,
                performance_metrics TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(agent_id) REFERENCES agents(id)
            )
        ''')

        # Skills Index
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skills_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_name TEXT UNIQUE,
                skill_type TEXT,
                description TEXT,
                last_scanned TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Chat Messages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER,
                sender TEXT,
                message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(agent_id) REFERENCES agents(id)
            )
        ''')

        # Seed initial agents
        cursor.execute("INSERT OR IGNORE INTO agents (name, role, system_prompt) VALUES ('Analyzer Agent', 'Campaign Analyst', 'You are a campaign analyzer AI agent.')")
        cursor.execute("INSERT OR IGNORE INTO agents (name, role, system_prompt) VALUES ('Keyword Agent', 'Keyword Optimizer', 'You are a keyword optimization AI agent.')")

        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")

    # CRUD Methods
    def log_agent_activity(self, agent_name, log_type, content):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM agents WHERE name = ?", (agent_name,))
        agent = cursor.fetchone()
        if agent:
            cursor.execute("INSERT INTO agent_logs (agent_id, log_type, content) VALUES (?, ?, ?)",
                         (agent[0], log_type, str(content)))
            conn.commit()
        conn.close()

    def save_chat_message(self, agent_name, sender, message):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM agents WHERE name = ?", (agent_name,))
        agent = cursor.fetchone()
        if agent:
            cursor.execute("INSERT INTO chat_messages (agent_id, sender, message) VALUES (?, ?, ?)",
                         (agent[0], sender, message))
            conn.commit()
        conn.close()

    def get_agent_history(self, agent_name):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT h.input, h.output, h.timestamp 
            FROM agent_history h
            JOIN agents a ON h.agent_id = a.id
            WHERE a.name = ? 
            ORDER BY h.timestamp DESC
        """, (agent_name,))
        history = cursor.fetchall()
        conn.close()
        return history

db_manager = DatabaseManager()
