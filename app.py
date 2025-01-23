import streamlit as st
from database import create_connection, get_classes, add_student, load_data
import pandas as pd
from malakpet_teacher import malakpet_teacher_dashboard
from dilshuknagar_teacher import dilshuknagar_teacher_dashboard  # Import teacher dashboards
from bulk_upload import bulk_upload_component

def authenticate_user(username, password):
    conn = create_connection("school.db")
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        return user

def superadmin_dashboard():
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["Schools", "Branches", "Teachers", "Classes"])

    if page == "Schools":
        st.header("Manage Schools")
        # Add School Form
        with st.form("add_school_form"):
            school_name = st.text_input("School Name")
            address = st.text_input("Address")
            branch_name = st.text_input("Branch Name")
            submitted = st.form_submit_button("Add School")

            if submitted and school_name and branch_name:
                conn = create_connection("school.db")
                try:
                    with conn:
                        conn.execute("""
                            INSERT INTO Schools (name, address, branch_name) 
                            VALUES (?, ?, ?)
                        """, (school_name, address, branch_name))
                    st.success("School and Branch information added successfully!")
                except Exception as e:
                    st.error(f"Error adding school: {e}")

        # Update School ID
        with st.form("update_school_id_form"):
            current_branch_name = st.text_input("Branch Name to Update ID")
            new_id = st.text_input("New ID")
            update_submitted = st.form_submit_button("Update School ID")

            if update_submitted and current_branch_name and new_id:
                conn = create_connection("school.db")
                try:
                    with conn:
                        conn.execute("""
                            UPDATE Schools 
                            SET id = ? 
                            WHERE branch_name = ?
                        """, (new_id, current_branch_name))
                        st.success("School ID updated successfully!")
                except Exception as e:
                    st.error(f"Error updating school ID: {e}")

        # Update School Address
        with st.form("update_school_address_form"):
            current_branch_name = st.text_input("Branch Name to Update Address")
            new_address = st.text_input("New Address")
            update_address_submitted = st.form_submit_button("Update School Address")

            if update_address_submitted and current_branch_name and new_address:
                conn = create_connection("school.db")
                try:
                    with conn:
                        conn.execute("""
                            UPDATE Schools 
                            SET address = ? 
                            WHERE branch_name = ?
                        """, (new_address, current_branch_name))
                        st.success("School address updated successfully!")
                except Exception as e:
                    st.error(f"Error updating school address: {e}")

        # Delete School by Branch Name
        with st.form("delete_school_form"):
            branch_name_to_delete = st.text_input("Branch Name to Delete")
            delete_submitted = st.form_submit_button("Delete School by Branch Name")

            if delete_submitted and branch_name_to_delete:
                conn = create_connection("school.db")
                try:
                    with conn:
                        conn.execute("DELETE FROM Schools WHERE branch_name = ?", (branch_name_to_delete,))
                    st.success(f"School with Branch Name '{branch_name_to_delete}' deleted successfully!")
                except Exception as e:
                    st.error(f"Error deleting school: {e}")

        # Display existing schools
        schools_df = load_data("SELECT * FROM Schools")
        if not schools_df.empty:
            st.subheader("Existing Schools")
            st.dataframe(schools_df)

    elif page == "Branches":
        st.header("Manage Branches")

        branches_df = load_data("SELECT id, name, address, branch_name FROM Schools")
        if not branches_df.empty:
            st.subheader("Existing Branches")
            st.dataframe(branches_df)

            # Update Branch Name
            with st.form("update_branch_form"):
                branch_id = st.selectbox("Select School to Update Branch", options=branches_df['id'].tolist(),
                                        format_func=lambda x: branches_df[branches_df['id'] == x]['name'].iloc[0])
                new_branch_name = st.text_input("New Branch Name")
                submitted = st.form_submit_button("Update Branch Name")

                if submitted and new_branch_name:
                    conn = create_connection("school.db")
                    try:
                        with conn:
                            conn.execute("""
                                UPDATE Schools 
                                SET branch_name = ? 
                                WHERE id = ?
                            """, (new_branch_name, branch_id))
                        st.success("Branch name updated successfully!")
                    except Exception as e:
                        st.error(f"Error updating branch name: {e}")

            # Delete Branch
            with st.form("delete_branch_form"):
                branch_name_to_delete = st.text_input("Branch Name to Delete")
                delete_submitted = st.form_submit_button("Delete Branch by Branch Name")

                if delete_submitted and branch_name_to_delete:
                    conn = create_connection("school.db")
                    try:
                        with conn:
                            conn.execute("DELETE FROM Schools WHERE branch_name = ?", (branch_name_to_delete,))
                        st.success(f"Branch with Branch Name '{branch_name_to_delete}' deleted successfully!")
                    except Exception as e:
                        st.error(f"Error deleting branch: {e}")
        else:
            st.warning("No schools available. Please add schools first.")

    elif page == "Teachers":
        st.header("Manage Teachers")

        # Create Teachers table if it doesn't exist
        conn = create_connection("school.db")
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS Teachers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    teacher_name TEXT NOT NULL,
                    school_name TEXT NOT NULL,
                    branch_name TEXT NOT NULL,
                    subject TEXT NOT NULL
                )
            """)

        # Add Teacher Form
        with st.form("add_teacher_form"):
            teacher_name = st.text_input("Teacher Name")
            school_name = st.text_input("School Name")
            branch_name = st.text_input("Branch Name")
            subject = st.text_input("Subject")
            submitted = st.form_submit_button("Add Teacher")

            if submitted and teacher_name and school_name and branch_name and subject:
                try:
                    with conn:
                        conn.execute("""
                            INSERT INTO Teachers (teacher_name, school_name, branch_name, subject)
                            VALUES (?, ?, ?, ?)
                        """, (teacher_name, school_name, branch_name, subject))
                    st.success(f"Teacher '{teacher_name}' added successfully!")
                except Exception as e:
                    st.error(f"Error adding teacher: {e}")

        # Delete Teacher by Name
        with st.form("delete_teacher_form"):
            teacher_name_to_delete = st.text_input("Teacher Name to Delete")
            delete_teacher_submitted = st.form_submit_button("Delete Teacher")

            if delete_teacher_submitted and teacher_name_to_delete:
                try:
                    with conn:
                        conn.execute("DELETE FROM Teachers WHERE teacher_name = ?", (teacher_name_to_delete,))
                    st.success(f"Teacher '{teacher_name_to_delete}' deleted successfully!")
                except Exception as e:
                    st.error(f"Error deleting teacher: {e}")

        # Display existing teachers
        teachers_df = load_data("SELECT * FROM Teachers")
        if not teachers_df.empty:
            st.subheader("Existing Teachers")
            st.dataframe(teachers_df)
        else:
            st.warning("No teachers available. Please add teachers.")

    elif page == "Classes":
        st.header("Manage Classes")

        # Form for adding classes
        with st.form("add_class_form"):
            school_name = st.text_input("School Name")
            branch_name = st.text_input("Branch Name")
            class_no = st.number_input("Class Number", min_value=1, max_value=12, step=1)
            section = st.text_input("Section")
            no_of_students = st.number_input("Number of Students", min_value=0, step=1)
            submitted = st.form_submit_button("Add Class")

            if submitted and school_name and branch_name and class_no and section and no_of_students:
                conn = create_connection("school.db")
                try:
                    with conn:
                        # Fetch the branch_id based on school_name and branch_name
                        cursor = conn.cursor()
                        cursor.execute("SELECT id FROM Schools WHERE name = ? AND branch_name = ?",
                                    (school_name, branch_name))
                        result = cursor.fetchone()
                        if result:
                            branch_id = result[0]
                            # Check if class already exists
                            cursor.execute("SELECT * FROM Classes WHERE branch_id = ? AND class = ? AND section = ?",
                                            (branch_id, class_no, section))
                            existing_class = cursor.fetchone()
                            if existing_class:
                                st.error(f"Class {class_no}-{section} already exists for branch '{branch_name}'.")
                            else:
                                conn.execute("""
                                    INSERT INTO Classes (branch_id, class, section, no_of_students)
                                    VALUES (?, ?, ?, ?)
                                """, (branch_id, class_no, section, no_of_students))
                                st.success(f"Class {class_no}-{section} added for branch '{branch_name}' successfully!")
                        else:
                            st.error("School or branch not found. Please check the school and branch names.")
                except Exception as e:
                    st.error(f"Error adding class: {e}")

        # Form to update class
        classes_df = load_data("SELECT id, class, section, branch_id, no_of_students FROM Classes")
        with st.form("update_class_form"):
            if not classes_df.empty:
                class_id = st.selectbox("Select class to update", options=classes_df['id'].tolist(),
                                        format_func=lambda x: f"Class {classes_df[classes_df['id'] == x]['class'].iloc[0]}-{classes_df[classes_df['id'] == x]['section'].iloc[0]}")
                new_class_no = st.number_input("New Class Number", min_value=1, max_value=12, step=1)
                new_section = st.text_input("New Section")
                new_no_of_students = st.number_input("Number of Students", min_value=0, step=1)
                update_submitted = st.form_submit_button("Update Class")

                if update_submitted and new_class_no and new_section and new_no_of_students:
                    conn = create_connection("school.db")
                    try:
                        with conn:
                            conn.execute("""
                                UPDATE Classes
                                SET class = ?, section = ?, no_of_students = ?
                                WHERE id = ?
                            """, (new_class_no, new_section, new_no_of_students, class_id))
                            st.success(f"Class updated to {new_class_no}-{new_section} successfully!")
                    except Exception as e:
                        st.error(f"Error updating class: {e}")
            else:
                st.warning("No classes available. Please add classes first.")

        # Form to delete class
        with st.form("delete_class_form"):
            if not classes_df.empty:
                class_no_to_delete = st.number_input("Class Number to Delete", min_value=1, max_value=12, step=1)
                section_to_delete = st.text_input("Section to Delete")
                delete_submitted = st.form_submit_button("Delete Class")

                if delete_submitted and class_no_to_delete and section_to_delete:
                    conn = create_connection("school.db")
                    try:
                        with conn:
                            # Delete class based on class and section
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM Classes WHERE class = ? AND section = ?",
                                            (class_no_to_delete, section_to_delete))
                            if cursor.rowcount > 0 :
                                st.success(f"Class {class_no_to_delete}-{section_to_delete} deleted successfully!")
                            else:
                                st.error(f"Class {class_no_to_delete}-{section_to_delete} not found, please check the class and section")
                    except Exception as e:
                        st.error(f"Error deleting class: {e}")
            else:
                st.warning("No classes available. Please add classes first.")

        # Display Existing Classes
        classes_df = load_data("SELECT c.id, s.name as school_name, s.branch_name, c.class, c.section, c.no_of_students FROM Classes c JOIN Schools s ON c.branch_id = s.id")
        if not classes_df.empty:
            st.subheader("Existing Classes")
            st.dataframe(classes_df)
        else:
            st.warning("No classes available. Please add classes.")


def branchadmin_dashboard():
    st.title("Branch Admin Dashboard")

    # Get the logged-in user's information
    user = st.session_state.user
    branch_id = user[4]  # Assuming branch_id is the 5th column in Users table

    if "branch_name_selected" not in st.session_state:
        st.session_state.branch_name_selected = None

    if not st.session_state.branch_name_selected:

        st.header(f"Welcome Branch Admin")

        with st.form("branch_login_form"):
            selected_branch_name = st.text_input("Branch Name")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

            if submitted and selected_branch_name and password:

                # validate if the branch name and password is correct from the schools table

                branch_auth_query = f"""
                   SELECT * FROM Schools WHERE branch_name = '{selected_branch_name}'
                """
                branch_auth_details = load_data(branch_auth_query)

                if not branch_auth_details.empty:

                    if (selected_branch_name == "Malakpet" and password == "admin" or selected_branch_name == "Dilshuknagar" and password == "admin"):
                        st.session_state.branch_name_selected = selected_branch_name
                        st.success(f"Logged in to branch: {selected_branch_name}")
                    else:
                        st.error("Invalid branch name or password")
                else:
                    st.error("Invalid branch name or password")

        return
    else:
        selected_branch_name = st.session_state.branch_name_selected
        # Fetch branch details from the schools table

        st.sidebar.title("Navigation")
        page = st.sidebar.selectbox("Choose a page", ["Overview", "Classes", "Teachers", "Subjects","Students", "Bulk Upload"])  #Add "Students" here

        if page == "Overview":
            # Fetch branch details from the schools table
            branch_details_query = f"""
            SELECT s.name AS school_name, s.address, s.branch_name 
            FROM Schools s
            WHERE s.branch_name = '{selected_branch_name}'
            """
            branch_details = load_data(branch_details_query)

            if not branch_details.empty:
                school_name = branch_details['school_name'].iloc[0]
                branch_name = branch_details['branch_name'].iloc[0]
                branch_address = branch_details['address'].iloc[0]

                st.header(f"Welcome {branch_name} Admin")
                st.subheader(f"School Name : {school_name}")
                st.subheader(f"Branch Name : {branch_name}")
                st.subheader(f"Branch Address : {branch_address}")

                # Calculate and display total classes
                classes_count_query = f"""
                SELECT COUNT(*) AS total_classes FROM Classes WHERE branch_id = (SELECT id from Schools WHERE branch_name = '{selected_branch_name}')
                """
                classes_count_df = load_data(classes_count_query)
                total_classes = classes_count_df['total_classes'].iloc[0] if not classes_count_df.empty else 0
                st.subheader(f"Total Classes: {total_classes}")

                # Calculate and display total teachers
                teachers_count_query = f"""
                    SELECT COUNT(*) AS total_teachers FROM Teachers WHERE branch_name = '{selected_branch_name}'
                """
                teachers_count_df = load_data(teachers_count_query)
                total_teachers = teachers_count_df['total_teachers'].iloc[0] if not teachers_count_df.empty else 0
                st.subheader(f"Total Teachers : {total_teachers}")
            else:
                st.error("Branch details not found. Contact SuperAdmin.")
                return
            st.header("Overview")
            st.write("This is the overview page for the branch admin")

        elif page == "Classes":
            st.header("Manage Classes")
            # Form for adding classes
            with st.form("add_class_form_branch"):
                class_no = st.number_input("Class Number", min_value=1, max_value=12, step=1)
                section = st.text_input("Section")
                no_of_students = st.number_input("Number of Students", min_value=0, step=1)
                submitted = st.form_submit_button("Add Class")

                if submitted and class_no and section and no_of_students:
                    conn = create_connection("school.db")
                    try:
                        with conn:
                            # Fetch the branch_id based on school_name and branch_name
                            cursor = conn.cursor()
                            cursor.execute("SELECT id FROM Schools WHERE branch_name = ?",
                                            (selected_branch_name,))
                            result = cursor.fetchone()
                            if result:
                                branch_id = result[0]
                            # Check if class already exists

                            cursor.execute("SELECT * FROM Classes WHERE branch_id = ? AND class = ? AND section = ?",
                                            (branch_id, class_no, section))
                            existing_class = cursor.fetchone()
                            if existing_class:
                                st.error(f"Class {class_no}-{section} already exists for branch.")
                            else:
                                conn.execute("""
                                    INSERT INTO Classes (branch_id, class, section, no_of_students)
                                    VALUES (?, ?, ?, ?)
                                """, (branch_id, class_no, section, no_of_students))
                                st.success(f"Class {class_no}-{section} added successfully!")

                    except Exception as e:
                        st.error(f"Error adding class: {e}")
            # Form to update class
            classes_df = load_data(f"SELECT id, class, section, branch_id, no_of_students FROM Classes WHERE branch_id = (SELECT id from Schools WHERE branch_name = '{selected_branch_name}')")
            with st.form("update_class_form_branch"):
                if not classes_df.empty:
                    class_id = st.selectbox("Select class to update", options=classes_df['id'].tolist(),
                                            format_func=lambda x: f"Class {classes_df[classes_df['id'] == x]['class'].iloc[0]}-{classes_df[classes_df['id'] == x]['section'].iloc[0]}")
                    new_class_no = st.number_input("New Class Number", min_value=1, max_value=12, step=1)
                    new_section = st.text_input("New Section")
                    new_no_of_students = st.number_input("Number of Students", min_value=0, step=1)
                    update_submitted = st.form_submit_button("Update Class")

                    if update_submitted and new_class_no and new_section and new_no_of_students:
                        conn = create_connection("school.db")
                        try:
                            with conn:
                                conn.execute("""
                                    UPDATE Classes
                                    SET class = ?, section = ?, no_of_students = ?
                                    WHERE id = ?
                                """, (new_class_no, new_section, new_no_of_students, class_id))
                                st.success(f"Class updated to {new_class_no}-{new_section} successfully!")
                        except Exception as e:
                            st.error(f"Error updating class: {e}")
                else:
                    st.warning("No classes available. Please add classes first.")
            # Form to delete class
            with st.form("delete_class_form_branch"):
                if not classes_df.empty:
                    class_no_to_delete = st.number_input("Class Number to Delete", min_value=1, max_value=12, step=1)
                    section_to_delete = st.text_input("Section to Delete")
                    delete_submitted = st.form_submit_button("Delete Class")

                    if delete_submitted and class_no_to_delete and section_to_delete:
                        conn = create_connection("school.db")
                        try:
                            with conn:
                                # Delete class based on class and section
                                cursor = conn.cursor()
                                cursor.execute("DELETE FROM Classes WHERE class = ? AND section = ? AND branch_id = (SELECT id from Schools WHERE branch_name = ?)",
                                                (class_no_to_delete, section_to_delete, selected_branch_name))
                                if cursor.rowcount > 0:
                                    st.success(f"Class {class_no_to_delete}-{section_to_delete} deleted successfully!")
                                else:
                                    st.error(f"Class {class_no_to_delete}-{section_to_delete} not found, please check the class and section")
                        except Exception as e:
                            st.error(f"Error deleting class: {e}")
                else:
                    st.warning("No classes available. Please add classes first.")
            # Display Existing Classes
            classes_df = load_data(f"SELECT c.id, s.name as school_name, s.branch_name, c.class, c.section, c.no_of_students FROM Classes c JOIN Schools s ON c.branch_id = s.id WHERE c.branch_id = (SELECT id from Schools WHERE branch_name = '{selected_branch_name}')")
            if not classes_df.empty:
                st.subheader("Existing Classes")
                st.dataframe(classes_df)
            else:
                st.warning("No classes available. Please add classes.")

        elif page == "Teachers":
            st.header("Manage Teachers")
            # Add Teacher Form
            with st.form("add_teacher_form_branch"):
                teacher_name = st.text_input("Teacher Name")
                school_name = st.text_input("School Name")
                subject = st.text_input("Subject")
                submitted = st.form_submit_button("Add Teacher")

                if submitted and teacher_name and school_name and subject:
                    conn = create_connection("school.db")
                    try:
                        with conn:
                            conn.execute("""
                                INSERT INTO Teachers (teacher_name, school_name, branch_name, subject)
                                VALUES (?, ?, ?, ?)
                            """, (teacher_name, school_name, selected_branch_name, subject))
                            st.success(f"Teacher '{teacher_name}' added successfully!")
                    except Exception as e:
                        st.error(f"Error adding teacher: {e}")

            # Delete Teacher by Name
            with st.form("delete_teacher_form_branch"):
                teacher_name_to_delete = st.text_input("Teacher Name to Delete")
                delete_teacher_submitted = st.form_submit_button("Delete Teacher")

                if delete_teacher_submitted and teacher_name_to_delete:
                    conn = create_connection("school.db")
                    try:
                        with conn:
                            conn.execute("DELETE FROM Teachers WHERE teacher_name = ? AND branch_name = ?", (teacher_name_to_delete, selected_branch_name))
                            st.success(f"Teacher '{teacher_name_to_delete}' deleted successfully!")
                    except Exception as e:
                        st.error(f"Error deleting teacher: {e}")

            teachers_df = load_data(f"SELECT * FROM Teachers WHERE branch_name = '{selected_branch_name}'")
            if not teachers_df.empty:
                st.subheader("Existing Teachers")
                st.dataframe(teachers_df)
            else:
                st.warning("No teachers available. Please add teachers.")

        elif page == "Subjects":
            st.header("Manage Subjects, Chapters and Topics")
            
            # Fetch the branch ID
            conn = create_connection("school.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM Schools WHERE branch_name = ?", (selected_branch_name,))
            branch_result = cursor.fetchone()
            if branch_result:
                branch_id = branch_result[0]
            else:
                st.error("Error fetching Branch ID")
                return
            
            # Load subjects here, before the view page selection
            subjects_df = load_data(f"SELECT id, name FROM Subjects WHERE branch_id = {branch_id}")

            # Add a new sub-page for viewing chapters and topics
            view_page = st.sidebar.selectbox("Subject Actions", ["Manage Subjects", "View Chapters & Topics"], key="subjects_action_dropdown")
            
            if view_page == "View Chapters & Topics":
                st.subheader("View Chapters and Topics")

                # Select Subject for Chapter Management
                if not subjects_df.empty:
                    selected_subject_view = st.selectbox("Select Subject to View Chapters & Topics", options=subjects_df['name'].tolist(), key="select_subject_dropdown")
                    
                    # Get the ID of the selected subject
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM Subjects WHERE name = ? AND branch_id = ?", (selected_subject_view, branch_id))
                    subject_result = cursor.fetchone()
                    if subject_result:
                        selected_subject_id_view = subject_result[0]
                    else:
                        st.error("Error fetching Subject ID")
                        return

                    # Fetch Chapters and Topics
                    chapters_query = f"""
                        SELECT id, name FROM Chapters WHERE subject_id = {selected_subject_id_view}
                    """
                    chapters_df = load_data(chapters_query)
                    
                    if not chapters_df.empty:
                        for chapter_index, chapter_row in chapters_df.iterrows():
                            chapter_id = chapter_row['id']
                            chapter_name = chapter_row['name']
                            with st.expander(f"Chapter: {chapter_name}"):
                                topics_query = f"""
                                    SELECT id, name FROM Topics WHERE chapter_id = {chapter_id}
                                """
                                topics_df = load_data(topics_query)
                                if not topics_df.empty:
                                    st.write("Topics:")
                                    for topic_index, topic_row in topics_df.iterrows():
                                        topic_name = topic_row['name']
                                        st.write(f"- {topic_name}")
                                else:
                                    st.write("No topics for this chapter.")
                    else:
                        st.warning("No chapters for this subject")
                else:
                    st.warning("No subjects available. Please add subjects first.")
            elif view_page == "Manage Subjects":
                # --- Subject Management ---
                st.subheader("Manage Subjects")
                with st.form("add_subject_form"):
                    subject_name = st.text_input("Subject Name")
                    add_subject_submitted = st.form_submit_button("Add Subject")

                    if add_subject_submitted and subject_name:
                        try:
                            with conn:
                                cursor = conn.cursor()
                                # Check if subject already exists for the branch
                                cursor.execute("SELECT * FROM Subjects WHERE name = ? AND branch_id = ?",
                                                (subject_name, branch_id))
                                existing_subject = cursor.fetchone()
                                if existing_subject:
                                    st.error(f"Subject '{subject_name}' already exists for this branch.")
                                else:
                                    cursor.execute("INSERT INTO Subjects (name, branch_id) VALUES (?, ?)", (subject_name, branch_id))
                                    conn.commit()
                                    st.success(f"Subject '{subject_name}' added successfully!")
                        except Exception as e:
                            st.error(f"Error adding subject: {e}")
                # Delete Subject Form
                with st.form("delete_subject_form"):
                    if not subjects_df.empty:
                        subject_to_delete = st.selectbox("Select Subject to Delete", options=subjects_df['name'].tolist())
                        delete_subject_submitted = st.form_submit_button("Delete Subject")

                        if delete_subject_submitted and subject_to_delete:
                            try:
                                with conn:
                                    cursor = conn.cursor()
                                    cursor.execute("DELETE FROM Subjects WHERE name = ? AND branch_id = ?", (subject_to_delete, branch_id))
                                    conn.commit()
                                    st.success(f"Subject '{subject_to_delete}' deleted successfully!")
                            except Exception as e:
                                st.error(f"Error deleting subject: {e}")
                    else:
                        st.warning("No Subjects available. Please add subjects first.")

                # Display Subjects Table
                if not subjects_df.empty:
                    st.subheader("Existing Subjects")
                    st.dataframe(subjects_df)
                else:
                    st.warning("No subjects available")

                # --- Chapter Management ---
                st.subheader("Manage Chapters")

                # Select Subject for Chapter Management
                if not subjects_df.empty:
                    selected_subject = st.selectbox("Select Subject to Manage Chapters", options=subjects_df['name'].tolist())

                    # Get the ID of the selected subject
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM Subjects WHERE name = ? AND branch_id = ?", (selected_subject, branch_id))
                    subject_result = cursor.fetchone()
                    if subject_result:
                        selected_subject_id = subject_result[0]
                    else:
                        st.error("Error fetching Subject ID")
                        return
                    # Form to add chapters
                    with st.form("add_chapter_form"):
                        chapter_name = st.text_input("Chapter Name")
                        add_chapter_submitted = st.form_submit_button("Add Chapter")

                        if add_chapter_submitted and chapter_name:
                            try:
                                with conn:
                                    cursor = conn.cursor()
                                    # Check if chapter already exists for the subject
                                    cursor.execute("SELECT * FROM Chapters WHERE name = ? AND subject_id = ?",
                                                    (chapter_name, selected_subject_id))
                                    existing_chapter = cursor.fetchone()
                                    if existing_chapter:
                                        st.error(f"Chapter '{chapter_name}' already exists for subject '{selected_subject}'.")
                                    else:
                                        cursor.execute("INSERT INTO Chapters (name, subject_id) VALUES (?, ?)", (chapter_name, selected_subject_id))
                                        conn.commit()
                                        st.success(f"Chapter '{chapter_name}' added successfully for subject '{selected_subject}'!")
                            except Exception as e:
                                st.error(f"Error adding chapter: {e}")

                    # Delete Chapter form
                    chapters_df = load_data(f"SELECT id, name FROM Chapters WHERE subject_id = {selected_subject_id}")
                    with st.form("delete_chapter_form"):
                        if not chapters_df.empty:
                            chapter_to_delete = st.selectbox("Select Chapter to Delete", options=chapters_df['name'].tolist())
                            delete_chapter_submitted = st.form_submit_button("Delete Chapter")
                            if delete_chapter_submitted and chapter_to_delete:
                                try:
                                    with conn:
                                        cursor = conn.cursor()
                                        cursor.execute("DELETE FROM Chapters WHERE name = ? AND subject_id = ?", (chapter_to_delete, selected_subject_id))
                                        conn.commit()
                                        st.success(f"Chapter '{chapter_to_delete}' deleted successfully!")
                                except Exception as e:
                                    st.error(f"Error deleting chapter: {e}")
                        else:
                            st.warning("No chapters available. Please add chapters first.")

                    # Display Chapters Table
                    if not chapters_df.empty:
                        st.subheader(f"Existing Chapters for {selected_subject}")
                        st.dataframe(chapters_df)
                    else:
                        st.warning(f"No chapters available for {selected_subject}.")
                else:
                    st.warning("Please add subjects first")

                # --- Topic Management ---
                st.subheader("Manage Topics")
                if not subjects_df.empty:
                    # Select a subject for topic management
                    selected_subject_for_topic = st.selectbox("Select Subject for Topic Management", options=subjects_df['name'].tolist(), key="subject_topic_dropdown")

                    # Get the ID of the selected subject
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM Subjects WHERE name = ? AND branch_id = ?", (selected_subject_for_topic, branch_id))
                    subject_topic_result = cursor.fetchone()
                    if subject_topic_result:
                        selected_subject_topic_id = subject_topic_result[0]
                    else:
                        st.error("Error fetching Subject ID")
                        return

                    chapters_for_topic_df = load_data(f"SELECT id, name FROM Chapters WHERE subject_id = {selected_subject_topic_id}")

                    if not chapters_for_topic_df.empty:
                        # Select chapter for topic management
                        selected_chapter = st.selectbox("Select Chapter to Manage Topics", options=chapters_for_topic_df['name'].tolist())

                        # Get the ID of the selected chapter
                        cursor = conn.cursor()
                        cursor.execute("SELECT id FROM Chapters WHERE name = ? AND subject_id = ?", (selected_chapter, selected_subject_topic_id))
                        chapter_topic_result = cursor.fetchone()
                        if chapter_topic_result:
                            selected_chapter_id = chapter_topic_result[0]
                        else:
                            st.error("Error fetching Chapter ID")
                            return
                        # Form to add topic
                        with st.form("add_topic_form"):
                            topic_name = st.text_input("Topic Name")
                            add_topic_submitted = st.form_submit_button("Add Topic")

                            if add_topic_submitted and topic_name:
                                try:
                                    with conn:
                                        cursor = conn.cursor()
                                        # Check if topic already exists for chapter
                                        cursor.execute("SELECT * FROM Topics WHERE name = ? AND chapter_id = ?",
                                                        (topic_name, selected_chapter_id))
                                        existing_topic = cursor.fetchone()
                                        if existing_topic:
                                            st.error(f"Topic '{topic_name}' already exists for chapter '{selected_chapter}'.")
                                        else:
                                            cursor.execute("INSERT INTO Topics (name, chapter_id) VALUES (?, ?)", (topic_name, selected_chapter_id))
                                            conn.commit()
                                            st.success(f"Topic '{topic_name}' added successfully for chapter '{selected_chapter}'!")
                                except Exception as e:
                                    st.error(f"Error adding topic: {e}")

                        # Delete Topic Form
                        topics_df = load_data(f"SELECT id, name FROM Topics WHERE chapter_id = {selected_chapter_id}")
                        with st.form("delete_topic_form"):
                            if not topics_df.empty:
                                topic_to_delete = st.selectbox("Select Topic to Delete", options=topics_df['name'].tolist())
                                delete_topic_submitted = st.form_submit_button("Delete Topic")
                                if delete_topic_submitted and topic_to_delete:
                                    try:
                                        with conn:
                                            cursor = conn.cursor()
                                            cursor.execute("DELETE FROM Topics WHERE name = ? AND chapter_id = ?", (topic_to_delete, selected_chapter_id))
                                            conn.commit()
                                            st.success(f"Topic '{topic_to_delete}' deleted successfully!")
                                    except Exception as e:
                                        st.error(f"Error deleting topic: {e}")
                            else:
                                st.warning("No topics available. Please add topics first.")
                        # Display Topics Table
                        if not topics_df.empty:
                            st.subheader(f"Existing Topics for {selected_chapter}")
                            st.dataframe(topics_df)
                        else:
                            st.warning(f"No topics available for {selected_chapter}.")
                    else:
                        st.warning(f"Please add chapters first for {selected_subject_for_topic}")
                else:
                    st.warning("Please add subjects first")  

        elif page == "Students":
            st.header("Manage Students")

            # Fetch classes for the current branch
            classes_for_branch = load_data(f"SELECT id, class, section FROM Classes WHERE branch_id = (SELECT id FROM Schools WHERE branch_name = '{selected_branch_name}')")
            if classes_for_branch.empty:
                st.warning("No classes available for this branch. Add classes first.")
            else:
                # Add Student Form
                with st.form("add_student_form_branch"):
                    student_name = st.text_input("Student Name")
                    class_id = st.selectbox("Select Class", options=classes_for_branch['id'].tolist(),
                                            format_func=lambda x: f"Class {classes_for_branch[classes_for_branch['id'] == x]['class'].iloc[0]}-{classes_for_branch[classes_for_branch['id'] == x]['section'].iloc[0]}")
                    add_student_submitted = st.form_submit_button("Add Student")

                    if add_student_submitted and student_name and class_id:
                        if add_student(class_id, student_name):
                            st.success(f"Student '{student_name}' added successfully to class with id {class_id}!")
                        else:
                            st.error(f"Error adding student '{student_name}'.")

                # Delete Student Form
                with st.form("delete_student_form_branch"):
                    student_name_to_delete = st.text_input("Student Name to Delete")
                    delete_student_submitted = st.form_submit_button("Delete Student")

                    if delete_student_submitted and student_name_to_delete:
                        conn = create_connection("school.db")
                        try:
                            with conn:
                                cursor = conn.cursor()
                                # Fetch the student ID
                                cursor.execute("SELECT id FROM Students WHERE student_name = ?", (student_name_to_delete,))
                                student_id_result = cursor.fetchone()
                                if student_id_result:
                                    student_id = student_id_result[0]
                                    # Delete student from Students table
                                    cursor.execute("DELETE FROM Students WHERE id = ?", (student_id,))
                                    conn.commit()
                                    st.success(f"Student '{student_name_to_delete}' deleted successfully!")
                                else:
                                    st.error(f"Student '{student_name_to_delete}' not found.")
                        except Exception as e:
                            st.error(f"Error deleting student: {e}")

                # Display Students Table
                students_df = load_data(f"""
                    SELECT s.id, s.student_name, c.class, c.section
                    FROM Students s
                    JOIN Classes c ON s.class_id = c.id
                    WHERE c.branch_id = (SELECT id FROM Schools WHERE branch_name = '{selected_branch_name}')
                """)

                if not students_df.empty:
                    st.subheader("Existing Students")
                    st.dataframe(students_df)
                else:
                    st.warning("No students available. Please add students.")   

        elif page == "Bulk Upload":
            bulk_upload_component(selected_branch_name)


def main():
    st.title("School Management System")

    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user and st.sidebar.button("Logout"):
        st.session_state.user = None
        st.success("Logged out successfully.")
        return

    if not st.session_state.user:
        st.sidebar.header("Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")

        if st.sidebar.button("Login"):
            if username == "mteacher" and password == "admin":
                st.session_state.user = ("mteacher", None, None, "MalakpetTeacher",None)  # Simulate user data
                st.success(f"Welcome, Malakpet Teacher!")
            elif username == "dteacher" and password == "admin":
                st.session_state.user = ("dteacher", None, None, "DilshuknagarTeacher",None)  # Simulate user data
                st.success(f"Welcome, Dilshuknagar Teacher!")

            else:
                user = authenticate_user(username, password)
                if user:
                    st.session_state.user = user
                    st.success(f"Welcome, {username}!")
                else:
                    st.error("Invalid username or password.")
    else:
        role = st.session_state.user[3]  # Assuming role is the 4th column in the Users table
        if role == "SuperAdmin":
            superadmin_dashboard()
        elif role == "BranchAdmin":
            branchadmin_dashboard()
        elif role == "MalakpetTeacher":
            malakpet_teacher_dashboard()
        elif role == "DilshuknagarTeacher":
            dilshuknagar_teacher_dashboard()
        else:
            st.error("Unauthorized access.")


if __name__ == "__main__":
    main()
