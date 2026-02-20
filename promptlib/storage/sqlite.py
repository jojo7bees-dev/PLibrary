import json
from datetime import datetime
from typing import List, Optional, Any
from uuid import UUID
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, JSON as SQLiteJSON, ForeignKey, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from promptlib.models.prompt import Prompt
from promptlib.models.version import PromptVersion
from promptlib.storage.base import BaseRepository

Base = declarative_base()

class SQLPrompt(Base):
    __tablename__ = 'prompts'
    id = Column(String(36), primary_key=True)
    name = Column(String(255), unique=True, index=True)
    description = Column(Text)
    content = Column(Text)
    variables = Column(SQLiteJSON)
    tags = Column(SQLiteJSON)
    category = Column(String(255), index=True)
    version = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime)
    author = Column(String(255))
    variable_definitions_json = Column(SQLiteJSON)
    metadata_json = Column(SQLiteJSON)
    checksum = Column(String(255))
    content_hash = Column(String(255))
    embedding_vector_json = Column(SQLiteJSON)
    hash_signature = Column(String(255))

class SQLPromptVersion(Base):
    __tablename__ = 'prompt_versions'
    id = Column(String(36), primary_key=True)
    prompt_id = Column(String(36), ForeignKey('prompts.id'), index=True)
    version = Column(String(50))
    content = Column(Text)
    checksum = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)
    author = Column(String(255))
    change_log = Column(Text)

class SQLAgent(Base):
    __tablename__ = 'agents'
    id = Column(String(36), primary_key=True)
    name = Column(String(255))
    role = Column(String(50))
    capabilities_json = Column(SQLiteJSON)
    assigned_prompts_json = Column(SQLiteJSON)
    execution_history_json = Column(SQLiteJSON)
    metadata_json = Column(SQLiteJSON)

class SQLWorkflow(Base):
    __tablename__ = 'workflows'
    id = Column(String(36), primary_key=True)
    name = Column(String(255))
    description = Column(Text)
    start_step_id = Column(String(255))
    steps_json = Column(SQLiteJSON)
    metadata_json = Column(SQLiteJSON)

