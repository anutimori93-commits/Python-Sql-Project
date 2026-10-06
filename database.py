import os
import pandas as pd
from sqlalchemy import create_engine, text


# --------------------------------------------------
# CONFIGURE YOUR MYSQL WORKBENCH CREDENTIALS
# --------------------------------------------------

DB_USER = "root"
DB_PASSWORD = "admin"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "campus_db"

CSV_PATH = r"C:\Users\HP\OneDrive\Desktop\Python Sql Project\indian_engineering_placement_2026.csv"


# --------------------------------------------------
# DATABASE URL
# --------------------------------------------------

DEFAULT_DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"
)

DATABASE_URL = f"{DEFAULT_DATABASE_URL}/{DB_NAME}"


# --------------------------------------------------
# CREATE DATABASE
# --------------------------------------------------

def ensure_database():
    """
    Create the target database if it does not exist.
    """

    default_engine = create_engine(DEFAULT_DATABASE_URL)

    try:
        with default_engine.connect() as conn:

            conn.execute(
                text(
                    f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`"
                )
            )

            conn.commit()

    finally:
        default_engine.dispose()


# --------------------------------------------------
# INITIALIZE DATABASE
# --------------------------------------------------

def init_db(csv_path=CSV_PATH):
    """
    Read CSV, clean data, handle missing values,
    load data into MySQL and create indexes.
    """

    # --------------------------------------------------
    # CHECK CSV FILE
    # --------------------------------------------------

    if not os.path.exists(csv_path):

        raise FileNotFoundError(
            f"Source file '{csv_path}' was not found."
        )


    # --------------------------------------------------
    # CREATE DATABASE
    # --------------------------------------------------

    ensure_database()


    # --------------------------------------------------
    # CREATE ENGINE
    # --------------------------------------------------

    engine = create_engine(DATABASE_URL)


    # --------------------------------------------------
    # READ CSV FILE
    # --------------------------------------------------

    df = pd.read_csv(csv_path)

    print("CSV loaded successfully!")

    print("Number of rows:", df.shape[0])
    print("Number of columns:", df.shape[1])


    # --------------------------------------------------
    # HANDLE MISSING VALUES
    # --------------------------------------------------

    if "Open_Source_Contributions" in df.columns:

        df["Open_Source_Contributions"] = (
            df["Open_Source_Contributions"]
            .fillna(
                df["Open_Source_Contributions"].median()
            )
        )


    if "Linkedin_Activity_Score" in df.columns:

        df["Linkedin_Activity_Score"] = (
            df["Linkedin_Activity_Score"]
            .fillna(
                df["Linkedin_Activity_Score"].median()
            )
        )


    # --------------------------------------------------
    # LOAD DATA INTO MYSQL
    # --------------------------------------------------

    df.to_sql(
        "students",
        con=engine,
        if_exists="replace",
        index=False
    )

    print("Data successfully loaded into MySQL!")


    # --------------------------------------------------
    # CREATE INDEXES
    # --------------------------------------------------

    with engine.connect() as conn:

        # College Tier Index
        if "College_Tier" in df.columns:

            conn.execute(
                text(
                    "ALTER TABLE students "
                    "ADD INDEX idx_tier (`College_Tier`(50));"
                )
            )


        # Branch Index
        if "Branch" in df.columns:

            conn.execute(
                text(
                    "ALTER TABLE students "
                    "ADD INDEX idx_branch (`Branch`(50));"
                )
            )


        # Placement Status Index
        if "placement_status" in df.columns:

            conn.execute(
                text(
                    "ALTER TABLE students "
                    "ADD INDEX idx_placement "
                    "(`placement_status`(20));"
                )
            )


        # CGPA Index
        if "cgpa" in df.columns:

            conn.execute(
                text(
                    "ALTER TABLE students "
                    "ADD INDEX idx_cgpa (`cgpa`);"
                )
            )


        # DSA Problems Solved Index
        if "DSA_Problems_Solved" in df.columns:

            conn.execute(
                text(
                    "ALTER TABLE students "
                    "ADD INDEX idx_dsa "
                    "(`DSA_Problems_Solved`);"
                )
            )


        conn.commit()


    print("Indexes created successfully!")

    print(
        "Data successfully loaded and indexed "
        "in MySQL Workbench!"
    )


# --------------------------------------------------
# RUN SQL QUERY
# --------------------------------------------------

def run_query(query, params=None):
    """
    Run SQL queries against MySQL using SQLAlchemy.
    """

    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:

        result = pd.read_sql_query(
            text(query),
            conn,
            params=params
        )

    return result


# --------------------------------------------------
# MAIN PROGRAM
# --------------------------------------------------

if __name__ == "__main__":

    init_db()