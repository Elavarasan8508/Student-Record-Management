from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for session management

# MySQL configuration
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  
        database="student_db"
    )
    return conn

@app.route('/')
def index():
    search_query = request.args.get('search', '')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if search_query:
        cursor.execute("""
            SELECT * FROM students 
            WHERE name LIKE %s OR roll_no LIKE %s OR department LIKE %s
            ORDER BY name
        """, (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
    else:
        cursor.execute("SELECT * FROM students ORDER BY name")
    
    students = cursor.fetchall()
    conn.close()
    
    return render_template('index.html', students=students, search_query=search_query)

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        roll_no = request.form['roll_no']
        department = request.form['department']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO students (name, roll_no, department) VALUES (%s, %s, %s)", 
                (name, roll_no, department)
            )
            conn.commit()
            flash('Student added successfully!', 'success')
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            conn.close()
        
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        name = request.form['name']
        roll_no = request.form['roll_no']
        department = request.form['department']
        
        try:
            cursor.execute(
                "UPDATE students SET name=%s, roll_no=%s, department=%s WHERE id=%s", 
                (name, roll_no, department, id)
            )
            conn.commit()
            flash('Student updated successfully!', 'success')
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            conn.close()
        
        return redirect(url_for('index'))
    
    cursor.execute("SELECT * FROM students WHERE id=%s", (id,))
    student = cursor.fetchone()
    conn.close()
    
    if not student:
        flash('Student not found!', 'danger')
        return redirect(url_for('index'))
    
    return render_template('edit.html', student=student)

@app.route('/delete/<int:id>')
def delete_student(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM students WHERE id=%s", (id,))
        conn.commit()
        flash('Student deleted successfully!', 'success')
    except mysql.connector.Error as err:
        flash(f'Error: {err}', 'danger')
    finally:
        conn.close()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)