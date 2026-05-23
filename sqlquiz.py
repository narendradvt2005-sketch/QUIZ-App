import sqlite3
import random
import os

# DATABASE CONNECTION
DB_NAME = "quiz1.db"
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

print(f"DEBUG: Current Working Directory: {os.getcwd()}")
print(f"DEBUG: Database Path: {os.path.abspath(DB_NAME)}")

# CREATE QUESTIONS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS questions(
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    option1 TEXT,
    option2 TEXT,
    option3 TEXT,
    option4 TEXT,
    correct_answer TEXT
)
""")

# CREATE SCORE TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS quiz_scores(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    total_questions INTEGER,
    score INTEGER,
    percentage INTEGER
)
""")

conn.commit()

# CHECK IF QUESTIONS TABLE IS EMPTY
cursor.execute("SELECT * FROM questions")
data = cursor.fetchall()

# INSERT DEFAULT QUESTIONS ONLY ONCE
if len(data) == 0:

    default_questions = [

        ("How many elements are in the periodic table?",
         "116", "117", "118", "119", "C"),

        ("Which animal lays the largest eggs?",
         "Whale", "Crocodile", "Elephant", "Ostrich", "D"),

        ("What is the most abundant gas in Earth's atmosphere?",
         "Nitrogen", "Oxygen", "Carbon-Dioxide", "Hydrogen", "A"),

        ("How many bones are in the human body?",
         "206", "207", "208", "209", "A"),

        ("Which planet in the solar system is the hottest?",
         "Mercury", "Venus", "Earth", "Mars", "B")

    ]

    for q in default_questions:

        cursor.execute("""
        INSERT INTO questions
        (question, option1, option2, option3, option4, correct_answer)
        VALUES (?, ?, ?, ?, ?, ?)
        """, q)

    conn.commit()

# Print questions count
cursor.execute("SELECT COUNT(*) FROM questions")
count = cursor.fetchone()[0]
print(f"DEBUG: Loaded {count} questions from database.")

# MAIN MENU
while True:

    print("\n========== QUIZ MANAGEMENT SYSTEM ==========")
    print("1. Add Question")
    print("2. View Questions")
    print("3. Start Quiz")
    print("4. View Leaderboard")
    print("5. Delete Question")
    print("6. Exit")

    choice = input("Enter your choice: ")

    # ADD QUESTION
    if choice == "1":

        question = input("Enter question: ")

        option1 = input("Enter option 1: ")
        option2 = input("Enter option 2: ")
        option3 = input("Enter option 3: ")
        option4 = input("Enter option 4: ")

        correct_answer = input("Enter correct answer (A/B/C/D): ").upper()

        cursor.execute("""
        INSERT INTO questions
        (question, option1, option2, option3, option4, correct_answer)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (question, option1, option2, option3, option4, correct_answer))

        conn.commit()

        print("Question added successfully!")

    # VIEW QUESTIONS
    elif choice == "2":

        cursor.execute("SELECT * FROM questions")

        records = cursor.fetchall()

        print("\n========== QUESTIONS ==========")

        for row in records:

            print("\nQuestion ID:", row[0])
            print("Question:", row[1])

            print("A.", row[2])
            print("B.", row[3])
            print("C.", row[4])
            print("D.", row[5])

            print("Correct Answer:", row[6])

    # START QUIZ
    elif choice == "3":

        name = input("Enter your name: ")

        cursor.execute("SELECT * FROM questions")

        records = cursor.fetchall()

        if len(records) == 0:
            print("No questions found!")
            continue

        try:
            num_questions = int(input(f"How many questions do you want? (1-{len(records)}): "))
        except ValueError:
            print("Enter valid number!")
            continue

        if num_questions < 1 or num_questions > len(records):
            print("Invalid number!")
            continue

        selected_questions = random.sample(records, num_questions)

        score = 0

        for q in selected_questions:

            print("\n----------------------")

            print(q[1])

            print("A.", q[2])
            print("B.", q[3])
            print("C.", q[4])
            print("D.", q[5])

            guess = input("Enter answer (A/B/C/D): ").upper()

            if guess == q[6]:
                print("CORRECT!")
                score += 1
            else:
                print("INCORRECT!")
                print("Correct answer is:", q[6])

        percentage = int((score / num_questions) * 100)

        print("\n========== RESULT ==========")

        print("Score:", score)
        print("Percentage:", percentage, "%")

        # SAVE SCORE
        cursor.execute("""
        INSERT INTO quiz_scores(name, total_questions, score, percentage)
        VALUES (?, ?, ?, ?)
        """, (name, num_questions, score, percentage))

        conn.commit()

        print("Score saved successfully!")

    # VIEW LEADERBOARD
    elif choice == "4":

        cursor.execute("""
        SELECT name, percentage
        FROM quiz_scores
        ORDER BY percentage DESC
        LIMIT 5
        """)

        records = cursor.fetchall()

        print("\n========== LEADERBOARD ==========")

        for row in records:
            print(row[0], "-", row[1], "%")

    # DELETE QUESTION
    elif choice == "5":

        cursor.execute("SELECT question_id, question FROM questions")

        records = cursor.fetchall()

        print("\n========== AVAILABLE QUESTIONS ==========")

        for row in records:
            print(row[0], "-", row[1])

        try:
            question_id = int(input("\nEnter Question ID to delete: "))
        except ValueError:
            print("Enter valid ID!")
            continue

        cursor.execute("""
        DELETE FROM questions
        WHERE question_id = ?
        """, (question_id,))

        # REORDER IDs
        cursor.execute("SELECT question_id FROM questions ORDER BY question_id")
        remaining_questions = cursor.fetchall()
        for new_id, row in enumerate(remaining_questions, start=1):
            old_id = row[0]
            if old_id != new_id:
                cursor.execute("UPDATE questions SET question_id = ? WHERE question_id = ?", (new_id, old_id))
        
        # RESET AUTOINCREMENT
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='questions'")

        conn.commit()

        print("Question deleted successfully!")

    # EXIT
    elif choice == "6":

        print("Exiting program...")
        break

    else:
        print("Invalid choice!")

# CLOSE DATABASE
conn.close()