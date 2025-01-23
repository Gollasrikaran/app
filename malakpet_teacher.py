import streamlit as st
from database import create_connection, load_data
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def malakpet_teacher_dashboard():
    st.title("Malakpet Teacher Dashboard")

    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["Evaluation"])

    if page == "Evaluation":
        st.header("Evaluate Students")

        # Fetch Malakpet Branch ID
        conn = create_connection("school.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM Schools WHERE branch_name = ?", ("Malakpet",))
        branch_result = cursor.fetchone()

        if branch_result:
            branch_id = branch_result[0]
        else:
            st.error("Error fetching branch ID")
            return

        # Fetch Subjects for Malakpet
        subjects_df = load_data(f"SELECT id, name FROM Subjects WHERE branch_id = {branch_id}")

        if subjects_df.empty:
            st.warning("No subjects available for Malakpet. Please add subjects using branch admin.")
        else:
            selected_subject = st.selectbox("Select Subject", options=subjects_df["name"].tolist())

            # Get the ID of the selected subject
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM Subjects WHERE name = ? AND branch_id = ?", (selected_subject, branch_id))
            subject_result = cursor.fetchone()
            if subject_result:
                selected_subject_id = subject_result[0]
            else:
                st.error("Error fetching Subject ID")
                return

            # Fetch Chapters for the selected subject
            chapters_query = f"""
                SELECT id, name FROM Chapters WHERE subject_id = {selected_subject_id}
            """
            chapters_df = load_data(chapters_query)

            if chapters_df.empty:
               st.warning(f"No Chapters available for subject '{selected_subject}'. Please add chapters using branch admin.")
            else:
                # Prepare Data for Evaluation
                evaluation_data = []
                for chapter_index, chapter_row in chapters_df.iterrows():
                    chapter_id = chapter_row['id']
                    chapter_name = chapter_row['name']
                    
                    # Fetch Topics for this chapter
                    topics_query = f"""
                        SELECT id, name FROM Topics WHERE chapter_id = {chapter_id}
                    """
                    topics_df = load_data(topics_query)
                    
                    if not topics_df.empty:
                       for topic_index, topic_row in topics_df.iterrows():
                            topic_id = topic_row['id']
                            topic_name = topic_row['name']
                            
                            # Fetch Students for the current branch,class and class id
                            students_query = f"""
                                SELECT s.student_name, c.class, c.section,c.id as class_id
                                FROM Students s
                                JOIN Classes c ON s.class_id = c.id
                                WHERE c.branch_id = {branch_id}
                            """
                            students_df = load_data(students_query)
                            
                            if not students_df.empty:
                                for student_index, student_row in students_df.iterrows():
                                    student_name = student_row['student_name']
                                    class_no = student_row['class']
                                    section = student_row['section']
                                    class_id = student_row['class_id']
                                    evaluation_data.append({
                                        "Student Name": student_name,
                                        "Class": class_no,
                                        "Section": section,
                                        "Chapter": chapter_name,
                                        "Topic": topic_name,
                                        "Evaluation": "Not Completed",  # Set default value
                                    })
                            else:
                                st.warning(f"No students available for this branch, Please add students in the branch admin page.")
                    else:
                        st.warning(f"No topics available for chapter '{chapter_name}'. Please add topics using branch admin.")
                if evaluation_data:
                    df = pd.DataFrame(evaluation_data)
                    
                    # Create an editable column in the dataframe for Evaluation
                    edited_df = st.data_editor(df,
                    column_config={
                        "Evaluation": st.column_config.SelectboxColumn(
                            "Evaluation",
                            options=["Completed", "Not Completed"],
                            default = "Not Completed",
                            width="medium",
                        )
                       },
                       key="evaluation_editor"
                    )
                    
                    # Pie Chart Data
                    completed_count = edited_df["Evaluation"].value_counts().get("Completed", 0)
                    not_completed_count = edited_df["Evaluation"].value_counts().get("Not Completed", 0)
                    
                    # Pie chart
                    fig_pie = go.Figure(data=[go.Pie(labels=['Completed', 'Not Completed'],
                                     values=[completed_count, not_completed_count],
                                     hole = .3
                                    )])
                    st.plotly_chart(fig_pie, use_container_width=True)
                    
                    # Bar chart data
                    class_counts = edited_df.groupby('Class')['Evaluation'].value_counts(normalize=True).unstack(fill_value=0)
                   
                    # Bar chart
                    fig_bar = px.bar(class_counts*100, 
                                    title='Class-wise Topic Completion Rate',
                                    labels={'value':'Completion Rate (%)', 'index':'Class'},
                                    barmode = 'group')
                    st.plotly_chart(fig_bar, use_container_width=True)

                    # Table for completed students count per chapter
                    chapter_counts = edited_df.groupby(["Chapter", "Evaluation"])["Student Name"].count().unstack(fill_value=0)
                    st.subheader("Student Completion Status per Chapter")
                    st.dataframe(chapter_counts)

                else:
                    st.warning(f"No evaluation data to display.")
        conn.close()