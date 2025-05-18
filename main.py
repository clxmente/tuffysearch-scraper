import os
import bs4
import json
import requests
import logging
import traceback

from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from concurrent.futures import ThreadPoolExecutor, Future
from modules.course_departments import CourseDepartments
from rich.progress import TaskID, Progress, BarColumn, SpinnerColumn, TextColumn

OUTPUT_FILENAME = "2025-2026_catalog.json"
# Find in url at csuf course catalog and click on the course descriptions
NAVOID = 14518
CATOID = 95

EXPANDED_URLS = [
    f"https://catalog.fullerton.edu/content.php?catoid={CATOID}&navoid={NAVOID}&filter[27]=-1&filter[29]=&filter[keyword]=&filter[32]=1&filter[cpage]={i}&filter[exact_match]=1&filter[item_type]=3&filter[only_active]=1&filter[3]=1&expand=1&print#acalog_template_course_filter"
    for i in range(1, 40)
]

UNEXPANDED_URLS = [
    f"https://catalog.fullerton.edu/content.php?catoid={CATOID}&navoid={NAVOID}&filter[27]=-1&filter[29]=&filter[keyword]=&filter[32]=1&filter[cpage]={i}&filter[exact_match]=1&filter[item_type]=3&filter[only_active]=1&filter[3]=1&print#acalog_template_course_filter"
    for i in range(1, 40)
]


def get_courses_table(soup: bs4.BeautifulSoup):
    """Find the last table with class "table_default" in the soup. This is the table containing a page's course information.

    :param bs4.BeautifulSoup soup: The entire soup of the page.
    :return bs4.element.Tag: A table element for the courses on the page.
    """
    return soup.find_all("table", class_="table_default")[-1]


def get_course_id(unexpanded_element) -> int:
    """The unexpanded table contains the course id in the href of the <a> tag.

    Example: `<a href="preview_course_nopop.php?catoid=95&coid=594896" .. />`

    :param bs4.element.Tag unexpanded_element: The unexpanded table row element for a course.
    :return int: The course id as an integer.
    """
    href_value = unexpanded_element.find("a")["href"]
    course_id = href_value.split("coid=")[1]
    return int(course_id)


def get_course_info(
    expanded_element, course_id: int, department: str
) -> dict[str, str | int]:
    """Returns a dictionary containing the course information.

    Args:
        expanded_element (bs4.element.Tag): The element from the table containing the course information.
        course_id (int): The id of the course. Taken from unexpanded version <a> tag.
        department (str): The department of the course taken from the section header.

    Returns:
        dict[str, str]: A dictionary containing the course information.

    Example Course:
    ```json
        {
            "title": "Financial Accounting",
            "description": "Accounting concepts and techniques essential to the ...",
            "department": "Accounting",
            "course_code": "ACCT 201A",
            "course_id": 537360,
            "units": "1-3",
            "prereqs": "Prerequisites: ACCT 301A , BUAD 301 with a 'C' (2.0) or better",
            "grad_credit": true,
            "available_online": true,
            "typically_offered": "Fall/Spring",
            "requires_dept_consent": true,
        }
    ```
    """
    course_header = expanded_element.find("h3").text.strip()
    # Example: "ACCT 201A - Financial Accounting (3)" -> ["ACCT 201A", "Financial Accounting (3)"]
    course_parts = course_header.split("-", maxsplit=1)
    # Get course code from first part
    course_code = course_parts[0].strip()
    # Get title and units from second part
    title_and_units = course_parts[1].strip()
    # Extract units from parentheses and convert to int
    units = title_and_units[title_and_units.rfind("(") + 1 : title_and_units.rfind(")")]
    # Get title by removing units portion
    course_title = title_and_units[: title_and_units.rfind("(")].strip()

    # the description is always the first text after the header, we want to parse everything after description
    sibling = expanded_element.find("h3").find_next_sibling("hr").next_sibling
    blocks = []
    current_block = ""
    while sibling:
        if sibling.name == "br":
            if current_block.strip():
                blocks.append(current_block.strip())
                current_block = ""
        else:
            text = sibling.text.strip()
            if text:
                current_block += " " + text
        sibling = sibling.next_sibling
    if current_block.strip():
        blocks.append(current_block.strip())

    course = {
        "title": course_title.strip(),
        "description": blocks[0].strip(),
        "department": department,
        "course_code": course_code.strip(),
        "course_id": course_id,
        "units": units,
    }

    # add extra fields if they exist
    # typically the order is prereqs, available for grad credit, available online, dept consent required, typically offered
    # we've extracted these strings from all text after the description
    for block in blocks[1:]:
        if "requisite" in block.lower() or block.lower().startswith("prereq"):
            course["prereqs"] = block
        elif block.lower() == "undergraduate course not available for graduate credit":
            course["grad_credit"] = False
        elif block.lower() in [
            "graduate-level",
            "400-level undergraduate course available for graduate credit",
        ]:
            course["grad_credit"] = True
        elif (
            block.lower() == "one or more sections may be offered in any online format."
        ):
            course["available_online"] = True
        elif block.lower() == "department consent required":
            course["requires_dept_consent"] = True
        elif block.lower().startswith("typically offered:"):
            course["typically_offered"] = block.split(":")[1].strip()
        else:
            print(f"unknown block in {course_code}:", block)

    # extract course level, handling special cases like "10S" which apparently exist
    # for some early start courses
    course_number = course_code.split(" ")[1]
    level_str = ""
    for char in course_number:
        if char.isdigit():
            level_str += char
        else:
            break
    course["course_level"] = int(level_str)
    return course


