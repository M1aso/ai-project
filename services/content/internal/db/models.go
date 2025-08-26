package db

import "time"

// Course represents a course row.
type Course struct {
	ID          string    `db:"id"`
	Title       string    `db:"title"`
	Description string    `db:"description"`
	Status      string    `db:"status"`
	CreatedAt   time.Time `db:"created_at"`
	UpdatedAt   time.Time `db:"updated_at"`
}

// Section represents a section row.
type Section struct {
	ID        string    `db:"id"`
	CourseID  string    `db:"course_id"`
	Title     string    `db:"title"`
	Sequence  int       `db:"sequence"`
	CreatedAt time.Time `db:"created_at"`
	UpdatedAt time.Time `db:"updated_at"`
}

// Material represents a learning material.
type Material struct {
	ID        string    `db:"id"`
	SectionID string    `db:"section_id"`
	Type      string    `db:"type"`
	Title     string    `db:"title"`
	Status    string    `db:"status"`
	CreatedAt time.Time `db:"created_at"`
	UpdatedAt time.Time `db:"updated_at"`
}

// MediaAsset represents an uploaded file linked to material.
type MediaAsset struct {
	ID         string    `db:"id"`
	MaterialID string    `db:"material_id"`
	URL        string    `db:"url"`
	Status     string    `db:"status"`
	CreatedAt  time.Time `db:"created_at"`
	UpdatedAt  time.Time `db:"updated_at"`
}

// Tag represents a course tag.
type Tag struct {
	ID        string    `db:"id"`
	Name      string    `db:"name"`
	CreatedAt time.Time `db:"created_at"`
	UpdatedAt time.Time `db:"updated_at"`
}
