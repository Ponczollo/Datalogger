import argparse
import csv
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, MetaData, Table, create_engine, inspect, select


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_SCHEMA = "datalogger"


def dump_tables(output_dir: Path | None = None) -> Path:
    if output_dir is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output_dir = PROJECT_ROOT / "database" / "exports" / timestamp

    output_dir.mkdir(parents=True, exist_ok=True)
    load_dotenv(PROJECT_ROOT / ".env")
    url = URL.create(
        "postgresql+psycopg2",
        username=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        database=os.getenv("POSTGRES_DB", "datalogger"),
    )
    engine = create_engine(url)
    try:
        with engine.connect() as connection:
            table_names = sorted(inspect(connection).get_table_names(schema=DB_SCHEMA))

            if not table_names:
                raise RuntimeError(f"No tables found in schema {DB_SCHEMA!r}")

            metadata = MetaData()
            for table_name in table_names:
                table = Table(
                    table_name,
                    metadata,
                    schema=DB_SCHEMA,
                    autoload_with=connection,
                )
                result = connection.execute(select(table))
                output_path = output_dir / f"{table_name}.csv"

                with output_path.open("w", newline="", encoding="utf-8") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(result.keys())
                    writer.writerows(result)

                print(f"Exported {DB_SCHEMA}.{table_name} to {output_path}")
    finally:
        engine.dispose()

    return output_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Export PostgreSQL tables to CSV")
    parser.add_argument(
        "--output",
        type=Path,
        help="Output directory (defaults to database/exports/<UTC timestamp>)",
    )
    args = parser.parse_args()
    output_dir = dump_tables(args.output)
    print(f"CSV export complete: {output_dir}")


if __name__ == "__main__":
    main()
