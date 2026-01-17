import psycopg2
import random
import string
from config import DB_CONFIG

class Database:
    def __init__(self):
        self.conn = None
        self.connect()
        self.init_db()
    
    def connect(self):
        """Подключение к базе данных"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
    
    def init_db(self):
        """Инициализация таблиц"""
        try:
            cur = self.conn.cursor()
            
            # Таблица пользователей
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username VARCHAR(255),
                    first_name VARCHAR(255),
                    unique_id VARCHAR(10) UNIQUE,
                    balance INTEGER DEFAULT 0,
                    is_banned BOOLEAN DEFAULT FALSE,
                    ban_reason TEXT,
                    ban_until TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица заказов
            cur.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id VARCHAR(10) PRIMARY KEY,
                    user_id BIGINT,
                    service_type VARCHAR(50),
                    description TEXT,
                    price INTEGER,
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # Таблица зеркальных ботов
            cur.execute('''
                CREATE TABLE IF NOT EXISTS mirror_bots (
                    token VARCHAR(255) PRIMARY KEY,
                    user_id BIGINT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # Таблица обращений в поддержку
            cur.execute('''
                CREATE TABLE IF NOT EXISTS support_tickets (
                    ticket_id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    message TEXT,
                    status VARCHAR(20) DEFAULT 'open',
                    response TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            self.conn.commit()
            cur.close()
        except Exception as e:
            print(f"Ошибка инициализации БД: {e}")
    
    def get_or_create_user(self, user_id, username, first_name):
        """Получение или создание пользователя"""
        cur = self.conn.cursor()
        
        # Проверяем существование пользователя
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cur.fetchone()
        
        if not user:
            # Создаем нового пользователя с уникальным ID
            unique_id = self.generate_unique_id()
            cur.execute('''
                INSERT INTO users (user_id, username, first_name, unique_id)
                VALUES (%s, %s, %s, %s)
            ''', (user_id, username, first_name, unique_id))
            self.conn.commit()
            user = (user_id, username, first_name, unique_id, 0, False, None, None)
        
        cur.close()
        return user
    
    def generate_unique_id(self):
        """Генерация уникального ID вида W-123456"""
        while True:
            numbers = ''.join(random.choices(string.digits, k=6))
            unique_id = f"W-{numbers}"
            
            cur = self.conn.cursor()
            cur.execute("SELECT COUNT(*) FROM users WHERE unique_id = %s", (unique_id,))
            count = cur.fetchone()[0]
            cur.close()
            
            if count == 0:
                return unique_id
    
    def get_user_balance(self, user_id):
        """Получение баланса пользователя"""
        cur = self.conn.cursor()
        cur.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
        result = cur.fetchone()
        cur.close()
        return result[0] if result else 0
    
    def update_balance(self, user_id, amount):
        """Обновление баланса пользователя"""
        cur = self.conn.cursor()
        cur.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s", (amount, user_id))
        self.conn.commit()
        cur.close()
    
    def set_balance(self, user_id, amount):
        """Установка баланса пользователя"""
        cur = self.conn.cursor()
        cur.execute("UPDATE users SET balance = %s WHERE user_id = %s", (amount, user_id))
        self.conn.commit()
        cur.close()
    
    def create_order(self, user_id, service_type, description, price):
        """Создание заказа"""
        order_id = ''.join(random.choices(string.digits, k=6))
        
        cur = self.conn.cursor()
        cur.execute('''
            INSERT INTO orders (order_id, user_id, service_type, description, price, status)
            VALUES (%s, %s, %s, %s, %s, 'pending')
        ''', (order_id, user_id, service_type, description, price))
        self.conn.commit()
        cur.close()
        
        return order_id
    
    def get_order(self, order_id):
        """Получение информации о заказе"""
        cur = self.conn.cursor()
        cur.execute('''
            SELECT o.*, u.unique_id, u.user_id as user_telegram_id
            FROM orders o
            JOIN users u ON o.user_id = u.user_id
            WHERE o.order_id = %s
        ''', (order_id,))
        order = cur.fetchone()
        cur.close()
        return order
    
    def update_order_status(self, order_id, status):
        """Обновление статуса заказа"""
        cur = self.conn.cursor()
        cur.execute("UPDATE orders SET status = %s WHERE order_id = %s", (status, order_id))
        self.conn.commit()
        cur.close()
    
    def add_mirror_bot(self, user_id, token):
        """Добавление зеркального бота"""
        cur = self.conn.cursor()
        try:
            cur.execute('''
                INSERT INTO mirror_bots (token, user_id)
                VALUES (%s, %s)
            ''', (token, user_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка добавления зеркального бота: {e}")
            return False
        finally:
            cur.close()
    
    def get_mirror_bots(self, user_id=None):
        """Получение списка зеркальных ботов"""
        cur = self.conn.cursor()
        if user_id:
            cur.execute('''
                SELECT mb.*, u.username, u.unique_id
                FROM mirror_bots mb
                JOIN users u ON mb.user_id = u.user_id
                WHERE mb.user_id = %s
            ''', (user_id,))
        else:
            cur.execute('''
                SELECT mb.*, u.username, u.unique_id
                FROM mirror_bots mb
                JOIN users u ON mb.user_id = u.user_id
            ''')
        bots = cur.fetchall()
        cur.close()
        return bots
    
    def create_support_ticket(self, user_id, message):
        """Создание обращения в поддержку"""
        cur = self.conn.cursor()
        cur.execute('''
            INSERT INTO support_tickets (user_id, message)
            VALUES (%s, %s)
            RETURNING ticket_id
        ''', (user_id, message))
        ticket_id = cur.fetchone()[0]
        self.conn.commit()
        cur.close()
        return ticket_id
    
    def get_support_ticket(self, ticket_id):
        """Получение обращения в поддержку"""
        cur = self.conn.cursor()
        cur.execute('''
            SELECT st.*, u.unique_id, u.user_id as user_telegram_id
            FROM support_tickets st
            JOIN users u ON st.user_id = u.user_id
            WHERE st.ticket_id = %s
        ''', (ticket_id,))
        ticket = cur.fetchone()
        cur.close()
        return ticket
    
    def respond_to_ticket(self, ticket_id, response):
        """Ответ на обращение в поддержку"""
        cur = self.conn.cursor()
        cur.execute('''
            UPDATE support_tickets 
            SET response = %s, status = 'closed'
            WHERE ticket_id = %s
        ''', (response, ticket_id))
        self.conn.commit()
        cur.close()
    
    def get_all_users(self):
        """Получение списка всех пользователей"""
        cur = self.conn.cursor()
        cur.execute('''
            SELECT user_id, username, first_name, unique_id, balance, is_banned
            FROM users
            ORDER BY created_at DESC
        ''')
        users = cur.fetchall()
        cur.close()
        return users
    
    def ban_user(self, unique_id, reason, days):
        """Блокировка пользователя"""
        cur = self.conn.cursor()
        
        if days == -1:
            ban_until = None
            is_banned = True
        else:
            cur.execute("SELECT NOW() + INTERVAL '%s days'", (days,))
            ban_until = cur.fetchone()[0]
            is_banned = False
        
        cur.execute('''
            UPDATE users 
            SET is_banned = %s, ban_reason = %s, ban_until = %s 
            WHERE unique_id = %s
        ''', (is_banned, reason, ban_until, unique_id))
        
        self.conn.commit()
        cur.close()
    
    def nullify_user(self, unique_id, reason):
        """Обнуление аккаунта пользователя"""
        cur = self.conn.cursor()
        
        # Генерируем новый уникальный ID
        new_unique_id = self.generate_unique_id()
        
        cur.execute('''
            UPDATE users 
            SET balance = 0, unique_id = %s
            WHERE unique_id = %s
            RETURNING user_id
        ''', (new_unique_id, unique_id))
        
        user_id = cur.fetchone()[0] if cur.rowcount > 0 else None
        self.conn.commit()
        cur.close()
        
        return user_id
    
    def get_user_by_unique_id(self, unique_id):
        """Получение пользователя по уникальному ID"""
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE unique_id = %s", (unique_id,))
        user = cur.fetchone()
        cur.close()
        return user
    
    def get_user_by_id(self, user_id):
        """Получение пользователя по ID Telegram"""
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()
        return user
    
    def close(self):
        """Закрытие соединения с БД"""
        if self.conn:
            self.conn.close()