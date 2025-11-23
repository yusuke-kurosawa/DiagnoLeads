#!/usr/bin/env python3
"""
Database Seeding CLI

Usage:
    python seed_database.py [--env ENV] [--clean]

Options:
    --env ENV       Environment (development, test, production) [default: development]
    --clean         Clean existing data before seeding
    --help          Show this help message

Examples:
    # Seed development data
    python seed_database.py

    # Seed test data
    python seed_database.py --env test

    # Clean and re-seed
    python seed_database.py --clean
"""

import argparse
import importlib
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.seed import DatabaseSeeder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger(__name__)


def load_seed_data(environment: str):
    """Load seed data for the specified environment"""
    try:
        module = importlib.import_module(f"seeds.{environment}")
        return module.SEED_DATA
    except ImportError as e:
        logger.error(f"❌ Could not load seed data for environment '{environment}': {e}")
        logger.error(f"   Make sure 'seeds/{environment}.py' exists")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Seed database with initial data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--env",
        default="development",
        choices=["development", "test", "production"],
        help="Environment to seed (default: development)",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean existing data before seeding",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompt in clean mode",
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("🌱 DiagnoLeads Database Seeding")
    logger.info("=" * 60)
    logger.info(f"Environment: {args.env}")
    logger.info(f"Clean mode: {'Yes' if args.clean else 'No'}")
    logger.info(f"Database: {settings.DATABASE_URL.split('@')[-1]}")  # Hide credentials
    logger.info("=" * 60)
    logger.info("")

    # Confirm if clean mode
    if args.clean and not args.force:
        logger.warning("⚠️  WARNING: Clean mode will delete ALL existing data!")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != "yes":
            logger.info("Seeding cancelled.")
            sys.exit(0)
        logger.info("")
    elif args.clean and args.force:
        logger.warning("⚠️  WARNING: Clean mode - forcing deletion of ALL existing data!")
        logger.info("")

    # Load seed data
    logger.info(f"📂 Loading seed data for '{args.env}' environment...")
    seed_data = load_seed_data(args.env)
    logger.info("")

    # Connect to database
    logger.info("🔌 Connecting to database...")
    engine = create_engine(settings.DATABASE_URL)
    db = Session(engine)

    try:
        # Run seeding
        seeder = DatabaseSeeder(db)
        seeder.seed_all(seed_data, clean=args.clean)

        logger.info("")
        logger.info("=" * 60)
        logger.info("✅ Database seeding completed successfully!")
        logger.info("=" * 60)

        # Print summary
        if "users" in seed_data and seed_data["users"]:
            logger.info("")
            logger.info("📋 Seeded Users:")
            for user in seed_data["users"]:
                logger.info(f"  • {user['name']} ({user['role']})")
                logger.info(f"    Email: {user['email']}")
                logger.info(f"    Password: {user['password']}")

    except Exception as e:
        logger.error(f"❌ Seeding failed: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
