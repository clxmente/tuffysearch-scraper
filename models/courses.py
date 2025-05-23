from typing import TypedDict


class RawCourse(TypedDict):
    course_id: int
    department: str
    header: str
    blocks: list[str]


class ProcessedCourse(TypedDict):
    course_id: int
    department: str
    course_level: int
    title: str
    description: str
    course_code: str
    units: str
    prerequisites: str
    grad_credit: bool
    available_online: bool
    requires_dept_consent: bool
    typically_offered: str
