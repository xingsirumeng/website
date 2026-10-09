from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Project
from app.schemas import ProjectCreate, ProjectResponse, ProjectUpdate

# 公开读取
router = APIRouter(tags=["projects"])

# 管理接口，鉴权由 main.py 注册时统一挂上 require_admin
admin_router = APIRouter(tags=["projects"])


def _ordered(query):
    """先按 sort 从大到小（手动排的优先级），再按 id 从新到旧"""
    return query.order_by(Project.sort.desc(), Project.id.desc())


@router.get("/projects", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    """已发布的项目"""
    return _ordered(db.query(Project).filter(Project.published.is_(True))).all()


@admin_router.get("/projects", response_model=list[ProjectResponse])
def admin_list_projects(db: Session = Depends(get_db)):
    """后台列表，含还没发布的"""
    return _ordered(db.query(Project)).all()


@admin_router.post("/projects", response_model=ProjectResponse)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@admin_router.put("/projects/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # PUT 是全量替换，所以逐个字段覆盖。
    # ProjectUpdate 里的字段和表字段是一一对应的，不会 setattr 出多余的属性
    for field, value in payload.model_dump().items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


@admin_router.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    db.delete(project)
    db.commit()
    return {"message": "已删除"}