def loop_through_courses(
    expanded_table, unexpanded_table, courses: dict[str, dict[str, str | int]]
) -> None:
    """Loop through individual page of courses and add them to the courses dictionary.

    Args:
        expanded_table (bs4.element.Tag): Page element containing the expanded course information. Used for getting the course description.
        unexpanded_table (bs4.element.Tag): Page element containing the unexpanded course information. Used for getting the course id.
        courses (dict[str, dict[str, str | int]]): Dictionary containing all the courses. Keys are course ids.
    """

    # ! For some reason, the table body is not found in da soup.
    # expanded_body = expanded_table.find("tbody")
    # unexpanded_body = unexpanded_table.find("tbody")

    current_section = ""
    expanded_row: bs4.element.Tag
    unexpanded_row: bs4.element.Tag
    for expanded_row, unexpanded_row in zip(
        expanded_table.find_all("tr"), unexpanded_table.find_all("tr"), strict=True
    ):
        # check to make sure there are two td elements in this tag, else skip
        # Section headers have 1 td element
        if (
            len(expanded_row.find_all("td")) != 2
            or len(unexpanded_row.find_all("td")) != 2
        ):
            # Check if this is a section header row (1 td element)
            if len(expanded_row.find_all("td")) == 1:
                header_td = expanded_row.find("td")
                if (
                    header_td
                    and header_td.find("p")  # type: ignore
                    and header_td.find("p").find("strong")  # type: ignore
                ):
                    current_section = header_td.find("p").find("strong").text.strip()  # type: ignore
            continue

        expanded_course_element = expanded_row.find_all("td")[1]
        unexpanded_course_element = unexpanded_row.find_all("td")[1]

        course_id = get_course_id(unexpanded_course_element)

        course = get_course_info(
            expanded_element=expanded_course_element,
            course_id=course_id,
            department=current_section,
        )
        courses[str(course_id)] = course


job_progress = Progress(
    TextColumn("[bold blue]{task.description}", justify="left"),
    BarColumn(bar_width=None),
    SpinnerColumn(finished_text="✅"),
)


def process_page(
    expanded_url: str,
    unexpanded_url: str,
    courses: dict[str, dict[str, str | int]],
    task_id: TaskID,
) -> None:
    try:
        expanded_page = requests.get(expanded_url)
        job_progress.update(task_id, advance=0.25)
        unexpanded_page = requests.get(unexpanded_url)
        job_progress.update(task_id, advance=0.25)

        expanded_soup = bs4.BeautifulSoup(expanded_page.text, "html.parser")
        job_progress.update(task_id, advance=0.125)
        unexpanded_soup = bs4.BeautifulSoup(unexpanded_page.text, "html.parser")
        job_progress.update(task_id, advance=0.125)

        expanded_table = get_courses_table(expanded_soup)
        unexpanded_table = get_courses_table(unexpanded_soup)

        loop_through_courses(
            expanded_table=expanded_table,
            unexpanded_table=unexpanded_table,
            courses=courses,
        )
        job_progress.update(task_id, advance=0.25)
        overall_progress.update(overall_task, advance=1)
    except Exception as e:
        logging.error(f"Error processing page {expanded_url}:")
        logging.error(traceback.format_exc())
        # Mark the task as failed in the progress bar
        job_progress.update(
            task_id,
            completed=1,
            description=f"❌ Page {expanded_url.split('cpage=')[1].split('&')[0]} failed",
        )
        overall_progress.update(overall_task, advance=1)
        raise  # Re-raise the exception to be caught by the main thread


overall_progress = Progress(
    TextColumn("[bold blue]{task.description}", justify="left"),
    BarColumn(bar_width=None),
    TextColumn("[bold blue]{task.completed}/{task.total}"),
)
overall_task = overall_progress.add_task("All Pages", total=len(EXPANDED_URLS))

progress_table = Table().grid()
progress_table.add_row(
    Panel.fit(
        overall_progress, title="[b]All Pages", border_style="green", padding=(2, 2)
    )
)
progress_table.add_row(
    Panel.fit(job_progress, title="[b]Pages", border_style="red", padding=(2, 2))
)

if __name__ == "__main__":
    # 2024-2025, for some reason 2025-2026 is missing the course departments page
    course_departments = CourseDepartments(navoid=13399, catoid=91)

    Courses = {}
    futures: list[Future] = []

    with Live(progress_table, refresh_per_second=10):
        with ThreadPoolExecutor() as pool:
            for i, (expanded_url, unexpanded_url) in enumerate(
                zip(EXPANDED_URLS, UNEXPANDED_URLS)
            ):
                task_id = job_progress.add_task(f"Page {i + 1}", total=1)
                future = pool.submit(
                    process_page,
                    expanded_url,
                    unexpanded_url,
                    Courses,
                    task_id,
                )
                futures.append(future)

            # Wait for all futures to complete and check for exceptions
            for future in futures:
                try:
                    future.result()  # This will raise any exceptions that occurred
                except Exception as e:
                    logging.error("A thread encountered an error")
                    # Don't exit immediately, let other threads complete

    # Only save if we have some data
    if Courses:
        with open(os.path.join(os.getcwd(), "data", OUTPUT_FILENAME), "w") as f:
            json.dump(Courses, f, indent=2)
        logging.info(f"Successfully saved {len(Courses)} courses to {OUTPUT_FILENAME}")
    else:
        logging.error("No courses were scraped successfully")
