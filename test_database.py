import sqlite3
import os
import sys

def get_connection():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Base de données introuvable : {DB_PATH}")
    return sqlite3.connect(DB_PATH)

def display_results(test_name, succes, detail=""):
    status = "SUCCES" if succes else "ECHEC"
    print(f"{test_name} : {status}. {detail}")

# ======================================
# Test d'intégrité de la base de données
# ======================================

def test_quick_check():
    """
    Vérifie rapidement la structure interne de la base de données.

    :return: True si la vérification est réussie, False sinon
    :rtype: bool
    """
    con = get_connection()
    cur = con.cursor()
    cur.execute("PRAGMA quick_check;")
    results = cur.fetchall()
    con.close()

    succes = results == [("ok",)]
    detail = "" if succes else f"{len(results)} problème(s) détecté(s) : {results[:10]}"
    display_results("PRAGMA quick_check", succes, detail)
    return succes

def integrity_check():
    """
    Vérifie en profondeur la structure interne de la base de données.

    :return: True si la vérification est réussie, False sinon
    :rtype: bool
    """
    con = get_connection()
    cur = con.cursor()
    cur.execute("PRAGMA integrity_check;")
    resultats = cur.fetchall()
    con.close()

    succes = resultats == [("ok",)]
    detail = "" if succes else f"{len(resultats)} problème(s) : {resultats[:10]}"
    display_results("PRAGMA integrity_check", succes, detail)
    return succes

def test_foreign_keys():
    """ 
    Vérifie l'intégrité des clés étrangères de la base de données.

    :return: True si la vérification est réussie, False sinon
    :rtype: bool
    """
    con = get_connection()
    cur = con.cursor()
    
    # Active la vérification des clés étrangères
    cur.execute("PRAGMA foreign_keys = ON;")
    
    # Vérifie les violations de clés étrangères
    cur.execute("PRAGMA foreign_key_check;")
    resultats = cur.fetchall()
    con.close()
    
    succes = len(resultats) == 0
    detail = "" if succes else f"{len(resultats)} violation(s) détectée(s) : {resultats[:10]}"
    display_results("PRAGMA foreign_key_check", succes, detail)
    return succes

# ======================================
# Point d'entrée du script
# ======================================

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage : python tests_database.py <chemin_base.db>")
        sys.exit(1)

    DB_PATH = sys.argv[1]
    test_quick_check()
    integrity_check()
    test_foreign_keys()