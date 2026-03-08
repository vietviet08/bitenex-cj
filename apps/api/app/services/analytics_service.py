"""Analytics service for timeline, funnel, and segment queries."""

from datetime import date
from typing import Any

from app.db.clickhouse import execute_query
from app.schemas.analytics import (
    FunnelResponse,
    SegmentPreviewRequest,
    SegmentPreviewResponse,
    TimelineEvent,
    TimelineResponse,
)


class AnalyticsService:
    """Service for analytics queries against ClickHouse."""

    async def get_user_timeline(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> TimelineResponse:
        """Get user's event timeline."""
        query = """
            SELECT event_name, timestamp, properties
            FROM events
            WHERE user_id = {user_id:String}
            ORDER BY timestamp DESC
            LIMIT {limit:UInt32}
            OFFSET {offset:UInt32}
        """
        results = await execute_query(
            query,
            parameters={"user_id": user_id, "limit": limit, "offset": offset},
        )

        events = []
        for row in results:
            import json

            props = row.get("properties", "{}")
            if isinstance(props, str):
                props = json.loads(props)
            events.append(
                TimelineEvent(
                    event_name=row["event_name"],
                    timestamp=row["timestamp"],
                    properties=props,
                )
            )

        return TimelineResponse(user_id=user_id, events=events)

    async def get_funnel(
        self,
        from_date: date,
        to_date: date,
        steps: list[str],
    ) -> FunnelResponse:
        """
        Calculate funnel conversion for given steps.
        Uses window functions to track user progression through steps.
        """
        # Build funnel query using ClickHouse's windowFunnel function
        steps_array = ", ".join([f"'{step}'" for step in steps])
        query = f"""
            SELECT
                step,
                count(DISTINCT user_id) as cnt
            FROM (
                SELECT
                    user_id,
                    windowFunnel(86400)(timestamp, {', '.join([f"event_name = '{step}'" for step in steps])}) as step
                FROM events
                WHERE timestamp >= {{from_date:Date}}
                  AND timestamp <= {{to_date:Date}}
                  AND event_name IN ({steps_array})
                GROUP BY user_id
            )
            GROUP BY step
            ORDER BY step
        """

        results = await execute_query(
            query,
            parameters={"from_date": str(from_date), "to_date": str(to_date)},
        )

        # Convert results to counts array
        counts = [0] * len(steps)
        for row in results:
            step_idx = row["step"]
            if 0 < step_idx <= len(steps):
                # Accumulate counts for each step reached
                for i in range(step_idx):
                    counts[i] += row["cnt"]

        return FunnelResponse(
            from_date=from_date,
            to_date=to_date,
            steps=steps,
            counts=counts,
        )

    async def preview_segment(
        self,
        request: SegmentPreviewRequest,
    ) -> SegmentPreviewResponse:
        """
        Preview segment by estimating matching users.
        """
        definition = request.definition

        # Build query based on segment definition
        include_event = definition.include.get("event", "")
        within_minutes = definition.include.get("within_minutes", 120)

        query = """
            SELECT count(DISTINCT user_id) as cnt
            FROM events
            WHERE event_name = {include_event:String}
              AND timestamp >= now() - INTERVAL {within_minutes:UInt32} MINUTE
        """
        params: dict[str, Any] = {
            "include_event": include_event,
            "within_minutes": within_minutes,
        }

        # Add exclude condition if present
        if definition.exclude:
            exclude_event = definition.exclude.get("event", "")
            exclude_minutes = definition.exclude.get("within_minutes", within_minutes)
            query = f"""
                SELECT count(DISTINCT user_id) as cnt
                FROM events
                WHERE event_name = {{include_event:String}}
                  AND timestamp >= now() - INTERVAL {{within_minutes:UInt32}} MINUTE
                  AND user_id NOT IN (
                      SELECT DISTINCT user_id
                      FROM events
                      WHERE event_name = {{exclude_event:String}}
                        AND timestamp >= now() - INTERVAL {{exclude_minutes:UInt32}} MINUTE
                  )
            """
            params["exclude_event"] = exclude_event
            params["exclude_minutes"] = exclude_minutes

        results = await execute_query(query, parameters=params)
        estimated_users = results[0]["cnt"] if results else 0

        segment_id = f"seg_{request.name}"
        return SegmentPreviewResponse(
            segment_id=segment_id,
            estimated_users=estimated_users,
        )
