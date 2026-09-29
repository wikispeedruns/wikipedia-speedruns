"""Exercise the production repair SQL against session-only MySQL tables."""
import json
import re
from pathlib import Path


def test_repair_marathon_22(cursor):
    # MySQL resolves these names to temporary tables for this connection only.
    # Copy the real columns, omitting foreign keys unsupported on temporary tables.
    def create_temporary(table):
        cursor.execute(f"SHOW CREATE TABLE {table}")
        ddl = cursor.fetchone()["Create Table"]
        ddl = "\n".join(line for line in ddl.splitlines()
                        if not line.lstrip().startswith("CONSTRAINT "))
        ddl = re.sub(r",\n\)", "\n)", ddl)
        cursor.execute(ddl.replace("CREATE TABLE", "CREATE TEMPORARY TABLE", 1))

    create_temporary("marathonprompts")
    try:
        create_temporary("marathonruns")
        try:
            _check_repair(cursor)
        finally:
            cursor.execute("DROP TEMPORARY TABLE marathonruns")
    finally:
        cursor.execute("DROP TEMPORARY TABLE marathonprompts")


def _check_repair(cursor):
    initial = ["University of Milan", "Duffer brothers"]
    reserve = ["Paragraph", "Prompt", "Graph theory"]
    for prompt_id in (20, 22, 23):
        cursor.execute(
            "INSERT INTO marathonprompts "
            "(prompt_id, start, initcheckpoints, checkpoints, seed) "
            "VALUES (%s, %s, %s, %s, %s)",
            (prompt_id, "Alexander the Great", json.dumps(initial),
             json.dumps(reserve), 0),
        )
    cursor.execute(
        "INSERT INTO marathonruns "
        "(run_id, path, checkpoints, prompt_id, finished, total_time) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (1, json.dumps(["Alexander the Great", "Duffer brothers"]),
         json.dumps(["Duffer brothers"]), 22, 1, 100),
    )

    def snapshot(table):
        cursor.execute(f"SELECT * FROM {table} ORDER BY 1")
        return cursor.fetchall()

    def repair():
        script = Path(__file__).resolve().parents[1] / "scripts/repair_marathon_22.sql"
        sql = "\n".join(line for line in script.read_text().splitlines()
                        if not line.lstrip().startswith("--"))
        for statement in sql.split(";"):
            if statement.strip():
                cursor.execute(statement)
                if cursor.description:
                    cursor.fetchall()

    before = snapshot("marathonprompts")
    runs_before = snapshot("marathonruns")
    repair()
    after = snapshot("marathonprompts")
    expected = [dict(row) for row in before]
    expected[1]["initcheckpoints"] = json.dumps(["University of Milan", "The Duffer Brothers"])
    expected[1]["checkpoints"] = json.dumps(["Paragraph", "Prompt engineering", "Graph theory"])
    assert after == expected, "Only the intended checkpoint fields should change"
    assert snapshot("marathonruns") == runs_before, "Historical runs must remain unchanged"

    repair()
    assert snapshot("marathonprompts") == after, "Rerunning must be a no-op"
    assert snapshot("marathonruns") == runs_before

    # Also cover the alternate spelling included in the repair script.
    cursor.execute("UPDATE marathonprompts SET checkpoints=%s WHERE prompt_id=22",
                   (json.dumps(["Prompt (disambiguation)"]),))
    repair()
    assert json.loads(snapshot("marathonprompts")[1]["checkpoints"]) == ["Prompt engineering"]

    # An unexpected prompt identity must not be overwritten.
    cursor.execute("UPDATE marathonprompts SET start=%s, checkpoints=%s WHERE prompt_id=22",
                   ("Different start", json.dumps(["Prompt"])))
    guarded = snapshot("marathonprompts")
    repair()
    assert snapshot("marathonprompts") == guarded
