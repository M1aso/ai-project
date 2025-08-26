package main

import (
	"database/sql"
	"flag"
	"log"
	"os"

	"github.com/pressly/goose/v3"
	_ "github.com/lib/pq"
)

const dialect = "postgres"

func main() {
	var dir = flag.String("dir", "/internal/db/migrations", "directory with migration files")
	flag.Parse()

	dbURL := os.Getenv("DATABASE_URL")
	if dbURL == "" {
		log.Fatal("DATABASE_URL environment variable is required")
	}

	db, err := sql.Open("postgres", dbURL)
	if err != nil {
		log.Fatalf("failed to open database: %v", err)
	}
	defer db.Close()

	if err := db.Ping(); err != nil {
		log.Fatalf("failed to ping database: %v", err)
	}

	args := flag.Args()
	if len(args) < 1 {
		log.Fatal("Expected at least one argument: up, down, status, etc.")
	}

	command := args[0]
	
	if err := goose.SetDialect(dialect); err != nil {
		log.Fatalf("failed to set dialect: %v", err)
	}

	switch command {
	case "up":
		if err := goose.Up(db, *dir); err != nil {
			log.Fatalf("failed to run up migrations: %v", err)
		}
		log.Println("Content migrations completed successfully")
	case "down":
		if err := goose.Down(db, *dir); err != nil {
			log.Fatalf("failed to run down migration: %v", err)
		}
	case "status":
		if err := goose.Status(db, *dir); err != nil {
			log.Fatalf("failed to get migration status: %v", err)
		}
	case "version":
		version, err := goose.GetDBVersion(db)
		if err != nil {
			log.Fatalf("failed to get database version: %v", err)
		}
		log.Printf("Database version: %d", version)
	default:
		log.Fatalf("Unknown command: %s", command)
	}
}
