# AI Agent Project

## Setup Instructions

1. **Environment Variables**

   - Copy the `.env.example` file to `.env` and update the values as needed for your environment.
   - Example:
     ```bash
     cp .env.example .env
     # Edit .env with your preferred settings
     ```

2. **Database Setup**
   - The project uses the `dvdrental` PostgreSQL sample database.
   - To restore the database, use the `pg_restore` command with the provided `dvdrental.tar` file in the `data/` directory.
   - Example command:
     ```bash
     pg_restore -U <your_pg_user> -d <your_database> data/dvdrental.tar
     ```
   - Replace `<your_pg_user>` and `<your_database>` with your PostgreSQL username and target database name.

## Requirements

- Python dependencies are listed in `requirements.txt`.
- PostgreSQL must be installed and running.

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up your `.env` file as described above.
3. Restore the database as described above.
4. Run the application as needed.
