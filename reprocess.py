import os
import json

from rich.progress import Progress, BarColumn, SpinnerColumn, TextColumn
from models.courses import RawCourse, ProcessedCourse


def reprocess_course(course: RawCourse) -> ProcessedCourse:
    """Convert the raw course data into a processed object

    :param RawCourse course: The raw course data scraped from the catalog
    :return ProcessedCourse: A processed course object with relevant fields extracted
    """
    # Example: "ACCT 201A - Financial Accounting (3)" -> ["ACCT 201A", "Financial Accounting (3)"]
    header_parts = course["header"].split("-", maxsplit=1)
    # example: "ACCT 201A"
    course_code = header_parts[0].strip()
    # extract title and units from second part
    title_units = header_parts[1].strip()
    # for the units we'll look for everything between the first and last parenthesis
    units = title_units[title_units.rfind("(") + 1 : title_units.rfind(")")]
    # now remove the units from the string to get the title
    title = title_units[: title_units.rfind("(")].strip()

    # extract the course level as an integer, handling special cases like "10S" which apparently exist
    # for some early start courses
    course_number = course_code.split(" ")[1]
    level_str = ""
    for char in course_number:
        if char.isdigit():
            level_str += char
        else:
            break
    course_level = int(level_str)

    # we'll create it with some defaults and override based on values we find
    processed_course: ProcessedCourse = {
        "course_id": course["course_id"],
        "department": course["department"],
        "course_level": course_level,
        "title": title,
        "description": course["blocks"][0],
        "course_code": course_code,
        "units": units,
        "prerequisites": "",
        "grad_credit": False,
        "available_online": False,
        "requires_dept_consent": False,
        "typically_offered": "",
    }
    # now we'll go through the blocks and extract the relevant information
    # typically the order is prerequisites, available for grad credit, available online, dept consent required, when its offered
    # there may be some extra but we'll just ignore it and log it
    for block in course["blocks"][1:]:
        if "requisite" in block.lower() or block.lower().startswith("prereq"):
            processed_course["prerequisites"] = block
        elif block.lower() == "undergraduate course not available for graduate credit":
            processed_course["grad_credit"] = False
        elif block.lower() in [
            "graduate-level",
            "400-level undergraduate course available for graduate credit",
        ]:
            processed_course["grad_credit"] = True
        elif (
            block.lower() == "one or more sections may be offered in any online format."
        ):
            processed_course["available_online"] = True
        elif block.lower() == "department consent required":
            processed_course["requires_dept_consent"] = True
        elif block.lower().startswith("typically offered"):
            processed_course["typically_offered"] = block.split(":")[1].strip()
        else:
            print(f"Unknown block in {course_code}: {block}")
    return processed_course


if __name__ == "__main__":
    RAW_COURSES_FILE = "raw_2025-2026_catalog.json"
    with open(os.path.join("data", RAW_COURSES_FILE)) as f:
        data = json.load(f)

    processed_courses = []

    progress = Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=None),
        SpinnerColumn(finished_text="✅"),
        TextColumn("[bold blue]{task.completed}/{task.total}"),
    )

    with progress:
        task = progress.add_task("Processing courses...", total=len(data))
        for course in data:
            processed_courses.append(reprocess_course(course))
            progress.update(task, advance=1)

    new_filename = RAW_COURSES_FILE.replace("raw_", "processed_")
    with open(os.path.join("data", new_filename), "w") as f:
        json.dump(processed_courses, f, indent=2)
