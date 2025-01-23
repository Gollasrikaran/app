import streamlit as st
import pandas as pd
from database import create_connection, load_data

def bulk_upload_component(branch_name):
    st.header("Bulk Upload Data")
    st.write("Please upload the CSV file")
    st.write(f"Required columns: Student Name, Class, Section, Chapter, Topic, Subject")

    uploaded_file = st.file_uploader("Browse Files", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)

            # Validate that the CSV file has the required columns.
            required_columns = ["Student Name", "Class", "Section", "Chapter", "Topic", "Subject"]
            if not all(col in df.columns for col in required_columns):
               st.error(f"CSV file must contain the following columns: {', '.join(required_columns)}")
               return

            if st.button("Upload Data"):
               upload_data(df,branch_name)
        except Exception as e:
             st.error(f"Error reading CSV file: {e}")

def upload_data(df,branch_name):
    conn = create_connection("school.db")
    cursor = conn.cursor()
    try:
       for index, row in df.iterrows():
           student_name = row["Student Name"]
           class_no = row["Class"]
           section = row["Section"]
           chapter_name = row["Chapter"]
           topic_name = row["Topic"]
           subject_name = row["Subject"]

           # Fetch branch ID
           cursor.execute("SELECT id FROM Schools WHERE branch_name = ?", (branch_name,))
           branch_result = cursor.fetchone()

           if branch_result:
               branch_id = branch_result[0]
           else:
                st.error(f"Error fetching Branch ID for branch name '{branch_name}'.")
                return

           # Fetch Subject ID
           cursor.execute("SELECT id FROM Subjects WHERE name = ? AND branch_id = ?", (subject_name, branch_id))
           subject_result = cursor.fetchone()

           if subject_result:
                subject_id = subject_result[0]
           else:
                 # Insert if subject does not exist
                cursor.execute("INSERT INTO Subjects (name, branch_id) VALUES (?, ?)", (subject_name, branch_id))
                conn.commit()
                # Fetch the subject id after the insertion
                cursor.execute("SELECT id FROM Subjects WHERE name = ? AND branch_id = ?", (subject_name, branch_id))
                subject_result = cursor.fetchone()
                if subject_result:
                     subject_id = subject_result[0]
                else:
                     st.error(f"Error fetching subject ID for '{subject_name}' in branch '{branch_name}'. Please add the subject in the branch admin page.")
                     return
           
           # Fetch chapter ID
           cursor.execute("SELECT id FROM Chapters WHERE name = ? AND subject_id = ?", (chapter_name, subject_id))
           chapter_result = cursor.fetchone()

           if chapter_result:
                chapter_id = chapter_result[0]
           else:
                 # Insert if chapter does not exist
                 cursor.execute("INSERT INTO Chapters (name, subject_id) VALUES (?, ?)", (chapter_name, subject_id))
                 conn.commit()
                # Fetch the chapter id after the insertion
                 cursor.execute("SELECT id FROM Chapters WHERE name = ? AND subject_id = ?", (chapter_name, subject_id))
                 chapter_result = cursor.fetchone()
                 if chapter_result:
                     chapter_id = chapter_result[0]
                 else:
                     st.error(f"Error fetching chapter ID for '{chapter_name}' in subject '{subject_name}'. Please add the chapter in the branch admin page")
                     return

           # Fetch Topic Id
           cursor.execute("SELECT id FROM Topics WHERE name = ? AND chapter_id = ?", (topic_name, chapter_id))
           topic_result = cursor.fetchone()

           if topic_result:
               topic_id = topic_result[0]
           else:
                 # Insert if topic does not exist
                cursor.execute("INSERT INTO Topics (name, chapter_id) VALUES (?, ?)", (topic_name, chapter_id))
                conn.commit()
                # Fetch the topic id after insertion
                cursor.execute("SELECT id FROM Topics WHERE name = ? AND chapter_id = ?", (topic_name, chapter_id))
                topic_result = cursor.fetchone()
                if topic_result:
                     topic_id = topic_result[0]
                else:
                    st.error(f"Error fetching topic ID for '{topic_name}' in chapter '{chapter_name}'. Please add the topic in the branch admin page")
                    return
           
           # Fetch class ID
           cursor.execute("SELECT id FROM Classes WHERE class = ? AND section = ? AND branch_id = ?", (class_no,section,branch_id))
           class_result = cursor.fetchone()
           
           if class_result:
               class_id = class_result[0]
           else:
                st.error(f"Error fetching Class ID for '{class_no}-{section}' in branch '{branch_name}'. Please add the class in branch admin page")
                return

           # Check if student already exists
           cursor.execute("SELECT id FROM Students WHERE student_name = ? AND class_id = ?", (student_name, class_id))
           student_result = cursor.fetchone()

           if not student_result:
               # If student doesn't exist, insert them
               cursor.execute("INSERT INTO Students (student_name, class_id) VALUES (?, ?)", (student_name, class_id))
               conn.commit()

       conn.commit()
       st.success("Data uploaded successfully")
    except Exception as e:
        conn.rollback()
        st.error(f"Error uploading data: {e}")
    finally:
        conn.close()