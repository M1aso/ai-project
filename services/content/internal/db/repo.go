package db

import (
	"context"
	"database/sql"
)

// Repo provides database access helpers.
type Repo struct {
	DB *sql.DB
}

func New(db *sql.DB) *Repo {
	return &Repo{DB: db}
}

// CreateCourse inserts a course record.
func (r *Repo) CreateCourse(ctx context.Context, c Course) error {
	_, err := r.DB.ExecContext(ctx,
		`INSERT INTO courses(id, title, description, status) VALUES(?,?,?,?)`,
		c.ID, c.Title, c.Description, c.Status,
	)
	return err
}

// GetCourse retrieves a course by id.
func (r *Repo) GetCourse(ctx context.Context, id string) (Course, error) {
	var c Course
	err := r.DB.QueryRowContext(ctx,
		`SELECT id, title, description, status, created_at, updated_at FROM courses WHERE id = ?`,
		id,
	).Scan(&c.ID, &c.Title, &c.Description, &c.Status, &c.CreatedAt, &c.UpdatedAt)
	return c, err
}

// GetMaterial retrieves a material by id.
func (r *Repo) GetMaterial(ctx context.Context, id string) (Material, error) {
	var m Material
	err := r.DB.QueryRowContext(ctx,
		`SELECT id, section_id, type, title, status, created_at, updated_at FROM materials WHERE id = ?`,
		id,
	).Scan(&m.ID, &m.SectionID, &m.Type, &m.Title, &m.Status, &m.CreatedAt, &m.UpdatedAt)
	return m, err
}
