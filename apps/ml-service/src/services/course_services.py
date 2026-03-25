from db.repositories import get_courses, get_courses_with_tags_raw
from utils.mappers import courses_with_tags_to_dict


async def iterate_courses(session, batch_size=1000):
    '''Asynchronously iterate through courses in batches.'''
    offset = 0

    while True:
        batch = await get_courses(session, batch_size, offset)

        if not batch:
            break

        yield batch
        offset += batch_size


async def get_courses_with_tags(session, limit=100, offset=0):
    """Fetch courses along with their associated tags, with pagination."""
    rows = await get_courses_with_tags_raw(session, limit, offset)
    return courses_with_tags_to_dict(rows)


async def iterate_courses_with_tags(session, batch_size=1000):
    """Asynchronously iterate through courses with their associated tags in batches."""
    offset = 0

    while True:
        batch = await get_courses_with_tags(session, batch_size, offset)

        if not batch:
            break

        yield batch
        offset += batch_size