class SQLiteRepository(BaseRepository):
    def __init__(self, database_url: str = "sqlite:///promptlib.db"):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self._init_fts()
        self.Session = sessionmaker(bind=self.engine)

    def _init_fts(self):
        with self.engine.connect() as conn:
            conn.execute(text("CREATE VIRTUAL TABLE IF NOT EXISTS prompt_fts USING fts5(prompt_id UNINDEXED, name, description, content);"))
            conn.commit()

    def _to_domain(self, sql_prompt: SQLPrompt) -> Prompt:
        from promptlib.models.variable import VariableDefinition
        return Prompt(
            id=UUID(sql_prompt.id),
            name=sql_prompt.name,
            description=sql_prompt.description,
            content=sql_prompt.content,
            variables=sql_prompt.variables or [],
            variable_definitions=[VariableDefinition(**d) for d in (sql_prompt.variable_definitions_json or [])],
            tags=sql_prompt.tags or [],
            category=sql_prompt.category,
            version=sql_prompt.version,
            created_at=sql_prompt.created_at,
            updated_at=sql_prompt.updated_at,
            usage_count=sql_prompt.usage_count,
            last_used=sql_prompt.last_used,
            author=sql_prompt.author,
            metadata=sql_prompt.metadata_json or {},
            checksum=sql_prompt.checksum,
            content_hash=sql_prompt.content_hash,
            embedding_vector=sql_prompt.embedding_vector_json,
            hash_signature=sql_prompt.hash_signature
        )

    def _to_sql(self, prompt: Prompt) -> SQLPrompt:
        return SQLPrompt(
            id=str(prompt.id),
            name=prompt.name,
            description=prompt.description,
            content=prompt.content,
            variables=prompt.variables,
            variable_definitions_json=[d.model_dump() for d in prompt.variable_definitions],
            tags=prompt.tags,
            category=prompt.category,
            version=prompt.version,
            created_at=prompt.created_at,
            updated_at=prompt.updated_at,
            usage_count=prompt.usage_count,
            last_used=prompt.last_used,
            author=prompt.author,
            metadata_json=prompt.metadata,
            checksum=prompt.checksum,
            content_hash=prompt.content_hash,
            embedding_vector_json=prompt.embedding_vector,
            hash_signature=prompt.hash_signature
        )

    def save(self, prompt: Prompt) -> None:
        with self.Session() as session:
            sql_prompt = self._to_sql(prompt)
            session.merge(sql_prompt)
            session.commit()

            # Update FTS
            with self.engine.connect() as conn:
                conn.execute(text("DELETE FROM prompt_fts WHERE prompt_id = :id"), {"id": str(prompt.id)})
                conn.execute(text("INSERT INTO prompt_fts (prompt_id, name, description, content) VALUES (:id, :name, :description, :content)"),
                             {"id": str(prompt.id), "name": prompt.name, "description": prompt.description, "content": prompt.content})
                conn.commit()

    def get_by_id(self, prompt_id: UUID) -> Optional[Prompt]:
        with self.Session() as session:
            sql_prompt = session.query(SQLPrompt).filter(SQLPrompt.id == str(prompt_id)).first()
            return self._to_domain(sql_prompt) if sql_prompt else None

    def get_by_name(self, name: str) -> Optional[Prompt]:
        with self.Session() as session:
            sql_prompt = session.query(SQLPrompt).filter(SQLPrompt.name == name).first()
            return self._to_domain(sql_prompt) if sql_prompt else None

    def delete(self, prompt_id: UUID) -> None:
        with self.Session() as session:
            session.query(SQLPrompt).filter(SQLPrompt.id == str(prompt_id)).delete()
            session.commit()

            with self.engine.connect() as conn:
                conn.execute(text("DELETE FROM prompt_fts WHERE prompt_id = :id"), {"id": str(prompt_id)})
                conn.commit()

    def list_all(self, category: Optional[str] = None, tags: Optional[List[str]] = None) -> List[Prompt]:
        with self.Session() as session:
            query = session.query(SQLPrompt)
            if category:
                query = query.filter(SQLPrompt.category == category)
            # Tag filtering is a bit harder with JSON column in SQLite, but we can do it in Python for now
            # or use JSON_EACH if available. For simplicity, Python filtering first.
            results = query.all()
            prompts = [self._to_domain(r) for r in results]
            if tags:
                prompts = [p for p in prompts if all(t in p.tags for t in tags)]
            return prompts

    def search(self, query: str) -> List[Prompt]:
        with self.Session() as session:
            # Using FTS5 for search
            with self.engine.connect() as conn:
                res = conn.execute(text("SELECT prompt_id FROM prompt_fts WHERE prompt_fts MATCH :query"), {"query": query})
                ids = [r[0] for r in res]

            if not ids:
                # Fallback to simple LIKE if FTS returns nothing (or for very short queries)
                results = session.query(SQLPrompt).filter(
                    (SQLPrompt.name.contains(query)) | (SQLPrompt.content.contains(query))
                ).order_by(SQLPrompt.usage_count.desc()).all()
                return [self._to_domain(r) for r in results]

            results = session.query(SQLPrompt).filter(SQLPrompt.id.in_(ids)).order_by(SQLPrompt.usage_count.desc()).all()
            return [self._to_domain(r) for r in results]

    def save_version(self, version: PromptVersion) -> None:
        with self.Session() as session:
            sql_version = SQLPromptVersion(
                id=str(version.id),
                prompt_id=str(version.prompt_id),
                version=version.version,
                content=version.content,
                checksum=version.checksum,
                created_at=version.created_at,
                author=version.author,
                change_log=version.change_log
            )
            session.add(sql_version)
            session.commit()

    def get_versions(self, prompt_id: UUID) -> List[PromptVersion]:
        with self.Session() as session:
            results = session.query(SQLPromptVersion).filter(SQLPromptVersion.prompt_id == str(prompt_id)).all()
            return [
                PromptVersion(
                    id=UUID(r.id),
                    prompt_id=UUID(r.prompt_id),
                    version=r.version,
                    content=r.content,
                    checksum=r.checksum,
                    created_at=r.created_at,
                    author=r.author,
                    change_log=r.change_log
                ) for r in results
            ]

    def update_usage(self, prompt_id: UUID) -> None:
        with self.Session() as session:
            sql_prompt = session.query(SQLPrompt).filter(SQLPrompt.id == str(prompt_id)).first()
            if sql_prompt:
                sql_prompt.usage_count += 1
                sql_prompt.last_used = datetime.now()
                session.commit()

    def save_agent(self, agent: Any) -> None:
        with self.Session() as session:
            sql_agent = SQLAgent(
                id=str(agent.id),
                name=agent.name,
                role=agent.role,
                capabilities_json=[c.model_dump() for c in agent.capabilities],
                assigned_prompts_json=[str(p) for p in agent.assigned_prompts],
                execution_history_json=agent.execution_history,
                metadata_json=agent.metadata
            )
            session.merge(sql_agent)
            session.commit()

    def get_agent(self, agent_id: UUID) -> Optional[Any]:
        from promptlib.models.agent import Agent, AgentCapability
        with self.Session() as session:
            sql_agent = session.query(SQLAgent).filter(SQLAgent.id == str(agent_id)).first()
            if not sql_agent:
                return None
            return Agent(
                id=UUID(sql_agent.id),
                name=sql_agent.name,
                role=sql_agent.role,
                capabilities=[AgentCapability(**c) for c in (sql_agent.capabilities_json or [])],
                assigned_prompts=[UUID(p) for p in (sql_agent.assigned_prompts_json or [])],
                execution_history=sql_agent.execution_history_json or [],
                metadata=sql_agent.metadata_json or {}
            )

    def save_workflow(self, workflow: Any) -> None:
        with self.Session() as session:
            sql_wf = SQLWorkflow(
                id=str(workflow.id),
                name=workflow.name,
                description=workflow.description,
                start_step_id=workflow.start_step_id,
                steps_json={k: v.model_dump(mode='json') for k, v in workflow.steps.items()},
                metadata_json=workflow.metadata
            )
            session.merge(sql_wf)
            session.commit()

    def get_workflow(self, workflow_id: UUID) -> Optional[Any]:
        from promptlib.models.workflow import Workflow, WorkflowStep
        with self.Session() as session:
            sql_wf = session.query(SQLWorkflow).filter(SQLWorkflow.id == str(workflow_id)).first()
            if not sql_wf:
                return None
            return Workflow(
                id=UUID(sql_wf.id),
                name=sql_wf.name,
                description=sql_wf.description,
                start_step_id=sql_wf.start_step_id,
                steps={k: WorkflowStep(**v) for k, v in (sql_wf.steps_json or {}).items()},
                metadata=sql_wf.metadata_json or {}
            )
