from app.db.database import get_connection

def test_db_connection():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Tenta buscar dados da tabela 'posts'
        cursor.execute("SELECT * FROM posts;")
        results = cursor.fetchall()

        if results:
            print("Dados encontrados na tabela 'posts':")
            for row in results:
                print(f"ID: {row[0]}, Título: {row[1]}, Conteúdo: {row[2]}, Publicado: {row[3]}")
        else:
            print("A tabela 'posts' está vazia.")

        conn.close()
    except Exception as e:
        print(f"Erro ao conectar ou buscar dados: {e}")

if __name__ == "__main__":
    test_db_connection()
