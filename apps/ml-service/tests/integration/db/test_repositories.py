import pytest
import pandas as pd
from unittest.mock import AsyncMock, MagicMock
from src.db.repositories import (
    save_df,
    get_user_by_id,
    get_course_by_id,
    get_courses,
    get_all_tags,
    get_tags_by_course,
    get_courses_with_tags_raw,
    get_actions_by_user,
    get_actions_by_course
)
from src.db.models import Course, User, Tag, Action

@pytest.mark.asyncio
async def test_save_df(mock_session):
    df = pd.DataFrame({
        "col1": [1, 2],
        "col2": ["a", "b"]
    })
    
    await save_df(mock_session, df, Course, batch_size=1)
    
    assert mock_session.execute.call_count == 2

@pytest.mark.asyncio
async def test_save_df_empty(mock_session):
    df = pd.DataFrame()
    await save_df(mock_session, df, Course)
    mock_session.execute.assert_not_called()

@pytest.mark.asyncio
async def test_get_user_by_id(mock_session):
    mock_result = MagicMock()
    mock_user = User(user_id=1)
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_session.execute.return_value = mock_result
    
    user = await get_user_by_id(mock_session, 1)
    
    assert user == mock_user
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_course_by_id(mock_session):
    mock_result = MagicMock()
    mock_course = Course(course_id=1)
    mock_result.scalar_one_or_none.return_value = mock_course
    mock_session.execute.return_value = mock_result
    
    course = await get_course_by_id(mock_session, 1)
    
    assert course == mock_course
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_courses(mock_session):
    mock_result = MagicMock()
    mock_courses = [Course(course_id=1), Course(course_id=2)]
    mock_result.scalars().all.return_value = mock_courses
    mock_session.execute.return_value = mock_result
    
    courses = await get_courses(mock_session, limit=10, offset=0)
    
    assert courses == mock_courses
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_all_tags(mock_session):
    mock_result = MagicMock()
    mock_tags = [Tag(tag_id=1), Tag(tag_id=2)]
    mock_result.scalars().all.return_value = mock_tags
    mock_session.execute.return_value = mock_result
    
    tags = await get_all_tags(mock_session)
    
    assert tags == mock_tags
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_tags_by_course(mock_session):
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [("tag1",), ("tag2",)]
    mock_session.execute.return_value = mock_result
    
    tags = await get_tags_by_course(mock_session, 1)
    
    assert tags == ["tag1", "tag2"]
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_courses_with_tags_raw(mock_session):
    mock_result = MagicMock()
    mock_data = [(1, "Course 1", "Desc", "Easy", ["tag1"])]
    mock_result.fetchall.return_value = mock_data
    mock_session.execute.return_value = mock_result
    
    data = await get_courses_with_tags_raw(mock_session)
    
    assert data == mock_data
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_actions_by_user(mock_session):
    mock_result = MagicMock()
    mock_actions = [Action(user_id=1)]
    mock_result.scalars().all.return_value = mock_actions
    mock_session.execute.return_value = mock_result
    
    actions = await get_actions_by_user(mock_session, 1)
    
    assert actions == mock_actions
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_actions_by_course(mock_session):
    mock_result = MagicMock()
    mock_actions = [Action(course_id=1)]
    mock_result.scalars().all.return_value = mock_actions
    mock_session.execute.return_value = mock_result
    
    actions = await get_actions_by_course(mock_session, 1)
    
    assert actions == mock_actions
    mock_session.execute.assert_called_once()
