from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class Repository(Base):
    __tablename__ = 'repositories'
    
    id = Column(Integer, primary_key=True)
    github_id = Column(Integer, unique=True)
    name = Column(String(255))
    full_name = Column(String(255), unique=True)
    private = Column(Boolean, default=False)
    
    # Relationships
    pull_requests = relationship("PullRequest", back_populates="repository")
    
    def __repr__(self):
        return f"<Repository(id={self.id}, name='{self.name}')>"


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    github_id = Column(Integer, unique=True)
    login = Column(String(255))
    type = Column(String(50))
    
    # Relationships
    created_prs = relationship("PullRequest", foreign_keys="PullRequest.user_id", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, login='{self.login}')>"


class PullRequest(Base):
    __tablename__ = 'pull_requests'
    
    id = Column(Integer, primary_key=True)
    github_id = Column(Integer, unique=True)
    number = Column(Integer)
    title = Column(String(255))
    body = Column(Text, nullable=True)
    state = Column(String(50))  # open, closed, merged
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    merged = Column(Boolean, default=False)
    merged_at = Column(DateTime, nullable=True)
    
    # Foreign keys
    repository_id = Column(Integer, ForeignKey('repositories.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # Extra data storage
    head_ref = Column(String(255))  # Source branch
    base_ref = Column(String(255))  # Target branch
    head_sha = Column(String(255))
    base_sha = Column(String(255))
    
    # Relationships
    repository = relationship("Repository", back_populates="pull_requests")
    user = relationship("User", foreign_keys=[user_id], back_populates="created_prs")
    events = relationship("PREvent", back_populates="pull_request")
    
    def __repr__(self):
        return f"<PullRequest(id={self.id}, number={self.number}, title='{self.title}')>"


class PREvent(Base):
    __tablename__ = 'pr_events'
    
    id = Column(Integer, primary_key=True)
    event_type = Column(String(50))  # opened, closed, reopened, edited, labeled, etc.
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    payload = Column(JSON, nullable=True)  # Additional event data
    
    # Foreign keys
    pull_request_id = Column(Integer, ForeignKey('pull_requests.id'))
    
    # Relationships
    pull_request = relationship("PullRequest", back_populates="events")
    
    def __repr__(self):
        return f"<PREvent(id={self.id}, type='{self.event_type}', pr_id={self.pull_request_id})>"


class BranchEvent(Base):
    __tablename__ = 'branch_events'
    
    id = Column(Integer, primary_key=True)
    event_type = Column(String(50))  # created, deleted, etc.
    ref = Column(String(255))  # Branch name with refs/heads/ prefix
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Foreign keys
    repository_id = Column(Integer, ForeignKey('repositories.id'))
    
    # JSON fields for additional data
    payload = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<BranchEvent(id={self.id}, type='{self.event_type}', ref='{self.ref}')>"


class PushEvent(Base):
    __tablename__ = 'push_events'
    
    id = Column(Integer, primary_key=True)
    ref = Column(String(255))  # Branch name with refs/heads/ prefix
    before = Column(String(255))  # SHA before push
    after = Column(String(255))  # SHA after push
    created = Column(Boolean, default=False)
    deleted = Column(Boolean, default=False)
    forced = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Foreign keys
    repository_id = Column(Integer, ForeignKey('repositories.id'))
    sender_id = Column(Integer, ForeignKey('users.id'))
    
    # JSON fields for additional data
    commits = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<PushEvent(id={self.id}, ref='{self.ref}', repo_id={self.repository_id})>"