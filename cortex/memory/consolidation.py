"""
Memory consolidation for lifecycle management.
"""
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json
import os
import shutil


class MemoryConsolidator:
    """Manages memory consolidation and archival."""
    
    def __init__(self, db_path: str, archive_dir: str):
        """Initialize consolidator.
        
        Args:
            db_path: Path to main database
            archive_dir: Path to archive directory
        """
        self.db_path = db_path
        self.archive_dir = archive_dir
        os.makedirs(archive_dir, exist_ok=True)
        
    def consolidate(self, days_threshold: int = 7) -> Dict[str, Any]:
        """Run consolidation process.
        
        Args:
            days_threshold: Archive data older than this many days
            
        Returns:
            Consolidation report
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        report = {
            'started_at': datetime.now().isoformat(),
            'operations': [],
            'stats': {}
        }
        
        try:
            # 1. Summarize old sessions
            sessions_processed = self._summarize_sessions(cursor, days_threshold)
            report['operations'].append({
                'operation': 'summarize_sessions',
                'count': sessions_processed
            })
            
            # 2. Archive old episodic memories
            archived_episodic = self._archive_episodic(cursor, days_threshold)
            report['operations'].append({
                'operation': 'archive_episodic',
                'count': archived_episodic
            })
            
            # 3. Consolidate semantic duplicates
            consolidated_semantic = self._consolidate_semantic(cursor)
            report['operations'].append({
                'operation': 'consolidate_semantic',
                'count': consolidated_semantic
            })
            
            # 4. Update memory tiers
            tier_updates = self._update_tiers(cursor)
            report['operations'].append({
                'operation': 'update_tiers',
                'count': tier_updates
            })
            
            # 5. Vacuum database
            cursor.execute("VACUUM")
            
            conn.commit()
            
            # Log consolidation
            cursor.execute("""
                INSERT INTO consolidation_log 
                (operation, records_processed, status, completed_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, ('full_consolidation', sum(
                op['count'] for op in report['operations']
            ), 'success'))
            conn.commit()
            
            report['status'] = 'success'
            report['completed_at'] = datetime.now().isoformat()
            
        except Exception as e:
            report['status'] = 'error'
            report['error'] = str(e)
        finally:
            conn.close()
            
        return report
        
    def _summarize_sessions(self, cursor, days_threshold: int) -> int:
        """Summarize old sessions.
        
        Args:
            cursor: Database cursor
            days_threshold: Days threshold
            
        Returns:
            Number of sessions summarized
        """
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        
        # Find sessions without summaries
        cursor.execute("""
            SELECT id, start_time FROM sessions
            WHERE summary IS NULL
            AND start_time < ?
            AND end_time IS NOT NULL
        """, (cutoff_date.isoformat(),))
        
        sessions = cursor.fetchall()
        count = 0
        
        for session in sessions:
            # Get session events
            cursor.execute("""
                SELECT event_type, COUNT(*) as count
                FROM episodic_memory
                WHERE session_id = ?
                GROUP BY event_type
            """, (session['id'],))
            
            events = cursor.fetchall()
            
            # Create summary
            summary_parts = []
            for event in events:
                summary_parts.append(
                    f"{event['count']} {event['event_type']} events"
                )
            summary = '; '.join(summary_parts)
            
            # Update session
            cursor.execute("""
                UPDATE sessions
                SET summary = ?
                WHERE id = ?
            """, (summary, session['id']))
            
            count += 1
            
        return count
        
    def _archive_episodic(self, cursor, days_threshold: int) -> int:
        """Archive old episodic memories.
        
        Args:
            cursor: Database cursor
            days_threshold: Days threshold
            
        Returns:
            Number of records archived
        """
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        
        # Export to archive
        cursor.execute("""
            SELECT * FROM episodic_memory
            WHERE timestamp < ?
            AND tier = 'WARM'
        """, (cutoff_date.isoformat(),))
        
        records = cursor.fetchall()
        
        if records:
            archive_file = os.path.join(
                self.archive_dir,
                f'episodic_{datetime.now().strftime("%Y%m%d")}.json'
            )
            
            with open(archive_file, 'w') as f:
                json.dump([dict(r) for r in records], f, indent=2)
                
            # Update tier to COLD
            cursor.execute("""
                UPDATE episodic_memory
                SET tier = 'COLD'
                WHERE timestamp < ?
                AND tier = 'WARM'
            """, (cutoff_date.isoformat(),))
            
        return len(records)
        
    def _consolidate_semantic(self, cursor) -> int:
        """Consolidate duplicate semantic memories.
        
        Args:
            cursor: Database cursor
            
        Returns:
            Number of duplicates consolidated
        """
        # Find potential duplicates (same topic and similar fact)
        cursor.execute("""
            SELECT topic, fact, COUNT(*) as count, 
                   MAX(confidence) as max_confidence,
                   GROUP_CONCAT(id) as ids
            FROM semantic_memory
            GROUP BY topic, SUBSTR(fact, 1, 50)
            HAVING count > 1
        """)
        
        duplicates = cursor.fetchall()
        count = 0
        
        for dup in duplicates:
            ids = [int(i) for i in dup['ids'].split(',')]
            keep_id = ids[0]
            remove_ids = ids[1:]
            
            # Update the kept record with max confidence
            cursor.execute("""
                UPDATE semantic_memory
                SET confidence = ?,
                    access_count = access_count + ?
                WHERE id = ?
            """, (dup['max_confidence'], len(remove_ids), keep_id))
            
            # Remove duplicates
            cursor.execute("""
                DELETE FROM semantic_memory
                WHERE id IN ({})
            """.format(','.join('?' * len(remove_ids))), remove_ids)
            
            count += len(remove_ids)
            
        return count
        
    def _update_tiers(self, cursor) -> int:
        """Update memory tiers based on usage.
        
        Args:
            cursor: Database cursor
            
        Returns:
            Number of tier updates
        """
        count = 0
        
        # Promote frequently accessed semantic memories to HOT
        cursor.execute("""
            UPDATE semantic_memory
            SET tier = 'HOT'
            WHERE access_count > 10
            AND tier = 'WARM'
        """)
        count += cursor.rowcount
        
        # Demote rarely accessed to WARM
        cursor.execute("""
            UPDATE semantic_memory
            SET tier = 'WARM'
            WHERE access_count <= 10
            AND tier = 'HOT'
        """)
        count += cursor.rowcount
        
        # Update skills tier
        cursor.execute("""
            UPDATE skill_memory
            SET tier = 'HOT'
            WHERE last_used > datetime('now', '-7 days')
            AND tier = 'WARM'
        """)
        count += cursor.rowcount
        
        return count
        
    def get_consolidation_history(self) -> List[Dict]:
        """Get consolidation history.
        
        Returns:
            List of consolidation logs
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM consolidation_log
            ORDER BY started_at DESC
            LIMIT 10
        """)
        
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return logs
        
    def export_knowledge_base(self, output_file: str) -> Dict[str, Any]:
        """Export entire knowledge base.
        
        Args:
            output_file: Output file path
            
        Returns:
            Export report
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        export = {
            'exported_at': datetime.now().isoformat(),
            'semantic_memory': [],
            'skill_memory': [],
            'sessions': []
        }
        
        # Export semantic memory
        cursor.execute("SELECT * FROM semantic_memory WHERE confidence >= 0.5")
        export['semantic_memory'] = [dict(row) for row in cursor.fetchall()]
        
        # Export skills
        cursor.execute("SELECT * FROM skill_memory WHERE confidence >= 0.5")
        skills = cursor.fetchall()
        for skill in skills:
            skill_dict = dict(skill)
            if skill_dict['steps']:
                skill_dict['steps'] = json.loads(skill_dict['steps'])
            if skill_dict['prerequisites']:
                skill_dict['prerequisites'] = json.loads(skill_dict['prerequisites'])
            export['skill_memory'].append(skill_dict)
            
        # Export session summaries
        cursor.execute("""
            SELECT id, start_time, end_time, summary, context
            FROM sessions
            WHERE summary IS NOT NULL
            ORDER BY start_time DESC
            LIMIT 100
        """)
        export['sessions'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        # Write to file
        with open(output_file, 'w') as f:
            json.dump(export, f, indent=2)
            
        return {
            'status': 'success',
            'output_file': output_file,
            'semantic_count': len(export['semantic_memory']),
            'skill_count': len(export['skill_memory']),
            'session_count': len(export['sessions'])
        }
