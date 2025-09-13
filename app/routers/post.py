from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app import models
from app.database import get_db
from app.logger import logger
from app.oauth2 import get_current_user
from app.schemas import Post, PostCreate, PostOut

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

# @router.get("/", response_model=list[Post], status_code=status.HTTP_200_OK)
@router.get("/", response_model=list[PostOut], status_code=status.HTTP_200_OK)
def get_posts(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    logger.info("Fetching all posts")
    # posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).order_by(models.Post.created_at.desc()).all() # type: ignore
    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True
    ).group_by(models.Post.id).all()
    # logger.info(f"Retrieved posts: {len(posts)} found")
    logger.info(f"Retrieved posts: {len(results)} found")
    return results


# @router.get("/{id}", response_model=Post, status_code=status.HTTP_200_OK)
@router.get("/{id}", response_model=PostOut, status_code=status.HTTP_200_OK)
def get_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # post = db.query(models.Post).filter(models.Post.id == id).first()
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True
    ).group_by(models.Post.id).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} not found")
    return post  


@router.post("/", response_model=Post, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_post = models.Post(owner_id=current_user.id,**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.put("/{id}", response_model=Post, status_code=status.HTTP_202_ACCEPTED)
def update_post(id: int, updated_post: PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} not found")
    if getattr(post, "owner_id", None) != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    post_query.update({getattr(models.Post, key): value for key, value in updated_post.model_dump().items()}, synchronize_session=False)
    db.commit()
    return post_query.first()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} not found")
    if getattr(post, "owner_id", None) != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    db.delete(post)
    db.commit()
    return {"message": "Post deleted successfully"}