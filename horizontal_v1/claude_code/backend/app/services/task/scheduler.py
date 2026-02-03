"""
Task scheduler service using APScheduler.

Provides:
- Database-driven task persistence
- Dynamic service invocation
- Cron and interval scheduling
- Task execution logging

Reference:
- cool-admin-midway/src/modules/task/service/info.ts
- cool-admin-midway/src/modules/task/queue/task.ts
"""

import asyncio
import importlib
import json
import logging
import re
from datetime import datetime
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.task import TaskInfo, TaskLog

logger = logging.getLogger("work_assistant.task.scheduler")


class TaskScheduler:
    """
    Async task scheduler using APScheduler.

    Features:
    - Database-driven task configuration
    - Cron and interval triggers
    - Dynamic service method invocation
    - Execution logging
    - Graceful startup/shutdown
    """

    _instance: "TaskScheduler | None" = None
    _scheduler: AsyncIOScheduler | None = None
    _initialized: bool = False

    def __new__(cls) -> "TaskScheduler":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize scheduler (singleton)."""
        if self._scheduler is not None:
            return

        self._scheduler = AsyncIOScheduler(
            timezone="Asia/Shanghai",
            job_defaults={
                "coalesce": True,
                "max_instances": 1,
                "misfire_grace_time": 60,
            },
        )

    async def start(self) -> None:
        """
        Start the scheduler and load tasks from database.

        Should be called during application startup.
        """
        if self._initialized:
            return

        logger.info("Starting task scheduler...")
        self._scheduler.start()
        self._initialized = True

        # Wait a bit for database to be ready
        await asyncio.sleep(3)

        # Load active tasks
        await self._init_tasks()
        logger.info("Task scheduler started")

    async def shutdown(self) -> None:
        """
        Shutdown the scheduler gracefully.

        Should be called during application shutdown.
        """
        if not self._initialized:
            return

        logger.info("Shutting down task scheduler...")
        self._scheduler.shutdown(wait=False)
        self._initialized = False
        logger.info("Task scheduler stopped")

    async def _init_tasks(self) -> None:
        """Load and schedule all active tasks from database."""
        try:
            async with async_session_factory() as session:
                result = await session.execute(
                    select(TaskInfo).where(TaskInfo.status == 1)
                )
                tasks = result.scalars().all()

                for task in tasks:
                    if not self._job_exists(task.id):
                        logger.info(f"Initializing task: {task.name}")
                        await self._add_job(task)

        except Exception as e:
            logger.error(f"Failed to initialize tasks: {e}")

    def _job_exists(self, task_id: int) -> bool:
        """Check if a job already exists."""
        job_id = f"task_{task_id}"
        return self._scheduler.get_job(job_id) is not None

    async def _add_job(self, task: TaskInfo) -> bool:
        """
        Add a job to the scheduler.

        Args:
            task: TaskInfo model instance

        Returns:
            True if job was added successfully
        """
        job_id = f"task_{task.id}"

        # Build trigger
        if task.taskType == 0 and task.cron:
            # Cron trigger
            try:
                trigger = CronTrigger.from_crontab(task.cron)
            except Exception as e:
                logger.error(f"Invalid cron expression for task {task.id}: {e}")
                return False
        elif task.taskType == 1 and task.every:
            # Interval trigger (every is in milliseconds)
            trigger = IntervalTrigger(seconds=task.every / 1000)
        else:
            logger.warning(f"Task {task.id} has invalid trigger configuration")
            return False

        # Add job
        try:
            self._scheduler.add_job(
                self._execute_task,
                trigger=trigger,
                id=job_id,
                args=[task.id],
                name=task.name,
                replace_existing=True,
                start_date=task.startDate,
                end_date=task.endDate,
            )

            # Update next run time
            job = self._scheduler.get_job(job_id)
            if job and job.next_run_time:
                async with async_session_factory() as session:
                    await session.execute(
                        update(TaskInfo)
                        .where(TaskInfo.id == task.id)
                        .values(
                            nextRunTime=job.next_run_time,
                            jobId=job_id,
                        )
                    )
                    await session.commit()

            logger.info(f"Added job for task {task.id}: {task.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to add job for task {task.id}: {e}")
            return False

    async def _remove_job(self, task_id: int) -> bool:
        """Remove a job from the scheduler."""
        job_id = f"task_{task_id}"
        try:
            self._scheduler.remove_job(job_id)
            logger.info(f"Removed job for task {task_id}")
            return True
        except Exception:
            return False

    async def _execute_task(self, task_id: int) -> None:
        """
        Execute a scheduled task.

        Args:
            task_id: Task ID to execute
        """
        logger.info(f"Executing task {task_id}")

        async with async_session_factory() as session:
            result = await session.execute(
                select(TaskInfo).where(TaskInfo.id == task_id)
            )
            task = result.scalar_one_or_none()

            if not task:
                logger.warning(f"Task {task_id} not found, removing job")
                await self._remove_job(task_id)
                return

            try:
                # Execute service method
                result_data = await self.invoke_service(task.service)

                # Log success
                await self._record_log(
                    session,
                    task_id=task_id,
                    status=1,
                    detail=json.dumps(result_data, ensure_ascii=False) if result_data else None,
                )

            except Exception as e:
                logger.error(f"Task {task_id} execution failed: {e}")
                # Log failure
                await self._record_log(
                    session,
                    task_id=task_id,
                    status=0,
                    detail=str(e),
                )

            # Update next run time
            job = self._scheduler.get_job(f"task_{task_id}")
            if job and job.next_run_time:
                await session.execute(
                    update(TaskInfo)
                    .where(TaskInfo.id == task_id)
                    .values(nextRunTime=job.next_run_time)
                )
            await session.commit()

    async def _record_log(
        self,
        session: AsyncSession,
        task_id: int,
        status: int,
        detail: str | None = None,
    ) -> None:
        """Record task execution log."""
        log = TaskLog(
            taskId=task_id,
            status=status,
            detail=detail,
        )
        session.add(log)
        await session.flush()

    async def invoke_service(self, service_str: str | None) -> Any:
        """
        Dynamically invoke a service method.

        Service string format: "ServiceName.method(arg1, arg2)"
        Example: "SupplyService.analyze(123, 'test')"

        Args:
            service_str: Service method string

        Returns:
            Result from service method call
        """
        if not service_str:
            return None

        # Parse service string: ServiceName.method(args)
        match = re.match(r"(\w+)\.(\w+)\((.*)\)", service_str)
        if not match:
            raise ValueError(f"Invalid service string format: {service_str}")

        service_name, method_name, args_str = match.groups()

        # Parse arguments
        args = []
        if args_str.strip():
            # Split by comma, but respect quoted strings
            arg_parts = re.split(r",(?=(?:[^'\"]*['\"][^'\"]*['\"])*[^'\"]*$)", args_str)
            for arg in arg_parts:
                arg = arg.strip()
                if arg:
                    try:
                        # Try to parse as JSON
                        args.append(json.loads(arg))
                    except json.JSONDecodeError:
                        # If not valid JSON, strip quotes if present
                        if (arg.startswith("'") and arg.endswith("'")) or \
                           (arg.startswith('"') and arg.endswith('"')):
                            args.append(arg[1:-1])
                        else:
                            args.append(arg)

        # Import and get service
        # Services are in app.services.{module}.{service_name}
        # Try common locations
        service_module = None
        service_class = None

        # Map service names to module paths
        service_map = {
            "SupplyService": "app.services.rk.supply",
            "DemandService": "app.services.rk.demand",
            "CaseService": "app.services.rk.case",
            "CustomerService": "app.services.rk.customer",
            "VendorService": "app.services.rk.vendor",
            "NoticeService": "app.services.rk.notice",
            "DictService": "app.services.dict.info",
        }

        module_path = service_map.get(service_name)
        if module_path:
            try:
                module = importlib.import_module(module_path)
                # Get the service instance (usually exported as {name}_service)
                instance_name = service_name[0].lower() + service_name[1:].replace("Service", "_service")
                service_instance = getattr(module, instance_name, None)
                if service_instance and hasattr(service_instance, method_name):
                    method = getattr(service_instance, method_name)
                    if asyncio.iscoroutinefunction(method):
                        return await method(*args)
                    else:
                        return method(*args)
            except Exception as e:
                logger.error(f"Failed to invoke {service_str}: {e}")
                raise

        raise ValueError(f"Service not found: {service_name}")

    # ==================== Public API ====================

    async def add_task(self, task_data: dict[str, Any]) -> TaskInfo:
        """
        Add or update a task.

        Args:
            task_data: Task configuration dict

        Returns:
            Created/updated TaskInfo
        """
        async with async_session_factory() as session:
            task_id = task_data.get("id")

            if task_id:
                # Update existing task
                result = await session.execute(
                    select(TaskInfo).where(TaskInfo.id == task_id)
                )
                task = result.scalar_one_or_none()
                if task:
                    for key, value in task_data.items():
                        if hasattr(task, key):
                            setattr(task, key, value)
                else:
                    task = TaskInfo(**task_data)
                    session.add(task)
            else:
                # Create new task
                task = TaskInfo(**task_data)
                session.add(task)

            await session.flush()

            # Handle scheduling
            if task.status == 1:
                await self._remove_job(task.id)
                await self._add_job(task)
            else:
                await self._remove_job(task.id)

            await session.commit()
            await session.refresh(task)
            return task

    async def start_task(self, task_id: int) -> bool:
        """Start a task."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(TaskInfo).where(TaskInfo.id == task_id)
            )
            task = result.scalar_one_or_none()
            if not task:
                return False

            task.status = 1
            await session.commit()

            await self._remove_job(task_id)
            return await self._add_job(task)

    async def stop_task(self, task_id: int) -> bool:
        """Stop a task."""
        async with async_session_factory() as session:
            await session.execute(
                update(TaskInfo)
                .where(TaskInfo.id == task_id)
                .values(status=0, nextRunTime=None)
            )
            await session.commit()

        return await self._remove_job(task_id)

    async def run_once(self, task_id: int) -> None:
        """Run a task once immediately."""
        await self._execute_task(task_id)

    async def delete_task(self, task_id: int) -> bool:
        """Delete a task and its logs."""
        await self._remove_job(task_id)

        async with async_session_factory() as session:
            await session.execute(delete(TaskLog).where(TaskLog.taskId == task_id))
            await session.execute(delete(TaskInfo).where(TaskInfo.id == task_id))
            await session.commit()

        return True

    async def get_task(self, task_id: int) -> TaskInfo | None:
        """Get a task by ID."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(TaskInfo).where(TaskInfo.id == task_id)
            )
            return result.scalar_one_or_none()

    async def list_tasks(
        self,
        page: int = 1,
        size: int = 20,
        status: int | None = None,
    ) -> dict[str, Any]:
        """List tasks with pagination."""
        async with async_session_factory() as session:
            query = select(TaskInfo)
            if status is not None:
                query = query.where(TaskInfo.status == status)

            # Count total
            from sqlalchemy import func
            count_query = select(func.count()).select_from(TaskInfo)
            if status is not None:
                count_query = count_query.where(TaskInfo.status == status)
            total_result = await session.execute(count_query)
            total = total_result.scalar() or 0

            # Get page
            query = query.order_by(TaskInfo.id.desc())
            query = query.offset((page - 1) * size).limit(size)
            result = await session.execute(query)
            tasks = result.scalars().all()

            return {
                "list": [self._task_to_dict(t) for t in tasks],
                "pagination": {
                    "page": page,
                    "size": size,
                    "total": total,
                },
            }

    async def get_task_logs(
        self,
        task_id: int | None = None,
        status: int | None = None,
        page: int = 1,
        size: int = 20,
    ) -> dict[str, Any]:
        """Get task execution logs with pagination."""
        async with async_session_factory() as session:
            query = select(TaskLog)
            if task_id is not None:
                query = query.where(TaskLog.taskId == task_id)
            if status is not None:
                query = query.where(TaskLog.status == status)

            # Count total
            from sqlalchemy import func
            count_query = select(func.count()).select_from(TaskLog)
            if task_id is not None:
                count_query = count_query.where(TaskLog.taskId == task_id)
            if status is not None:
                count_query = count_query.where(TaskLog.status == status)
            total_result = await session.execute(count_query)
            total = total_result.scalar() or 0

            # Get page
            query = query.order_by(TaskLog.id.desc())
            query = query.offset((page - 1) * size).limit(size)
            result = await session.execute(query)
            logs = result.scalars().all()

            return {
                "list": [self._log_to_dict(log) for log in logs],
                "pagination": {
                    "page": page,
                    "size": size,
                    "total": total,
                },
            }

    @staticmethod
    def _task_to_dict(task: TaskInfo) -> dict[str, Any]:
        """Convert TaskInfo to dict."""
        return {
            "id": task.id,
            "name": task.name,
            "cron": task.cron,
            "every": task.every,
            "limit": task.limit,
            "status": task.status,
            "taskType": task.taskType,
            "type": task.type,
            "service": task.service,
            "data": task.data,
            "remark": task.remark,
            "startDate": task.startDate.isoformat() if task.startDate else None,
            "endDate": task.endDate.isoformat() if task.endDate else None,
            "nextRunTime": task.nextRunTime.isoformat() if task.nextRunTime else None,
            "jobId": task.jobId,
            "createTime": task.createTime.isoformat() if task.createTime else None,
            "updateTime": task.updateTime.isoformat() if task.updateTime else None,
        }

    @staticmethod
    def _log_to_dict(log: TaskLog) -> dict[str, Any]:
        """Convert TaskLog to dict."""
        return {
            "id": log.id,
            "taskId": log.taskId,
            "status": log.status,
            "detail": log.detail,
            "createTime": log.createTime.isoformat() if log.createTime else None,
        }


# Global singleton instance
task_scheduler = TaskScheduler()
