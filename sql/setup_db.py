import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def ejecutar_init_sql():
    ruta_sql = "sql/init.sql"  # Ruta relativa al archivo
    with open(ruta_sql, "r", encoding="utf-8") as f:
        script = f.read()


    try:
        conexion = mysql.connector.connect(
            host = os.getenv("DB_HOST", "localhost"),
            user = os.getenv("MYSQL_USER", "root"),
            password = os.getenv("MYSQL_PASSWORD", "root"),
        )
        cursor = conexion.cursor()
        for statement in script.split(";"):
            stmt = statement.strip()
            if stmt:
                cursor.execute(stmt)
        conexion.commit()
        cursor.close()
        conexion.close()
        print("✅ Script SQL ejecutado correctamente.")
    except mysql.connector.Error as err:
        print(f"❌ Error al ejecutar el script SQL: {err}")

if __name__ == "__main__":
    ejecutar_init_sql()
