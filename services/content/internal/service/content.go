package service

import (
	"database/sql"
	"fmt"
	"time"

	"github.com/example/content/internal/db"
	_ "github.com/lib/pq"
)

// ContentService handles business logic for content operations
type ContentService struct {
	db *sql.DB
}

// NewContentService creates a new ContentService instance
func NewContentService(databaseURL string) (*ContentService, error) {
	database, err := sql.Open("postgres", databaseURL)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to database: %w", err)
	}

	if err := database.Ping(); err != nil {
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	return &ContentService{db: database}, nil
}

// Close closes the database connection
func (s *ContentService) Close() error {
	return s.db.Close()
}

// CreateCourse creates a new course
func (s *ContentService) CreateCourse(title, description, category string) (*db.Course, error) {
	courseID := fmt.Sprintf("course-%s", title)
	now := time.Now()
	
	course := &db.Course{
		ID:          courseID,
		Title:       title,
		Description: description,
		Status:      "draft",
		CreatedAt:   now,
		UpdatedAt:   now,
	}

	query := `
		INSERT INTO courses (id, title, description, status, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6)
	`
	
	_, err := s.db.Exec(query, course.ID, course.Title, course.Description, 
		course.Status, course.CreatedAt, course.UpdatedAt)
	if err != nil {
		return nil, fmt.Errorf("failed to create course: %w", err)
	}

	return course, nil
}

// GetCourses retrieves all courses
func (s *ContentService) GetCourses() ([]db.Course, error) {
	query := `SELECT id, title, description, status, created_at, updated_at FROM courses ORDER BY created_at DESC`
	
	rows, err := s.db.Query(query)
	if err != nil {
		return nil, fmt.Errorf("failed to query courses: %w", err)
	}
	defer rows.Close()

	var courses []db.Course
	for rows.Next() {
		var course db.Course
		err := rows.Scan(&course.ID, &course.Title, &course.Description, 
			&course.Status, &course.CreatedAt, &course.UpdatedAt)
		if err != nil {
			return nil, fmt.Errorf("failed to scan course: %w", err)
		}
		courses = append(courses, course)
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("rows error: %w", err)
	}

	return courses, nil
}

// GetCourse retrieves a specific course by ID
func (s *ContentService) GetCourse(id string) (*db.Course, error) {
	query := `SELECT id, title, description, status, created_at, updated_at FROM courses WHERE id = $1`
	
	var course db.Course
	err := s.db.QueryRow(query, id).Scan(&course.ID, &course.Title, &course.Description,
		&course.Status, &course.CreatedAt, &course.UpdatedAt)
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("course not found")
		}
		return nil, fmt.Errorf("failed to get course: %w", err)
	}

	return &course, nil
}

// UpdateCourse updates an existing course
func (s *ContentService) UpdateCourse(id string, status string) (*db.Course, error) {
	query := `UPDATE courses SET status = $1, updated_at = $2 WHERE id = $3`
	
	now := time.Now()
	_, err := s.db.Exec(query, status, now, id)
	if err != nil {
		return nil, fmt.Errorf("failed to update course: %w", err)
	}

	return s.GetCourse(id)
}

// CreateMaterial creates a new material
func (s *ContentService) CreateMaterial(sectionID, materialType, title string) (*db.Material, error) {
	materialID := fmt.Sprintf("material-%s", title)
	now := time.Now()
	
	material := &db.Material{
		ID:        materialID,
		SectionID: sectionID,
		Type:      materialType,
		Title:     title,
		Status:    "draft",
		CreatedAt: now,
		UpdatedAt: now,
	}

	query := `
		INSERT INTO materials (id, section_id, type, title, status, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7)
	`
	
	_, err := s.db.Exec(query, material.ID, material.SectionID, material.Type,
		material.Title, material.Status, material.CreatedAt, material.UpdatedAt)
	if err != nil {
		return nil, fmt.Errorf("failed to create material: %w", err)
	}

	return material, nil
}

// GetMaterials retrieves all materials
func (s *ContentService) GetMaterials() ([]db.Material, error) {
	query := `SELECT id, section_id, type, title, status, created_at, updated_at FROM materials ORDER BY created_at DESC`
	
	rows, err := s.db.Query(query)
	if err != nil {
		return nil, fmt.Errorf("failed to query materials: %w", err)
	}
	defer rows.Close()

	var materials []db.Material
	for rows.Next() {
		var material db.Material
		err := rows.Scan(&material.ID, &material.SectionID, &material.Type,
			&material.Title, &material.Status, &material.CreatedAt, &material.UpdatedAt)
		if err != nil {
			return nil, fmt.Errorf("failed to scan material: %w", err)
		}
		materials = append(materials, material)
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("rows error: %w", err)
	}

	return materials, nil
}

// GetMaterial retrieves a specific material by ID
func (s *ContentService) GetMaterial(id string) (*db.Material, error) {
	query := `SELECT id, section_id, type, title, status, created_at, updated_at FROM materials WHERE id = $1`
	
	var material db.Material
	err := s.db.QueryRow(query, id).Scan(&material.ID, &material.SectionID, &material.Type,
		&material.Title, &material.Status, &material.CreatedAt, &material.UpdatedAt)
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("material not found")
		}
		return nil, fmt.Errorf("failed to get material: %w", err)
	}

	return &material, nil
}

// UpdateMaterial updates an existing material
func (s *ContentService) UpdateMaterial(id string, status string) (*db.Material, error) {
	query := `UPDATE materials SET status = $1, updated_at = $2 WHERE id = $3`
	
	now := time.Now()
	_, err := s.db.Exec(query, status, now, id)
	if err != nil {
		return nil, fmt.Errorf("failed to update material: %w", err)
	}

	return s.GetMaterial(id)
}
