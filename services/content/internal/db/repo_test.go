package db

import (
	"context"
	"database/sql"
	"os"
	"strings"
	"testing"

	_ "github.com/lib/pq"
)

func setup(t *testing.T) *Repo {
	t.Helper()
	db, err := sql.Open("postgres", "postgresql://postgres:postgres@localhost:5432/test_aiproject?sslmode=disable")
	if err != nil {
		t.Fatal(err)
	}
	sqlBytes, err := os.ReadFile("migrations/001_init.sql")
	if err != nil {
		t.Fatal(err)
	}
	up := strings.Split(string(sqlBytes), "-- +goose Down")[0]
	if _, err := db.Exec(up); err != nil {
		t.Fatal(err)
	}
	return New(db)
}

func TestCreateAndGetCourse(t *testing.T) {
	repo := setup(t)
	ctx := context.Background()
	c := Course{ID: "c1", Title: "Test", Status: "draft"}
	if err := repo.CreateCourse(ctx, c); err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := repo.GetCourse(ctx, "c1")
	if err != nil {
		t.Fatalf("get: %v", err)
	}
	if got.Title != c.Title {
		t.Fatalf("want %s got %s", c.Title, got.Title)
	}
}
