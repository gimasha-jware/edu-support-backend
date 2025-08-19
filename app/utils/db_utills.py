import mysql.connector
from mysql.connector import Error
from datetime import datetime
from werkzeug.security import generate_password_hash
from app.utils.config import Config

TABLE_SCHEMAS = {
    'users': """
        CREATE TABLE IF NOT EXISTS users (
            uid INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(100) UNIQUE NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            user_type ENUM('super_admin', 'admin', 'student', 'institute') NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
    """,

    'institutes': """
        CREATE TABLE IF NOT EXISTS institutes (
            iid INT AUTO_INCREMENT PRIMARY KEY,
            contact_email VARCHAR(100),
            legal_name VARCHAR(100) NOT NULL,
            description TEXT,
            contact_phone VARCHAR(20),
            billing_address TEXT,
            vat_number VARCHAR(20),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
    """,

    'admins': """
        CREATE TABLE IF NOT EXISTS admins (
            aid INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            role_description VARCHAR(255),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(uid) ON DELETE CASCADE
        );
    """,

    'students': """
        CREATE TABLE IF NOT EXISTS students (
            sid INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            age INT CHECK (age >= 0),
            qualification_level ENUM('school', 'o/l', 'a/l', 'undergraduate', 'graduate') DEFAULT 'school',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(uid) ON DELETE CASCADE
        );
    """,

    'student_search_filters': """
        CREATE TABLE IF NOT EXISTS student_search_filters (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            filters JSON NOT NULL,
            searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(sid) ON DELETE CASCADE
        );
    """,

    'student_exam_results': """
        CREATE TABLE IF NOT EXISTS student_exam_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            al_results JSON,
            ol_results JSON,
            z_score DECIMAL(5,3),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(sid) ON DELETE CASCADE
        );
    """,

    'courses': """
        CREATE TABLE IF NOT EXISTS courses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
    """,

    'course_streams': """
        CREATE TABLE IF NOT EXISTS course_streams (
            id INT PRIMARY KEY AUTO_INCREMENT ,
            course_id INT NOT NULL,
            stream VARCHAR(100),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        );
    """,

    'course_locations': """
        CREATE TABLE IF NOT EXISTS course_locations (
            id INT PRIMARY KEY AUTO_INCREMENT,
            course_id INT NOT NULL,
            location VARCHAR(100),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        );
    """,

    'course_education_mode': """
        CREATE TABLE IF NOT EXISTS course_education_mode (
            id INT PRIMARY KEY AUTO_INCREMENT,
            course_id INT NOT NULL,
            education_mode VARCHAR(20) NOT NULL,
            FOREIGN KEY (course_id) REFERENCES courses(id)
        );
    """,

    'course_media': """
        CREATE TABLE IF NOT EXISTS course_media (
            id INT PRIMARY KEY AUTO_INCREMENT,
            course_id INT NOT NULL,
            media_type VARCHAR(10) NOT NULL,
            media_url VARCHAR(255),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        );
    """,

    'student_bookmarked_courses': """
        CREATE TABLE IF NOT EXISTS student_bookmarked_courses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            course_id INT NOT NULL,
            bookmarked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(sid) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
            UNIQUE KEY unique_bookmark (student_id, course_id)
        );
    """,

}

EXTRA_COLUMNS = {
  'courses': [
        {"name": "sub_content", "type": "VARCHAR(140)"},
        {"name": "institute_type", "type": "VARCHAR(20) NOT NULL"},
        {"name": "category", "type": "VARCHAR(50) NOT NULL"},
        {"name": "course_duration", "type": "INT NOT NULL"},
        {"name": "course_fee", "type": "DECIMAL(10,2) NOT NULL"},
        {"name": "install_availability", "type": "BOOLEAN NOT NULL"},
        {"name": "instructor", "type": "VARCHAR(100)"},
        {
            "name": "course_level", 
            "type": "ENUM('primary education', 'junior education', 'ordinary level', 'advanced level', 'certificate', 'NVQ', 'diploma', 'higher national diploma', 'degree', 'masters', 'PhD') NOT NULL"
        },

    ]
}

def create_database():
    """Create database if it doesn't exist"""
    conn = None
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
        )
        
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME}")
        print(f"Database '{Config.DB_NAME}' created successfully or already exists")
            
    except Error as e:
        print(f"Error creating database: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_db_connection():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )

def create_tables():
    """Create all required tables"""
    try:
        conn = get_db_connection()
        if conn.is_connected():
            print("Connected to the database")
        
        cursor = conn.cursor(dictionary=True)
        for table, query in TABLE_SCHEMAS.items():
            # print(f"Checking table: {table}")
            cursor.execute(query)
            conn.commit()
            # print(f"{table} table created successfully!")
        
    except Error as e:
        print(f"Error creating tables: {e}")
    
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def alter_columns():
  conn = get_db_connection()
  cursor = conn.cursor()
  
  for table, columns in EXTRA_COLUMNS.items():
    for col in columns:
      col_name = col["name"]
      col_type = col["type"]
      
      cursor.execute(f"""
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{Config.DB_NAME}'
        AND TABLE_NAME = '{table}'
        AND COLUMN_NAME = '{col_name}';
      """)
      
      if cursor.fetchone()[0] == 0:
        alter_query = f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type};"
        print(f"Adding column: {col_name} to table: {table}")
        cursor.execute(alter_query)
              
  conn.commit()
  cursor.close()
  conn.close()

def create_default_users():
    """Create default admin users"""
    try:
        conn = get_db_connection()

        with conn.cursor(dictionary=True) as cursor:
            # Check if super admin exists
            cursor.execute("SELECT uid FROM users WHERE user_type = 'super_admin'")
            if not cursor.fetchone():
                # Create super admin
                super_admin_password = generate_password_hash('admin123')
                cursor.execute("""
                    INSERT INTO users (email, first_name, last_name, password_hash, user_type)
                    VALUES (%s, %s, %s, %s, %s)
                """, ('superadmin@example.com', 'Super', 'Admin', super_admin_password, 'super_admin'))
                print("Super admin created successfully!")
            
            # Check if admin exists
            cursor.execute("SELECT uid FROM users WHERE user_type = 'admin'")
            if not cursor.fetchone():
                # Create admin
                admin_password = generate_password_hash('admin123')
                cursor.execute("""
                    INSERT INTO users (email, first_name, last_name, password_hash, user_type)
                    VALUES (%s, %s, %s, %s, %s)
                """, ('admin@example.com', 'Admin', 'User', admin_password, 'admin'))
                print("Admin user created successfully!")

            conn.commit()

    except Error as e:
        print(f"Error creating default users: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def apply_schema_updates():
    """Main function to set up the database"""
    print("Setting up database...")
    try:
        create_database()
        create_tables()
        create_default_users()
    except Exception as e:
        print(f"Database setup is not completed: {e}")
        return
    print("Database setup completed!")

if __name__ == "__main__":
    apply_schema_updates()