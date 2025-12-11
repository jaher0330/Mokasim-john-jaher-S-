from car_rental_system import get_db_connection

conn = get_db_connection()
if not conn:
    print('NO_DB_CONNECTION')
else:
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, email, password, role FROM users LIMIT 50")
        rows = cursor.fetchall()
        if not rows:
            print('NO_USERS')
        else:
            for r in rows:
                print(r)
    except Exception as e:
        print('QUERY_ERROR:', e)
    finally:
        conn.close()
