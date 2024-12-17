import logging
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlmodel import Session

from ...db.database import get_db
from ...db.models import Script, BlogPost
from ...db.schemas import ScriptCreate, ScriptUpdate, BlogPostCreate, BlogPostUpdate
from ...services.content_service import ContentService
from ...utils.s3_util import S3Util

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

content_router = APIRouter()


def get_content_service(db: Session = Depends(get_db)):
    s3_util = S3Util()
    return ContentService(db, s3_util)


@content_router.post("/scripts", response_model=Script, tags=["Content 📜"], description="Create a new script")
def create_script(script_in: ScriptCreate, author_id: uuid.UUID, use_ai_metadata: bool = False,
                  service: ContentService = Depends(get_content_service)):
    try:
        logger.info("Creating a new script")
        script = service.create_script(script_in, author_id, use_ai_metadata)
        logger.info("Script created successfully")
        return script
    except Exception as e:
        logger.error(f"Error creating script: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating script")


@content_router.get("/scripts/{script_id}", response_model=Script, tags=["Content 📜"], description="Get a script by ID")
def get_script(script_id: uuid.UUID, service: ContentService = Depends(get_content_service)):
    try:
        logger.info(f"Fetching script with ID {script_id}")
        script = service.get_script(script_id)
        if not script:
            logger.warning(f"Script with ID {script_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Script not found")
        logger.info(f"Script with ID {script_id} fetched successfully")
        return script
    except Exception as e:
        logger.error(f"Error fetching script with ID {script_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching script")


@content_router.put("/scripts/{script_id}", response_model=Script, tags=["Content 📜"],
                    description="Update a script by ID")
def update_script(script_id: uuid.UUID, script_in: ScriptUpdate, service: ContentService = Depends(get_content_service)):
    try:
        logger.info(f"Updating script with ID {script_id}")
        script = service.update_script(script_id, script_in)
        if not script:
            logger.warning(f"Script with ID {script_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Script not found")
        logger.info(f"Script with ID {script_id} updated successfully")
        return script
    except Exception as e:
        logger.error(f"Error updating script with ID {script_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating script")


@content_router.delete("/scripts/{script_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Content 📜"],
                       description="Delete a script by ID")
def delete_script(script_id: uuid.UUID, service: ContentService = Depends(get_content_service)):
    try:
        logger.info(f"Deleting script with ID {script_id}")
        service.delete_script(script_id)
        logger.info(f"Script with ID {script_id} deleted successfully")
        return None
    except Exception as e:
        logger.error(f"Error deleting script with ID {script_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting script")


@content_router.post("/blog_posts", response_model=BlogPost, tags=["Content 📝"], description="Create a new blog post")
async def create_blog_post(
        title: str = Form(...),
        content: str = Form(...),
        tags: List[str] = Form(...),
        category: str = Form(...),
        author_id: uuid.UUID = Form(...),
        image: UploadFile = File(...),
        revise: bool = Form(False),
        db: Session = Depends(get_db)
):
    try:
        logger.info("Creating a new blog post")
        blog_post_in = BlogPostCreate(
            title=title,
            content=content,
            tags=tags,
            category=category,
            author_id=author_id  # Ensure author_id is included here
        )
        service = ContentService(db, s3_util=S3Util())
        blog_post = service.create_blog_post(blog_post_in, image, revise)
        logger.info("Blog post created successfully")
        return blog_post
    except Exception as e:
        logger.error(f"Error creating blog post: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating blog post")


@content_router.get("/blog_posts/{blog_post_id}", response_model=BlogPost, tags=["Content 📝"],
                    description="Get a blog post by ID")
def get_blog_post(blog_post_id: uuid.UUID, service: ContentService = Depends(get_content_service)):
    try:
        logger.info(f"Fetching blog post with ID {blog_post_id}")
        blog_post = service.get_blog_post(blog_post_id)
        if not blog_post:
            logger.warning(f"Blog post with ID {blog_post_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog post not found")
        logger.info(f"Blog post with ID {blog_post_id} fetched successfully")
        return blog_post
    except Exception as e:
        logger.error(f"Error fetching blog post with ID {blog_post_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching blog post")


@content_router.put("/blog_posts/{blog_post_id}", response_model=BlogPost, tags=["Content 📝"],
                    description="Update a blog post by ID")
def update_blog_post(blog_post_id: uuid.UUID, blog_post_in: BlogPostUpdate,
                     service: ContentService = Depends(get_content_service)):
    try:
        logger.info(f"Updating blog post with ID {blog_post_id}")
        blog_post = service.update_blog_post(blog_post_id, blog_post_in)
        if not blog_post:
            logger.warning(f"Blog post with ID {blog_post_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog post not found")
        logger.info(f"Blog post with ID {blog_post_id} updated successfully")
        return blog_post
    except Exception as e:
        logger.error(f"Error updating blog post with ID {blog_post_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating blog post")


@content_router.delete("/blog_posts/{blog_post_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Content 📝"],
                       description="Delete a blog post by ID")
def delete_blog_post(blog_post_id: uuid.UUID, service: ContentService = Depends(get_content_service)):
    try:
        logger.info(f"Deleting blog post with ID {blog_post_id}")
        service.delete_blog_post(blog_post_id)
        logger.info(f"Blog post with ID {blog_post_id} deleted successfully")
        return None
    except Exception as e:
        logger.error(f"Error deleting blog post with ID {blog_post_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting blog post")