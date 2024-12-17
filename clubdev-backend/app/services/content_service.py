# content_service.py
import logging
import uuid
from functools import lru_cache

from fastapi import UploadFile, HTTPException, status
from sqlmodel import Session, select
from ..crud import script, blog_post
from ..db.models import Script, BlogPost, User
from ..db.schemas import ScriptCreate, ScriptUpdate, BlogPostCreate, BlogPostUpdate
from ..utils.gemini_util import create_model, generate_metadata_from_code, revise_blog_entry, configure_genai, \
    create_generation_config
from ..utils.s3_util import S3Util

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentService:
    def __init__(self, db: Session, s3_util: S3Util):
        self.db = db
        self.s3_util = s3_util
        configure_genai()  # Ensure the API key is configured
        self.model = create_model("gemini-2.0-flash-exp")  # Create the model
        self.config = create_generation_config()

    def create_script(self, script_in: ScriptCreate, author_id: uuid.UUID, use_ai_metadata: bool = False) -> Script:
        try:
            # Validate that the author_id exists and is a UUID
            if not isinstance(author_id, uuid.UUID):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid author ID")

            statement = select(User).where(User.id == author_id)
            author = self.db.exec(statement).first()
            if not author:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")

            if use_ai_metadata:
                logger.info("Generating metadata using AI")
                metadata = generate_metadata_from_code(self.model, self.config, script_in.content)
                logger.info(f"Generated metadata: {metadata}")
                script_in.title = metadata.get("title", script_in.title)
                script_in.description = metadata.get("description", script_in.description)
                script_in.use_cases = ", ".join(metadata.get("use_cases", []))
                script_in.instructions = metadata.get("instructions", script_in.instructions)
                script_in.language = metadata.get("language", script_in.language)
                script_in.framework = metadata.get("framework", script_in.framework)
                script_in.license = metadata.get("license", script_in.license)
                script_in.tags = metadata.get("tags", script_in.tags)
                script_in.grade = metadata.get("grade", script_in.grade)

            new_script = script.create(self.db, script_in)
            new_script.author_id = author_id
            author.scripts_count += 1  # Increment the scripts count
            self.db.commit()
            self.db.refresh(new_script)
            return new_script
        except Exception as e:
            logger.error(f"Error creating script: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating script: {e}")

    @lru_cache(maxsize=128)
    def get_script(self, script_id: uuid.UUID) -> Script:
        try:
            return script.get(self.db, script_id)
        except Exception as e:
            logger.error(f"Error getting script with ID {script_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error getting script")

    def update_script(self, script_id: uuid.UUID, script_in: ScriptUpdate) -> Script:
        try:
            return script.update(self.db, script_id, script_in)
        except Exception as e:
            logger.error(f"Error updating script with ID {script_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating script")

    def delete_script(self, script_id: uuid.UUID) -> None:
        try:
            script_obj = script.get(self.db, script_id)
            if script_obj:
                author = self.db.get(User, script_obj.author_id)
                if author:
                    author.scripts_count -= 1  # Decrement the scripts count
                script.delete(self.db, script_id)
                self.db.commit()
        except Exception as e:
            logger.error(f"Error deleting script with ID {script_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting script")

    def create_blog_post(self, blog_post_in: BlogPostCreate, image: UploadFile, revise: bool = False) -> BlogPost:
        try:
            if revise:
                revised_content = revise_blog_entry(self.model, self.config, blog_post_in.content)
                blog_post_in.title = revised_content.get("title", blog_post_in.title)
                blog_post_in.content = revised_content.get("content", blog_post_in.content)
                blog_post_in.tags = revised_content.get("tags", blog_post_in.tags)
                blog_post_in.category = revised_content.get("category", blog_post_in.category)

            image_url = self.s3_util.upload_file(image, "blog_images")
            blogger_post = BlogPost(**blog_post_in.model_dump(), image_url=image_url)
            self.db.add(blogger_post)
            author = self.db.get(User, blog_post_in.author_id)
            if author:
                author.blog_posts_count += 1  # Increment the blog posts count
            self.db.commit()
            self.db.refresh(blogger_post)
            return blogger_post
        except Exception as e:
            logger.error(f"Error creating blog post: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating blog post")

    @lru_cache(maxsize=128)
    def get_blog_post(self, blog_post_id: uuid.UUID) -> BlogPost:
        try:
            return blog_post.get(self.db, blog_post_id)
        except Exception as e:
            logger.error(f"Error getting blog post with ID {blog_post_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error getting blog post")

    def update_blog_post(self, blog_post_id: uuid.UUID, blog_post_in: BlogPostUpdate) -> BlogPost:
        try:
            return blog_post.update(self.db, blog_post_id, blog_post_in)
        except Exception as e:
            logger.error(f"Error updating blog post with ID {blog_post_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating blog post")

    def delete_blog_post(self, blog_post_id: uuid.UUID) -> None:
        try:
            blog_post_obj = blog_post.get(self.db, blog_post_id)
            if blog_post_obj:
                author = self.db.get(User, blog_post_obj.author_id)
                if author:
                    author.blog_posts_count -= 1  # Decrement the blog posts count
                blog_post.delete(self.db, blog_post_id)
                self.db.commit()
        except Exception as e:
            logger.error(f"Error deleting blog post with ID {blog_post_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting blog post")