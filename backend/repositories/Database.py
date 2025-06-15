from mysql import connector
import os

class Database:
    @staticmethod
    def __open_connection():
        try:
            db = connector.connect(
                option_files=os.path.abspath(
                    os.path.join(os.path.dirname(__file__), "../config.py")  
                ),
                autocommit=False,
            )
            if "AttributeError" in (str(type(db))):
                raise Exception("Foutieve database parameters in config")
            cursor = db.cursor(dictionary=True, buffered=True)  
            return db, cursor
        except connector.Error as err:
            if err.errno == connector.errorcode.ER_ACCESS_DENIED_ERROR:
                print("Error: Er is geen toegang tot de database (username/password fout)")
            elif err.errno == connector.errorcode.ER_BAD_DB_ERROR:
                print("Error: De database is niet gevonden")
            else:
                print(f"Database connectie error: {err}")
            return None, None

    @staticmethod
    def get_rows(sqlQuery, params=None):
        result = []
        db, cursor = Database.__open_connection()
        if not db or not cursor:
            print("Error: Geen database connectie mogelijk")
            return None
        try:
            cursor.execute(sqlQuery, params)
            result = cursor.fetchall()
        except connector.Error as error:
            print(f"SQL Error in get_rows: {error}")
            result = None
        except Exception as error:
            print(f"Onverwachte fout in get_rows: {error}")
            result = None
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()
            return result

    @staticmethod
    def get_one_row(sqlQuery, params=None):
        result = None
        db, cursor = Database.__open_connection()
        if not db or not cursor:
            print("Error: Geen database connectie mogelijk")
            return None
        try:
            cursor.execute(sqlQuery, params)
            result = cursor.fetchone()
        except connector.Error as error:
            print(f"SQL Error in get_one_row: {error}")
            result = None
        except Exception as error:
            print(f"Onverwachte fout in get_one_row: {error}")
            result = None
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()
            return result

    @staticmethod
    def execute_sql(sqlQuery, params=None):
        result = None
        db, cursor = Database.__open_connection()
        if not db or not cursor:
            print("Error: Geen database connectie mogelijk")
            return None
        try:
            cursor.execute(sqlQuery, params)
            db.commit()
            if cursor.lastrowid > 0:
                result = cursor.lastrowid
            else:
                result = cursor.rowcount
        except connector.Error as error:
            print(f"SQL Error in execute_sql: {error}")
            if db:
                db.rollback()
            result = None
        except Exception as error:
            print(f"Onverwachte fout in execute_sql: {error}")
            if db:
                db.rollback()
            result = None
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()
            return result

    @staticmethod
    def test_connection():
        db, cursor = Database.__open_connection()
        if db and cursor:
            try:
                cursor.execute("SELECT 1 as test")
                _ = cursor.fetchone()
                print("Database connectie werkt!")
                return True
            except Exception as e:
                print(f"Database test mislukt: {e}")
                return False
            finally:
                cursor.close()
                db.close()
        else:
            print("Database connectie mislukt")
            return False

    @staticmethod
    def setup_database():
        db, cursor = Database.__open_connection()
        if not db or not cursor:
            print("Kan geen verbinding maken voor database setup")
            return False
        try:
            cursor.execute(
                "CREATE DATABASE IF NOT EXISTS GlasGoDb CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci"
            )
            print("Database 'GlasGoDb' bestaat of is aangemaakt")
            return True
        except connector.Error as error:
            print(f"SQL Error in setup_database: {error}")
            return False
        except Exception as error:
            print(f"Onverwachte fout in setup_database: {error}")
            return False
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    

if __name__ == "__main__":
    print("=== Database Test ===")
    if Database.test_connection():
        print("Database connectie werkt!")
    else:
        print("Probeer database setup...")
        if Database.setup_database():
            print("Database setup voltooid, test connectie opnieuw...")
            Database.test_connection()
