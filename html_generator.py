def course_summary(user_name: str = "", uc=[], pc=[]) -> str:

    upcoming_courses_str = " ".join([f'<li>{course}</li>' for course in uc])
    planned_courses_str = " ".join([f'<li>{course}</li>' for course in pc])

    return (f"""
    <b>Cześć {user_name}!</b>
    <br />
    Oto lista kursów które wybrałeś i zostaniesz powiadomiony o ich rozpoczęciu:
    {upcoming_courses_str}
    <hr />
    Tutaj lista kursów które wybrałeś ale są nadal w produkcji:
    <ul>
    {planned_courses_str}
    </ul>
    <hr />
    <br />
    <i>
    Pozdrawiamy! <br />
    Zespół NEWGRADVETS
    </i>
    """)
